from types import ModuleType

from nonebot import logger
from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_localstore")
require("nonebot_plugin_orm")


API: ModuleType
builtin_hook: ModuleType
config: ModuleType
matcher_manager: ModuleType
preprocess: ModuleType

try:
    __import__("amrita")  # Amrita 适配
    logger.info("检测到Amrita，SuggarChat将转发Amrita模块。")
    require("amrita.plugins.chat")
    from amrita.plugins.chat import (  # type: ignore
        API,
        builtin_hook,
        config,
        matcher_manager,
        preprocess,
    )
except ImportError:
    __plugin_meta__ = PluginMetadata(
        name="SuggarChat LLM聊天插件",
        description="强大的聊天插件，即配即用，内建OpenAI协议客户端实现，多模型切换，DeepSeek/Gemini支持，多模态模型支持，适配Onebot-V11适配器",
        usage="https://docs.suggar.top/project/suggarchat/",
        homepage="https://github.com/LiteSuggarDEV/nonebot_plugin_suggarchat/",
        type="application",
        supported_adapters={"~onebot.v11"},
    )
    from . import (
        API,
        builtin_hook,
        config,
        matcher_manager,
        preprocess,
    )

__all__ = [
    "API",
    "builtin_hook",
    "config",
    "matcher_manager",
    "preprocess",
]
