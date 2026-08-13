from __future__ import annotations

import asyncio
import gzip
import json
import os
import time
import uuid
import weakref
from typing import Literal

import aiohttp
from osc_data.text_stream import TextStreamSentencizer

from livekit.agents import (
    APIConnectOptions,
    APIConnectionError,
    APITimeoutError,
    tts,
    utils,
)
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS

from .log import logger

PROTOCOL_VERSION = 0b0001
DEFAULT_HEADER_SIZE = 0b0001

CLIENT_FULL_REQUEST = 0b0001
SERVER_FULL_RESPONSE = 0b1001
SERVER_ERROR_RESPONSE = 0b1111

MSG_WITH_EVENT = 0b0100
JSON_SERIAL = 0b0001
GZIP_COMPRESS = 0b0001

EVENT_START_CONNECTION = 1
EVENT_FINISH_CONNECTION = 2
EVENT_START_SESSION = 100
EVENT_FINISH_SESSION = 102
EVENT_TASK_REQUEST = 200

EVENT_CONNECTION_STARTED = 50
EVENT_SESSION_STARTED = 150
EVENT_SESSION_FINISHED = 152
EVENT_SESSION_FAILED = 153
EVENT_TTS_RESPONSE = 352

# 方言需走 explicit_dialect，不能填进 explicit_language
_DIALECTS = {"beijing", "dongbei", "henan", "shaanxi", "shanghai", "sichuan", "tianjin", "yue"}


def _build_frame(event: int, payload: dict | None = None, session_id: str = "") -> bytearray:
    payload_bytes = gzip.compress(b"{}") if payload is None else gzip.compress(
        str.encode(json.dumps(payload, ensure_ascii=False))
    )
    header = bytearray([
        (PROTOCOL_VERSION << 4) | DEFAULT_HEADER_SIZE,
        (CLIENT_FULL_REQUEST << 4) | MSG_WITH_EVENT,
        (JSON_SERIAL << 4) | GZIP_COMPRESS,
        0,
    ])
    frame = bytearray(header)
    frame.extend(event.to_bytes(4, "big"))
    if session_id:
        sid = str.encode(session_id)
        frame.extend(len(sid).to_bytes(4, "big"))
        frame.extend(sid)
    frame.extend(len(payload_bytes).to_bytes(4, "big"))
    frame.extend(payload_bytes)
    return frame


def _parse_response(res: bytes) -> dict | None:
    header_size = res[0] & 0x0F
    message_type = res[1] >> 4
    message_type_specific_flags = res[1] & 0x0F
    message_compression = res[2] & 0x0F
    payload = res[header_size * 4 :]

    if message_type == SERVER_ERROR_RESPONSE:
        code = int.from_bytes(payload[:4], "big", signed=False)
        payload_size = int.from_bytes(payload[4:8], "big", signed=False)
        error_msg = payload[8:8 + payload_size]
        if message_compression == GZIP_COMPRESS:
            error_msg = gzip.decompress(error_msg)
        logger.error("tts server error", extra={"code": code, "error": str(error_msg, "utf-8")})
        return {"event": 0, "payload": {"error": str(error_msg, "utf-8")}}

    result = {"event": 0, "payload": b""}
    start = 0
    if message_type_specific_flags & MSG_WITH_EVENT:
        result["event"] = int.from_bytes(payload[:4], "big", signed=False)
        start = 4

    payload = payload[start:]
    # 连接级事件没有 session_id，session 级事件有
    sid_size = int.from_bytes(payload[:4], "big", signed=True)
    if sid_size > 0:
        result["session_id"] = str(payload[4:4 + sid_size], "utf-8")
        payload = payload[4 + sid_size:]
    else:
        payload = payload[4:]

    if len(payload) < 4:
        return result

    payload_size = int.from_bytes(payload[:4], "big", signed=False)
    payload_msg = payload[4:4 + payload_size]

    if result["event"] != EVENT_TTS_RESPONSE and payload_msg:
        if message_compression == GZIP_COMPRESS:
            payload_msg = gzip.decompress(payload_msg)
        payload_msg = json.loads(payload_msg)
    result["payload"] = payload_msg
    return result


