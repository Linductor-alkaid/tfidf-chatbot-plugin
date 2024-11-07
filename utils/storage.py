import json
import os
from datetime import datetime

# 文件路径
MESSAGE_PATH = "data/message.json"
IMAGE_PATH = "data/image.json"

def initialize_files():
    """初始化 JSON 文件，如果文件不存在则创建空文件"""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    if not os.path.exists(MESSAGE_PATH):
        with open(MESSAGE_PATH, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
            
    if not os.path.exists(IMAGE_PATH):
        with open(IMAGE_PATH, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

def load_data(file_path):
    """加载 JSON 文件数据，如果文件不存在则创建一个空文件并返回空数据"""
    if not os.path.exists(file_path):
        initialize_files()
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, file_path):
    """保存数据到 JSON 文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 更新消息记录
def update_message_json(group_id, user_id, message):
    """更新 message.json 文件，将新的消息存储进去"""
    messages = load_data(MESSAGE_PATH)

    # 检查 group_id 和 user_id 是否存在，不存在则创建
    if group_id not in messages:
        messages[group_id] = {}
    if user_id not in messages[group_id]:
        messages[group_id][user_id] = {}

    # 获取该用户的当前消息数量，作为 messageID
    message_id = str(len(messages[group_id][user_id]) + 1)

    # 获取连续消息类型和内容
    last_message_info = get_last_message_info(messages, group_id, user_id)

    # 添加新的消息记录
    messages[group_id][user_id][message_id] = {
        "last message": last_message_info,
        "type": message["type"],
        "content": message["content"],
        "time": message["time"],
        "node": message_id
    }

    # 保存数据
    save_data(messages, MESSAGE_PATH)

def get_last_message_info(messages, group_id, user_id):
    """获取用户前一条消息的类型和内容"""
    # 查找其他用户的最后一条消息
    other_user_messages = []
    for other_user_id, user_messages in messages[group_id].items():
        if other_user_id != user_id:
            last_msg = list(user_messages.values())[-1]
            other_user_messages.append(last_msg)

    if other_user_messages:
        all_types = [msg["type"] for msg in other_user_messages]
        all_contents = [msg["content"] for msg in other_user_messages]
        return {"all type": all_types, "all content": all_contents}
    return None

# 更新图像记录
def update_image_json(image_path):
    """更新 image.json 文件，存储新的图像路径并返回 imageID"""
    images = load_data(IMAGE_PATH)

    # 获取新的 imageID
    image_id = str(len(images) + 1)

    # 更新图像路径
    images[image_id] = {"content": image_path}

    # 保存数据
    save_data(images, IMAGE_PATH)

    return image_id

# 处理消息内容函数
def process_message_content(message):
    """处理消息内容，将图像内容替换为 imageID"""
    if message["type"] == "图片":
        image_path = message["content"]
        image_id = update_image_json(image_path)
        message["content"] = f"image{image_id}"
    return message

# 调用时示例
def handle_new_message(group_id, user_id, message_type, content):
    """处理新消息并存储到文件中"""
    # 确保文件已初始化
    initialize_files()

    # 创建消息字典
    message = {
        "type": message_type,
        "content": content,
        "time": int(datetime.now().timestamp())
    }

    # 处理内容，如有图片则更新 imageID
    message = process_message_content(message)

    # 更新消息文件
    update_message_json(group_id, user_id, message)
