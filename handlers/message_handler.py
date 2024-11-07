from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent
from ..utils.storage import handle_new_message

message_event = on_message(priority=5)

@message_event.handle()
async def process_message(event: MessageEvent):
    """
    处理接收到的消息，存储到 JSON 文件中。
    """
    # 判断群聊和私聊
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
    else:
        group_id = "-1"  # 私聊的 group_id 设为 -1

    user_id = str(event.user_id)
    message_type, content = parse_message_content(event)

    # 存储消息
    handle_new_message(group_id=group_id, user_id=user_id, message_type=message_type, content=content)

def parse_message_content(event):
    """
    解析消息内容，根据消息类型返回内容。
    """
    # 获取消息内容
    message_segments = event.message

    for segment in message_segments:
        if segment.type == "text":
            return "文本", segment.data["text"]

        elif segment.type == "image":
            # 若为图片类型，获取图片 URL 或文件路径
            image_path = segment.data.get("url", "path/to/local/image.jpg")  # 替换为实际的文件存储路径
            return "图片", image_path

    # 如果是其他类型，如语音消息，不处理
    return "未知", ""
