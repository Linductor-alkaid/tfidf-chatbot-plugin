import json
import random
from ..utils.tfidf import calculate_tfidf  # 需要确保 tfidf 计算已经完成
from ..utils.storage import load_data

# 文件路径
TFIDF_PATH = "../data/tfidf.json"
MESSAGE_PATH = "../data/message.json"

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
    question_magnitude = sum(value ** 2 for value in question_vector.values()) ** 0.5
    content_magnitude = sum(value ** 2 for value in content_vector.values()) ** 0.5
    if question_magnitude * content_magnitude == 0:
        return 0
    return dot_product / (question_magnitude * content_magnitude)

def get_response(event):
    """主函数，根据消息内容返回一个合理的回复"""
    global is_speaking, speak_count

    # 检查关键词匹配并计算回复概率
    question_text = event.message.extract_plain_text()
    should_respond = decide_response(question_text)

    if should_respond:
        # 获取问题的 TF-IDF 向量
        question_vector = get_tfidf_vector(question_text)
        
        # 读取 message.json，找到最相似的历史消息
        messages = load_data(MESSAGE_PATH)
        best_match = None
        highest_similarity = 0

        for group_id, users in messages.items():
            for user_id, user_messages in users.items():
                for msg_id, msg_content in user_messages.items():
                    last_message = msg_content.get("last message")
                    if last_message:
                        last_message_vector = get_tfidf_vector(" ".join(last_message["all content"]))
                        similarity = calculate_similarity(question_vector, last_message_vector)

                        # 找到最高相似度的消息
                        if similarity > highest_similarity:
                            highest_similarity = similarity
                            best_match = msg_content["content"]

        # 更新机器人状态
        if best_match:
            is_speaking = True
            speak_count += 1
            if speak_count >= MAX_SPEAK_COUNT:
                is_speaking = False
                speak_count = 0
            return best_match  # 返回找到的最相似内容
    return None  # 不回复

def decide_response(question_text):
    """根据机器人状态和关键词决定是否回复"""
    global is_speaking

    # 检查关键词
    contains_keyword = any(keyword in question_text for keyword in keywords)

    if not is_speaking:
        # 未发言状态，关键词匹配时有 80% 概率回复，否则有 5% 概率回复
        return random.random() < 0.8 if contains_keyword else random.random() < 0.05
    else:
        # 发言状态，有 50% 概率回复
        return random.random() < 0.5

def get_tfidf_vector(text):
    """为给定文本生成 TF-IDF 向量"""
    tfidf_data = load_tfidf()
    words = text.split()
    vector = {}

    for word in words:
        for group_data in tfidf_data.values():
            for user_data in group_data.values():
                if word in user_data:
                    vector[word] = user_data[word]["tfidf"]
                    break
    return vector
