from .bigmodel_stt import BigModelSTT
from .llm import LLM
from .stt import STT
from .tts import TTS
from .realtime import RealtimeModel
from .version import __version__, check_livekit_agents_version

# 在模块加载时检查版本
check_livekit_agents_version()

__all__ = ["TTS", "LLM", "STT", "BigModelSTT", "RealtimeModel", "__version__", "check_livekit_agents_version"]

from livekit.agents import Plugin

from .log import logger


class VolcenginePlugin(Plugin):
    def __init__(self):
        super().__init__(__name__, __version__, __package__, logger)


Plugin.register_plugin(VolcenginePlugin())

# Cleanup docs of unexported modules
_module = dir()
NOT_IN_ALL = [m for m in _module if m not in __all__]

__pdoc__ = {}

for n in NOT_IN_ALL:
    __pdoc__[n] = False