class TTS(tts.TTS):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        resource_id: str = "seed-tts-2.0",
        speaker: str = "zh_female_vv_uranus_bigtts",
        language: str | None = None,
        speech_rate: int = 0,
        loudness_rate: int = 0,
        sample_rate: int = 24000,
        output_format: Literal["pcm", "mp3", "ogg_opus"] = "pcm",
        disable_markdown_filter: bool = False,
        disable_emoji_filter: bool = False,
        http_session: aiohttp.ClientSession | None = None,
    ):
        """火山引擎豆包语音合成 v3 (双向流式 WebSocket)

        endpoint: wss://openspeech.bytedance.com/api/v3/tts/bidirection

        Args:
            api_key: API Key，未提供时从 VOLCENGINE_TTS_API_KEY / VOLCENGINE_API_KEY 读取。
            resource_id: seed-tts-2.0 / seed-tts-1.0 / seed-icl-2.0 等。
            speaker: 音色 ID。2.0 以 _uranus_bigtts 结尾。
            language: 合成语种/方言。如 "yue"(粤语), "zh-cn"(中文), "en"(英语), "ja"(日语), "sichuan"(四川话) 等。
            speech_rate: 语速 [-50, 100]，0 为正常，100=2倍速。
            loudness_rate: 音量 [-50, 100]，0 为正常。
            sample_rate: 采样率 (8000-48000)。
            output_format: pcm / mp3 / ogg_opus，流式推荐 pcm。
        """
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=True, aligned_transcript=False),
            sample_rate=sample_rate,
            num_channels=1,
        )

        api_key = api_key or os.environ.get("VOLCENGINE_TTS_API_KEY") or os.environ.get("VOLCENGINE_API_KEY")
        if api_key is None:
            raise ValueError(
                "api_key is required. Pass api_key parameter or set VOLCENGINE_TTS_API_KEY / VOLCENGINE_API_KEY."
            )

        self._api_key = api_key
        self._resource_id = resource_id
        self._speaker = speaker
        self._language = language
        self._speech_rate = speech_rate
        self._loudness_rate = loudness_rate
        self._output_format = output_format
        self._disable_markdown_filter = disable_markdown_filter
        self._disable_emoji_filter = disable_emoji_filter
        self._sample_rate = sample_rate

        self._session = http_session
        self._streams: weakref.WeakSet[SynthesizeStream] = weakref.WeakSet()

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = utils.http_context.http_session()
        return self._session

    @property
    def model(self) -> str:
        return self._speaker

    @property
    def provider(self) -> str:
        return "volcengine"

    def prewarm(self) -> None:
        self._ensure_session()

    async def aclose(self) -> None:
        for stream in list(self._streams):
            await stream.aclose()
        self._streams.clear()

    def synthesize(self, text, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS):
        raise NotImplementedError("Volcengine TTS only supports streaming synthesis. Use stream().")

    def stream(self, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS):
        stream = SynthesizeStream(
            tts=self,
            conn_options=conn_options,
            session=self._ensure_session(),
        )
        self._streams.add(stream)
        return stream


