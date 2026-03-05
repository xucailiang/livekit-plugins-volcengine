# livekit-plugins-volcengine

[![PyPI version](https://badge.fury.io/py/livekit-plugins-volcengine.svg)](https://pypi.org/project/livekit-plugins-volcengine/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

[LiveKit Agents](https://github.com/livekit/agents) 火山引擎插件，提供 STT、TTS、LLM 和实时语音模型集成。

## 功能

| 组件 | 类名 | 说明 |
|------|------|------|
| 语音识别 | `STT` | 火山引擎流式语音识别 |
| 大模型语音识别 | `BigModelSTT` | 火山引擎大模型 ASR，支持更高精度 |
| 语音合成 | `TTS` | 火山引擎流式语音合成 |
| 大语言模型 | `LLM` | 豆包大模型，兼容 OpenAI 接口 |
| 实时语音 | `RealtimeModel` | 端到端实时语音交互 |

## 安装

```bash
pip install livekit-plugins-volcengine
```

开发安装：

```bash
git clone https://github.com/AIOps-Lab-NKU/livekit-plugins-volcengine.git
cd livekit-plugins-volcengine
pip install -e .
```

## 快速开始

### STT (语音识别)

```python
from livekit.plugins.volcengine import STT, BigModelSTT

# 标准 STT
stt = STT(
    app_id="your_app_id",
    cluster="your_cluster",
    access_token="your_access_token",
)

# 大模型 STT (推荐)
stt = BigModelSTT(
    app_id="your_app_id",
    access_token="your_access_token",
    model_name="bigmodel",
    enable_punc=True,
)
```

### TTS (语音合成)

```python
from livekit.plugins.volcengine import TTS

tts = TTS(
    app_id="your_app_id",
    cluster="volcano_tts",
    access_token="your_access_token",
    voice="BV001_V2_streaming",  # 音色
    sample_rate=24000,
)
```

### LLM (大语言模型)

```python
from livekit.plugins.volcengine import LLM

# 豆包大模型
llm = LLM(
    model="doubao-1-5-lite-32k-250115",
    api_key="your_api_key",
    base_url="https://ark.cn-beijing.volces.com/api/v3/",
)

# 兼容 OpenAI 接口的其他模型
llm = LLM(
    model="qwen3-max",
    api_key="your_api_key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
```

### RealtimeModel (实时语音)

```python
from livekit.plugins.volcengine import RealtimeModel

realtime = RealtimeModel(
    app_id="your_app_id",
    access_token="your_access_token",
    bot_name="智能助手",
)
```

### 与 LiveKit Agent 集成

```python
from livekit.agents import AgentSession, Agent
from livekit.plugins import volcengine, silero

session = AgentSession(
    vad=silero.VAD.load(),
    stt=volcengine.BigModelSTT(
        app_id="your_app_id",
        access_token="your_access_token",
    ),
    llm=volcengine.LLM(
        model="doubao-1-5-lite-32k-250115",
        api_key="your_api_key",
    ),
    tts=volcengine.TTS(
        app_id="your_app_id",
        cluster="volcano_tts",
        access_token="your_access_token",
    ),
)
```

## 环境变量

可通过环境变量配置凭证：

```bash
# STT
export VOLCENGINE_STT_ACCESS_TOKEN="your_access_token"
export VOLCENGINE_STT_APP_ID="your_app_id"

# TTS
export VOLCENGINE_TTS_ACCESS_TOKEN="your_access_token"

# LLM
export VOLCENGINE_LLM_API_KEY="your_api_key"
```

## API 参考

### BigModelSTT 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `app_id` | str | - | 应用 ID |
| `access_token` | str | - | Access Token |
| `model_name` | str | `"bigmodel"` | 模型名称 |
| `enable_punc` | bool | `True` | 启用标点 |
| `enable_itn` | bool | `False` | 启用文本规范化 |
| `enable_ddc` | bool | `False` | 启用语义顺滑 |
| `vad_segment_duration` | int | `3000` | VAD 分句时长 (ms) |
| `end_window_size` | int | `500` | 静音判停时长 (ms) |

### TTS 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `app_id` | str | - | 应用 ID |
| `cluster` | str | - | 集群名称 |
| `access_token` | str | - | Access Token |
| `voice` | str | `"BV001_V2_streaming"` | 音色 |
| `sample_rate` | int | `16000` | 采样率 |
| `speed` | float | `1.0` | 语速 (0.2-3.0) |
| `volume` | float | `1.0` | 音量 (0.1-3.0) |
| `pitch` | float | `1.0` | 音调 (0.1-3.0) |

### LLM 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | str | `"doubao-1-5-lite-32k-250115"` | 模型名称 |
| `api_key` | str | - | API Key |
| `base_url` | str | 豆包 API | API 地址 |
| `temperature` | float | - | 温度参数 |
| `tool_choice` | str | - | 工具选择策略 |

## 依赖

- `livekit-agents ~= 1.4.4`
- `numpy`
- `openai >= 1.75.0`
- `pydantic`

## 相关链接

- [LiveKit Agents 文档](https://docs.livekit.io/agents/)
- [火山引擎语音技术](https://www.volcengine.com/docs/6561/1594356)
- [豆包大模型](https://www.volcengine.com/docs/82379/1099455)

## 许可证

Apache 2.0
