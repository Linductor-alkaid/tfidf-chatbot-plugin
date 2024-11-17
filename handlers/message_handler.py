import requests
import os
import mimetypes
from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent
from ..utils.storage import handle_new_message

message_event = on_message(priority=5)

# 指定一个目录来保存图片
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
IMAGE_PATH = os.path.join(DATA_DIR, "./images")

# 确保图片目录存在
os.makedirs(IMAGE_PATH, exist_ok=True)

def sanitize_filename(filename):
    """
    移除非法字符，规范化文件名。
    """
    return "".join(c if c.isalnum() or c in "-_.()" else "_" for c in filename)

def download_image(image_url):
    """
    下载图片并保存为本地文件。
    """
    try:
        # 发送 HTTP GET 请求以获取图片
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # 获取文件名并规范化
        filename = sanitize_filename(os.path.basename(image_url))
        # 获取扩展名
        content_type = response.headers.get("Content-Type")
        ext = mimetypes.guess_extension(content_type)
        if not ext:
            ext = ".png"  # 如果未识别出扩展名，默认使用 .png

        # 构建图片的本地路径
        image_path = os.path.join(IMAGE_PATH, filename + ext)

        # 保存图片
        with open(image_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        return image_path
    except Exception as e:
        print(f"图片下载失败: {e}")
        return None

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
            # 获取图片 URL
            image_url = segment.data.get("url", segment.data.get("file"))
            if image_url:
                # 下载图片并返回本地路径
                image_path = download_image(image_url)
                if image_path:
                    return "图片", image_path
                else:
                    return "图片", "图片下载失败"

    # 如果是其他类型，如语音消息，不处理
    return "未知", ""
