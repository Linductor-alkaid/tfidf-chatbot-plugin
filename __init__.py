from nonebot import get_driver
from nonebot.plugin import PluginMetadata

from .config import Config
from .main import handle_message  # 导入主入口的事件处理器，确保插件加载时执行

__plugin_meta__ = PluginMetadata(
    name="chatbot-plugin",
    description="聊天机器人插件",
    usage="自动记录接收数据，生成合适的回复",
    config=Config,
)

global_config = get_driver().config
config = Config.parse_obj(global_config)
