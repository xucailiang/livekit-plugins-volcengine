import warnings
from importlib.metadata import version as get_version

__version__ = "1.3.0"

MINIMUM_LIVEKIT_AGENTS_VERSION = "1.2.9"


def check_livekit_agents_version() -> None:
    """检查 livekit-agents 版本兼容性"""
    try:
        installed_version = get_version("livekit-agents")
        if installed_version < MINIMUM_LIVEKIT_AGENTS_VERSION:
            warnings.warn(
                f"livekit-plugins-volcengine {__version__} requires "
                f"livekit-agents >= {MINIMUM_LIVEKIT_AGENTS_VERSION}, "
                f"but {installed_version} is installed. "
                f"Some features may not work correctly.",
                UserWarning,
                stacklevel=2,
            )
    except Exception:
        pass  # 无法获取版本时静默忽略
