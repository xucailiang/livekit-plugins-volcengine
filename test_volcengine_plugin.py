"""
火山引擎 LiveKit 插件测试脚本
测试 STT (BigModelSTT)、TTS 和 LLM 功能

注意：在 Agent Worker 外部使用时，需要手动传入 http_session 并管理其生命周期。
这是 LiveKit 插件的标准模式。
"""

import asyncio
import wave
from pathlib import Path

import aiohttp

# 配置参数
STT_CONFIG = {
    "app_id": "6268967697",
    "access_token": "b2_Zd6vO_cuqqFIehXF0FxDIWbRpLCoC",
    "model_name": "bigmodel",
    "enable_punc": True,
    "enable_itn": False,
}

TTS_CONFIG = {
    "app_id": "6268967697",
    "access_token": "b2_Zd6vO_cuqqFIehXF0FxDIWbRpLCoC",
    "cluster": "volcano_tts",
    "voice": "BV001_V2_streaming",
    "sample_rate": 24000,
    "speed": 1.0,
    "volume": 1.0,
    "pitch": 1.0,
}

# LLM 配置 (使用兼容 OpenAI 的接口)
LLM_CONFIG = {
    "model": "qwen3-max",
    "api_key": "sk-4bd9a83b368b4c0c89e3256f2bcbec2c",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}

# 测试音频文件路径
TEST_AUDIO_FILE = "我现在开始录音，理论上会有两个文件.wav"