class SynthesizeStream(tts.SynthesizeStream):
    def __init__(
        self,
        *,
        tts: TTS,
        session: aiohttp.ClientSession,
        conn_options=None,
    ):
        super().__init__(tts=tts, conn_options=conn_options)
        self._tts = tts
        self._session = session

    async def _run(self, emitter: tts.AudioEmitter):
        request_id = utils.shortuuid()

        sentence_splitter = TextStreamSentencizer()
        emitter.initialize(
            request_id=request_id,
            sample_rate=self._tts._sample_rate,
            num_channels=1,
            mime_type="audio/pcm",
            frame_size_ms=200,
            stream=True,
        )

        logger.debug("tts synthesis started", extra={
            "request_id": request_id,
            "speaker": self._tts._speaker,
            "sample_rate": self._tts._sample_rate,
        })

        ws = await asyncio.wait_for(
            self._session.ws_connect(
                "wss://openspeech.bytedance.com/api/v3/tts/bidirection",
                headers={
                    "X-Api-Key": self._tts._api_key,
                    "X-Api-Resource-Id": self._tts._resource_id,
                    "X-Api-Connect-Id": str(uuid.uuid4()),
                },
            ),
            self._conn_options.timeout,
        )

        session_id = str(uuid.uuid4())
        try:
            await ws.send_bytes(_build_frame(EVENT_START_CONNECTION))
            resp = _parse_response(await ws.receive_bytes())
            if resp is None or resp.get("event") != EVENT_CONNECTION_STARTED:
                raise APIConnectionError("failed to start TTS connection")

            additions = {}
            if self._tts._language:
                if self._tts._language in _DIALECTS:
                    additions["explicit_dialect"] = self._tts._language
                else:
                    additions["explicit_language"] = self._tts._language
            if self._tts._disable_markdown_filter:
                additions["disable_markdown_filter"] = True
            if self._tts._disable_emoji_filter:
                additions["disable_emoji_filter"] = True

            # 官方协议：所有合成参数必须包在 req_params 里，否则 speaker 不生效，
            # 服务端会报 "resource ID is mismatched with speaker related resource"
            req_params = {
                "speaker": self._tts._speaker,
                "audio_params": {
                    "format": self._tts._output_format,
                    "sample_rate": self._tts._sample_rate,
                    "speech_rate": self._tts._speech_rate,
                    "loudness_rate": self._tts._loudness_rate,
                },
            }
            if additions:
                req_params["additions"] = json.dumps(additions, ensure_ascii=False)
            start_req = {"req_params": req_params}

            await ws.send_bytes(_build_frame(EVENT_START_SESSION, start_req, session_id))
            resp = _parse_response(await ws.receive_bytes())
            if resp is None or resp.get("event") != EVENT_SESSION_STARTED:
                raise APIConnectionError(f"failed to start TTS session: {resp}")

            # 官方协议：逐句发送 TaskRequest，全部发完后再发 FinishSession，
            # 服务端才会回 TTSSentenceEnd / SessionFinished；边发边读避免音频积压
            async def _send_text():
                start = time.perf_counter()
                first = True
                async for token in self._input_ch:
                    if isinstance(token, self._FlushSentinel):
                        sentences = sentence_splitter.flush()
                    else:
                        sentences = sentence_splitter.push(text=token)
                    for sentence in sentences:
                        if not sentence.strip():
                            continue
                        if first:
                            first = False
                            logger.info("llm first sentence", extra={"spent": round(time.perf_counter() - start, 4)})
                        await ws.send_bytes(_build_frame(
                            EVENT_TASK_REQUEST, {"req_params": {"text": sentence}}, session_id
                        ))
                await ws.send_bytes(_build_frame(EVENT_FINISH_SESSION, session_id=session_id))

            send_task = asyncio.create_task(_send_text())

            emitter.start_segment(segment_id=utils.shortuuid())
            tts_start = time.perf_counter()
            first_audio = True
            while True:
                resp = _parse_response(await ws.receive_bytes())
                if resp is None:
                    continue
                payload = resp.get("payload", b"")
                if isinstance(payload, dict) and "error" in payload:
                    raise APIConnectionError(f"TTS server error: {payload['error']}")
                event = resp.get("event", 0)
                if event == EVENT_TTS_RESPONSE:
                    data = payload
                    if isinstance(data, bytes) and data:
                        if first_audio:
                            first_audio = False
                            logger.info("tts first response", extra={"spent": round(time.perf_counter() - tts_start, 4)})
                        emitter.push(data=data)
                elif event == EVENT_SESSION_FINISHED:
                    break
                elif event == EVENT_SESSION_FAILED:
                    raise APIConnectionError(f"TTS session failed: {payload}")

            emitter.end_segment()
            await send_task
            logger.info("tts end", extra={"request_id": request_id})

            await ws.send_bytes(_build_frame(EVENT_FINISH_CONNECTION))
            await ws.receive_bytes()

        except asyncio.TimeoutError:
            logger.error("tts timeout", extra={"request_id": request_id})
            raise APITimeoutError(retryable=True)
        except aiohttp.ClientError as e:
            logger.error("tts connection error", extra={"request_id": request_id, "error": type(e).__name__}, exc_info=True)
            raise APIConnectionError(retryable=True) from e
        except APIConnectionError:
            raise
        except Exception as e:
            logger.error("tts unexpected error", extra={"request_id": request_id, "error": type(e).__name__}, exc_info=True)
            raise APIConnectionError(retryable=False) from e
        finally:
            await ws.close()
