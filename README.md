# livekit-plugins-volcengine

[![PyPI version](https://badge.fury.io/py/livekit-plugins-volcengine.svg)](https://pypi.org/project/livekit-plugins-volcengine/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

火山引擎服务专用的 [LiveKit Agents](https://github.com/livekit/agents) 插件，提供完整的语音和语言模型集成解决方案。

## 📦 关于此仓库

这是 `livekit-plugins-volcengine` 包的**原始源代码**（版本 1.3.0），从 PyPI 官方包中提取并重新组织为标准的 Python 包结构。

- **原始包**: https://pypi.org/project/livekit-plugins-volcengine/
- **版本**: 1.3.0
- **作者**: wangmengdi <790990241@qq.com>
- **许可证**: Apache 2.0

## ✨ 特性

- 🎤 **语音识别 (STT)** - 支持火山引擎语音识别服务
- 🗣️ **语音合成 (TTS)** - 支持火山引擎文本转语音服务
- 🤖 **大语言模型 (LLM)** - 支持豆包大模型系列
- 🎯 **大模型语音识别 (BigModelSTT)** - 增强版语音识别服务
- ⚡ **实时语音模型 (Realtime)** - 端到端实时语音交互
- 🔧 **简单集成** - 与 LiveKit Agents 框架无缝集成
- 📦 **开箱即用** - 完整的 Python 包支持

## 🛠️ 安装

### 从 PyPI 安装（推荐）

```bash
pip install livekit-plugins-volcengine
```

### 从本仓库安装

```bash
# 克隆仓库
git clone https://github.com/your-username/livekit-plugins-volcengine.git
cd livekit-plugins-volcengine

# 安装
pip install -e .
```

### 从源码构建

```bash
# 构建包
python -m build

# 安装构建的包
pip install dist/livekit_plugins_volcengine-1.3.0-py3-none-any.whl
```

## 📖 使用方法

安装后，可以像使用官方包一样导入：

```python
from livekit.plugins import volcengine

# 使用实时语音模型
llm = volcengine.RealtimeModel(
    app_id="your_app_id",
    access_token="your_access_token",
    bot_name="智能助手",
    model="O"
)
```

详细使用文档请参考 [火山引擎官方文档](https://www.volcengine.com/docs/6561/1594356)。

## 📁 项目结构

```
livekit-plugins-volcengine/
├── livekit/
│   └── plugins/
│       └── volcengine/
│           ├── __init__.py          # 包初始化
│           ├── bigmodel_stt.py      # 大模型语音识别
│           ├── llm.py               # 大语言模型集成
│           ├── realtime.py          # 实时语音模型
│           ├── stt.py               # 标准语音识别
│           ├── tts.py               # 语音合成
│           ├── utils.py             # 工具函数
│           ├── version.py           # 版本信息
│           └── py.typed             # 类型标注
├── pyproject.toml                   # 包配置
├── README.md                        # 说明文档
└── LICENSE                          # 许可证

```

## 🔍 代码来源验证

此仓库中的代码是从 PyPI 官方包中提取的原始代码：

1. 使用 `pip download livekit-plugins-volcengine` 下载官方 wheel 包
2. 解压 wheel 包提取源代码
3. 重新组织为标准 Python 包结构
4. 添加构建配置文件（`pyproject.toml`）

**代码完全未修改**，只是调整了目录结构以支持从源码安装。

## ⚙️ 系统要求

- Python >= 3.9
- LiveKit Agents == 1.2.9

## 📝 依赖项

```
livekit-agents==1.2.9
numpy
openai>=1.75.0
osc-data==0.2.2
pydantic
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 Apache 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 原作者邮箱: 790990241@qq.com
- PyPI 包: https://pypi.org/project/livekit-plugins-volcengine/

## 🙏 致谢

- [LiveKit](https://github.com/livekit/agents) - 优秀的实时通信框架
- [火山引擎](https://www.volcengine.com/) - 强大的AI服务提供商
- 原作者 wangmengdi - 开发并维护此插件