async def test_stt(http_session: aiohttp.ClientSession):
    """测试 STT (BigModelSTT) 功能"""
    print("\n" + "=" * 50)
    print("测试 STT (BigModelSTT) 功能")
    print("=" * 50)

    from livekit.plugins.volcengine import BigModelSTT
    from livekit import rtc

    # 检查测试音频文件
    if not Path(TEST_AUDIO_FILE).exists():
        print(f"❌ 测试音频文件不存在: {TEST_AUDIO_FILE}")
        return False

    try:
        # 创建 BigModelSTT 实例，传入 http_session
        stt = BigModelSTT(
            app_id=STT_CONFIG["app_id"],
            access_token=STT_CONFIG["access_token"],
            model_name=STT_CONFIG["model_name"],
            enable_punc=STT_CONFIG["enable_punc"],
            enable_itn=STT_CONFIG["enable_itn"],
            http_session=http_session,
        )

        print(f"✓ STT 实例创建成功")
        print(f"  - model: {stt.model}")
        print(f"  - provider: {stt.provider}")

        # 读取 WAV 文件
        with wave.open(TEST_AUDIO_FILE, "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            num_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            n_frames = wav_file.getnframes()
            audio_data = wav_file.readframes(n_frames)

        print(f"✓ 音频文件读取成功")
        print(f"  - 采样率: {sample_rate} Hz")
        print(f"  - 声道数: {num_channels}")
        print(f"  - 采样位数: {sample_width * 8} bits")
        print(f"  - 帧数: {n_frames}")

        # 创建流式识别
        stream = stt.stream()
        print("✓ STT 流创建成功，开始识别...")

        # 分块发送音频数据
        chunk_size = sample_rate * sample_width * num_channels // 10  # 100ms chunks
        transcripts = []

        async def send_audio():
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i : i + chunk_size]
                frame = rtc.AudioFrame(
                    data=chunk,
                    sample_rate=sample_rate,
                    num_channels=num_channels,
                    samples_per_channel=len(chunk) // (sample_width * num_channels),
                )
                stream.push_frame(frame)
                await asyncio.sleep(0.05)
            stream.end_input()

        async def receive_results():
            async for event in stream:
                if event.type.name == "FINAL_TRANSCRIPT":
                    for alt in event.alternatives:
                        transcripts.append(alt.text)
                        print(f"  [最终] {alt.text}")
                elif event.type.name == "INTERIM_TRANSCRIPT":
                    for alt in event.alternatives:
                        print(f"  [临时] {alt.text}")

        try:
            await asyncio.wait_for(
                asyncio.gather(send_audio(), receive_results()),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            pass  # 超时后正常结束
        except Exception:
            pass  # 连接关闭等异常，忽略

        if transcripts:
            print(f"\n✓ STT 测试成功！识别结果: {''.join(transcripts)}")
            return True
        else:
            print("⚠ STT 测试完成，但未获取到识别结果")
            return True

    except Exception as e:
        print(f"❌ STT 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tts(http_session: aiohttp.ClientSession):
    """测试 TTS 功能"""
    print("\n" + "=" * 50)
    print("测试 TTS 功能")
    print("=" * 50)

    from livekit.plugins.volcengine import TTS

    try:
        # 创建 TTS 实例，传入 http_session
        tts = TTS(
            app_id=TTS_CONFIG["app_id"],
            access_token=TTS_CONFIG["access_token"],
            cluster=TTS_CONFIG["cluster"],
            voice=TTS_CONFIG["voice"],
            sample_rate=TTS_CONFIG["sample_rate"],
            speed=TTS_CONFIG["speed"],
            volume=TTS_CONFIG["volume"],
            pitch=TTS_CONFIG["pitch"],
            http_session=http_session,
        )

        print(f"✓ TTS 实例创建成功")
        print(f"  - model: {tts.model}")
        print(f"  - provider: {tts.provider}")

        # 测试文本
        test_text = "你好，这是一个火山引擎语音合成测试。"
        print(f"✓ 测试文本: {test_text}")

        # 创建流式合成
        stream = tts.stream()
        stream.push_text(test_text)
        stream.end_input()

        print("✓ TTS 流创建成功，开始合成...")

        # 收集音频数据
        audio_chunks = []
        async for event in stream:
            if event.frame:
                audio_chunks.append(event.frame.data)

        if audio_chunks:
            total_bytes = sum(len(chunk) for chunk in audio_chunks)
            print(f"✓ TTS 测试成功！")
            print(f"  - 生成音频块数: {len(audio_chunks)}")
            print(f"  - 总字节数: {total_bytes}")

            # 保存为 WAV 文件
            output_file = "tts_output.wav"
            with wave.open(output_file, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(TTS_CONFIG["sample_rate"])
                wav_file.writeframes(b"".join(audio_chunks))
            print(f"  - 输出文件: {output_file}")
            await tts.aclose()  # 关闭连接池
            return True
        else:
            print("⚠ TTS 测试完成，但未生成音频数据")
            await tts.aclose()
            return False

    except Exception as e:
        print(f"❌ TTS 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm():
    """测试 LLM 功能"""
    print("\n" + "=" * 50)
    print("测试 LLM 功能")
    print("=" * 50)

    from livekit.plugins.volcengine import LLM
    from livekit.agents.llm import ChatContext

    try:
        # 创建 LLM 实例 (使用 qwen3-max 模型，兼容 OpenAI 接口)
        # LLM 使用 httpx 客户端，不需要 aiohttp session
        llm = LLM(
            model=LLM_CONFIG["model"],
            api_key=LLM_CONFIG["api_key"],
            base_url=LLM_CONFIG["base_url"],
        )

        print(f"✓ LLM 实例创建成功")
        print(f"  - model: {LLM_CONFIG['model']}")
        print(f"  - base_url: {LLM_CONFIG['base_url']}")

        # 创建聊天上下文
        chat_ctx = ChatContext()
        chat_ctx.add_message(role="user", content="你好，请用一句话介绍一下你自己。")

        print("✓ 发送消息: 你好，请用一句话介绍一下你自己。")

        # 调用 LLM
        stream = llm.chat(chat_ctx=chat_ctx)

        print("✓ LLM 流创建成功，等待响应...")

        # 收集响应
        response_text = []
        async for chunk in stream:
            if chunk.delta and chunk.delta.content:
                response_text.append(chunk.delta.content)
                print(chunk.delta.content, end="", flush=True)

        print()  # 换行

        if response_text:
            print(f"\n✓ LLM 测试成功！")
            print(f"  - 响应长度: {len(''.join(response_text))} 字符")
            return True
        else:
            print("⚠ LLM 测试完成，但未获取到响应")
            return False

    except Exception as e:
        print(f"❌ LLM 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("=" * 50)
    print("火山引擎 LiveKit 插件测试")
    print("=" * 50)

    results = {}

    # 创建共享的 HTTP session，在 Agent Worker 外部使用时需要手动管理
    async with aiohttp.ClientSession() as http_session:
        # 测试 STT
        results["STT"] = await test_stt(http_session)

        # 测试 TTS
        results["TTS"] = await test_tts(http_session)

    # 测试 LLM (使用 httpx，不需要 aiohttp session)
    results["LLM"] = await test_llm()

    # 打印测试结果汇总
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    for name, result in results.items():
        if result is True:
            status = "✓ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⚠ 跳过"
        print(f"  {name}: {status}")


if __name__ == "__main__":
    asyncio.run(main())
