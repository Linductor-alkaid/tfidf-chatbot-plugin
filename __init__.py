from nonebot import get_driver
from nonebot.plugin import PluginMetadata

from .config import Config
from .main import handle_message  # 确保插件加载时执行 main.py 的消息处理
from .utils.tfidf import calculate_tfidf  # 导入 tfidf 计算函数

__plugin_meta__ = PluginMetadata(
    name="chatbot-plugin",
    description="聊天机器人插件",
    usage="自动记录接收数据，生成合适的回复",
    config=Config,
)

global_config = get_driver().config
config = Config.parse_obj(global_config)

# 在插件初始化时进行一次 TF-IDF 计算
calculate_tfidf()
