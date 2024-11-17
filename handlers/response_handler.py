import json
import os
import random
from ..utils.tfidf import calculate_tfidf
from ..utils.storage import load_data

# 设置基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
TFIDF_PATH = os.path.join(DATA_DIR, "tfidf.json")
MESSAGE_PATH = os.path.join(DATA_DIR, "message.json")
IMAGE_PATH = os.path.join(DATA_DIR, "image.json")

# 机器人状态
is_speaking = False
speak_count = 0
MAX_SPEAK_COUNT = 10  # 达到 10 条后进入未发言状态

# 问题关键词库
keywords = ["独角兽", "机器人", "oi", "梁乘浩", "梁教授", "徒弟", "师傅"]

def load_tfidf():
    """加载 TF-IDF 数据"""
    with open(TFIDF_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_similarity(question_vector, content_vector):
    """计算两个向量之间的余弦相似度"""
    dot_product = sum(question_vector[word] * content_vector.get(word, 0) for word in question_vector)
    print("Dot product:", dot_product)  # 调试信息
    question_magnitude = sum(value ** 2 for value in question_vector.values()) ** 0.5
    content_magnitude = sum(value ** 2 for value in content_vector.values()) ** 0.5
    print("Magnitudes:", question_magnitude, content_magnitude)  # 调试信息
    if question_magnitude * content_magnitude == 0:
        return 0
    return dot_product / (question_magnitude * content_magnitude)

def get_response(event):
    """主函数，根据消息内容返回一个合理的回复"""
    global is_speaking, speak_count

    # 获取消息文本并生成问题向量
    question_text = event.message.extract_plain_text()
    question_vector = get_tfidf_vector(question_text)

    # 检查是否需要回复
    should_respond = decide_response(question_text)
    if should_respond:
        print("判断为需要回复")

        # 读取 message.json，找到最相似的历史消息
        messages = load_data(MESSAGE_PATH)
        images = load_data(IMAGE_PATH)
        best_match = None
        highest_similarity = 0

        # 遍历所有群组和用户的 last_message，确保不漏掉任何用户的历史消息
        for group_id, users in messages.items():
            for user_id, user_messages in users.items():
                for msg_id, msg_content in user_messages.items():
                    last_message = msg_content.get("last message")
                    if last_message and "all content" in last_message:
                        # 获取消息的全部内容作为向量
                        last_message_text = " ".join(last_message["all content"])
                        last_message_vector = get_tfidf_vector(last_message_text)
                        similarity = calculate_similarity(question_vector, last_message_vector)

                        # 找到最高相似度的消息
                        if similarity > highest_similarity:
                            highest_similarity = similarity
                            if msg_content["type"] == "文本":
                                best_match = msg_content["content"]
                                msg_type = "text"
                            elif msg_content["type"] == "图片":
                                # 提取 imageXX 中的 XX
                                image_key = msg_content["content"].replace("image", "")
                                msg_type = "image"
                                # 在 images 中找到对应的对象，并赋值给 best_match
                                image_url = images.get(image_key, {}).get("content")
                                best_match = image_url

        # 输出调试信息，确认找到的最佳匹配
        print("Best match content:", best_match, msg_type)
        print("Highest similarity:", highest_similarity)
        
        # 如果找到相似度较高的历史消息，直接使用该消息作为回复
        if best_match and highest_similarity > 0:  # 增加最高相似度的条件
            is_speaking = True
            speak_count += 1
            if speak_count >= MAX_SPEAK_COUNT:
                is_speaking = False
                speak_count = 0
                calculate_tfidf()  # 达到最大发言数时退出发言状态，触发 TF-IDF 计算
            return best_match, msg_type  # 直接返回找到的最相似内容
    else:
        print("判断为不需要回复")
        calculate_tfidf()  # 不回复时触发 TF-IDF 计算
    return None, None  # 不回复

def decide_response(question_text):
    """根据关键词决定是否回复"""
    global is_speaking

    # 检查是否包含关键词
    contains_keyword = any(keyword in question_text for keyword in keywords)

    # 匹配到关键词时直接回复，否则回复概率为 50%
    if not is_speaking:
        return True if contains_keyword else (random.random() < 0.5)
    else:
        return True

def get_tfidf_vector(text):
    """为给定文本生成 TF-IDF 向量"""
    tfidf_data = load_tfidf()
    words = text.split()  # 可以使用 jieba 分词以确保词汇表匹配
    vector = {}

    for word in words:
        for group_data in tfidf_data.values():
            for user_data in group_data.values():
                if word in user_data:
                    vector[word] = user_data[word]  # 直接获取权重值
                    break
    print("Generated vector:", vector)  # 调试信息
    return vector
