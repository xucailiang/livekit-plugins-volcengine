# livekit-plugins-volcengine

[LiveKit Agents](https://github.com/livekit/agents) 的火山引擎插件，提供 STT、TTS、LLM 和实时语音模型集成。

## 安装

```bash
pip install livekit-plugins-volcengine
```

> Agent 集成示例使用 `silero` VAD，需另行安装 `pip install livekit-plugins-silero`。

## 用法

### LiveKit Agent 集成

```python
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import volcengine, silero

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=volcengine.BigModelSTT(language="zh-CN"),
        llm=volcengine.LLM(model="doubao-1-5-lite-32k-250115"),
        tts=volcengine.TTS(),
    )
    await session.start(
        agent=Agent(instructions="你是一个乐于助人的语音助手。"),
        room=ctx.room,
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

Worker 模式下通过环境变量配置密钥，无需在代码中硬编码:

```bash
export VOLCENGINE_STT_API_KEY="your_api_key"
export VOLCENGINE_TTS_API_KEY="your_api_key"
export VOLCENGINE_LLM_API_KEY="your_api_key"
```

### 单独使用

```python
from livekit.plugins.volcengine import BigModelSTT, TTS, LLM

# STT — bigmodel_async 双向流式
stt = BigModelSTT(api_key="...", language="zh-CN")

# TTS — v3 双向流式, language="yue" 合成粤语
tts = TTS(api_key="...", speaker="zh_female_vv_uranus_bigtts", language="yue")

# LLM — 豆包 或任意 OpenAI 兼容接口
llm = LLM(model="doubao-1-5-lite-32k-250115", api_key="...")
llm = LLM(model="qwen3-vl-plus", api_key="...", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
```

## API 参考

### BigModelSTT

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | str \| None | env `VOLCENGINE_STT_API_KEY` | API Key |
| `resource_id` | str | `volc.bigasr.sauc.duration` | 2.0: `volc.seedasr.sauc.*`, 1.0: `volc.bigasr.sauc.*` |
| `base_url` | str | `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async` | 端点 |
| `model_name` | str | `bigmodel` | 模型名称 |
| `language` | str | `zh-CN` | 识别语种，支持 `yue-CN`/`en-US`/`ja-JP` 等 |
| `enable_nonstream` | bool | `False` | 二遍识别（实时+非流式），提升准确率 |
| `enable_itn` | bool | `False` | 文本规范化（口语→书面） |
| `enable_punc` | bool | `True` | 标点 |
| `enable_ddc` | bool | `False` | 语义顺滑（去冗余/犹豫词） |
| `show_utterances` | bool | `True` | 分句/分词/时间戳 |
| `result_type` | str | `single` | `single`=增量, `full`=全量 |
| `vad_segment_duration` | int | `3000` | 语义分段最大静音(ms) |
| `end_window_size` | int | `800` | VAD 判停静音阈值(ms)，范围 [300,5000] |
| `force_to_speech_time` | int | `1000` | 判停前最小音频时长(ms) |
| `interim_results` | bool | `True` | 是否发送中间结果 |
| `http_session` | aiohttp.ClientSession \| None | `None` | 连接复用 |

### TTS

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | str \| None | env `VOLCENGINE_TTS_API_KEY` | API Key |
| `resource_id` | str | `seed-tts-2.0` | `seed-tts-2.0` / `seed-tts-1.0` / `seed-icl-2.0` |
| `speaker` | str | `zh_female_vv_uranus_bigtts` | 音色 ID，2.0 以 `_uranus_bigtts` 结尾 |
| `language` | str \| None | `None` | 语种/方言，如 `yue`(粤语)/`zh-cn`/`en`/`ja`/`sichuan` |
| `speech_rate` | int | `0` | 语速 [-50, 100]，100=2倍速 |
| `loudness_rate` | int | `0` | 音量 [-50, 100] |
| `sample_rate` | int | `24000` | 采样率 (8000/16000/24000) |
| `output_format` | str | `pcm` | `pcm` / `mp3` / `ogg_opus` |
| `disable_markdown_filter` | bool | `False` | 过滤 Markdown |
| `disable_emoji_filter` | bool | `False` | 过滤 emoji |
| `http_session` | aiohttp.ClientSession \| None | `None` | 连接复用 |

### LLM

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | str | `doubao-1-5-lite-32k-250115` | 模型名称 |
| `api_key` | str | env `VOLCENGINE_LLM_API_KEY` | API Key |
| `base_url` | str | 豆包 API | OpenAI 兼容地址 |
| `client` | openai.AsyncClient \| None | `None` | 自定义客户端 |
| `temperature` | float | - | 温度参数 |
| `tool_choice` | str | - | 工具选择策略 |

### RealtimeModel

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | str \| None | env `VOLCENGINE_REALTIME_API_KEY` | API Key |
| `bot_name` | str | `豆包` | Bot 名称 |
| `speaker` | str | `zh_female_vv_jupiter_bigtts` | TTS 音色 |
| `system_role` | str \| None | `None` | 系统角色/人设 |
| `model` | str | `O` | `O` / `SC` |
| `speaking_style` | str | - | 说话风格 |
| `opening` | str \| None | `None` | 开场白 |
| `enable_volc_websearch` | bool | `False` | 联网搜索 |
| `end_smooth_window_ms` | int | `500` | 停音平滑窗口(ms) |
| `modalities` | list | `["text","audio"]` | 交互模态 |
| `http_session` | aiohttp.ClientSession \| None | `None` | 连接复用 |

## 音色选择

TTS 2.0 (`seed-tts-2.0`) 常用音色，完整列表见 `音色列表.txt` 或 [官方文档](https://www.volcengine.com/docs/6561/97465):

| Speaker | 名称 | 语种/方言 |
|---------|------|-----------|
| `zh_female_vv_uranus_bigtts` | Vivi 2.0 | 中文/日文/印尼/西语 + 粤语/上海/四川等 |
| `zh_female_cancan_uranus_bigtts` | 灿灿 2.0 | 中文 |
| `zh_female_shuangkuaisisi_uranus_bigtts` | 爽快思思 2.0 | 中文 |
| `zh_female_tianmeixiaoyuan_uranus_bigtts` | 甜美小源 2.0 | 中文 |
| `zh_male_m191_uranus_bigtts` | 云舟 2.0 | 中文 + 粤语/上海/四川等 |
| `en_female_dacey_uranus_bigtts` | Dacey | 美式英语 |
| `en_male_tim_uranus_bigtts` | Tim | 美式英语 |

## 依赖

- `livekit-agents ~= 1.4.4`
- `numpy`
- `openai >= 1.75.0`
- `osc-data == 0.2.2`
- `pydantic`

## 许可证

Apache 2.0
