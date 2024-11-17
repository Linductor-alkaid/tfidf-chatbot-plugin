import jieba
import json
import math
import os
from collections import defaultdict

# 定义基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
MESSAGE_PATH = os.path.join(DATA_DIR, "message.json")
TFIDF_PATH = os.path.join(DATA_DIR, "tfidf.json")

def load_messages():
    """加载 message.json 中的消息数据"""
    with open(MESSAGE_PATH, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    return messages

def save_tfidf(tfidf_data):
    """将计算出的 TF-IDF 权重数据保存到 tfidf.json 文件中"""
    with open(TFIDF_PATH, 'w', encoding='utf-8') as f:
        json.dump(tfidf_data, f, ensure_ascii=False, indent=4)

def calculate_tf(word_freq, total_words):
    """计算词频（TF）"""
    tf = {word: freq / total_words for word, freq in word_freq.items()}
    return tf

def calculate_idf(word_doc_count, total_docs):
    """计算逆文档频率（IDF）"""
    idf = {word: math.log(total_docs / (1 + count)) for word, count in word_doc_count.items()}
    return idf

def calculate_tfidf():
    """计算并存储 TF-IDF 权重"""
    messages = load_messages()
    tfidf_data = {}

    # 统计每个词的文档频率
    word_doc_count = defaultdict(int)
    total_docs = 0

    # 逐个群组/用户计算
    for group_id, users in messages.items():
        tfidf_data[group_id] = {}
        for user_id, user_messages in users.items():
            total_docs += 1

            # 合并该用户的所有消息内容
            full_text = " ".join(
                msg["content"] if msg["type"] == "文本" else f"image{msg['content']}"
                for msg in user_messages.values()
            )

            # 分词和词频统计
            word_freq = defaultdict(int)
            words = jieba.lcut(full_text)
            total_words = len(words)
            for word in words:
                word_freq[word] += 1

            # 更新每个词的文档频率
            for word in word_freq.keys():
                word_doc_count[word] += 1

            # 计算 TF
            tf = calculate_tf(word_freq, total_words)

            # 暂时存储 TF 数据，待计算 IDF 后计算 TF-IDF
            tfidf_data[group_id][user_id] = tf

    # 计算 IDF
    idf = calculate_idf(word_doc_count, total_docs)

    # 计算 TF-IDF 并存储
    for group_id, users in tfidf_data.items():
        for user_id, tf_data in users.items():
            tfidf_data[group_id][user_id] = {
                word: tf_value * idf[word] for word, tf_value in tf_data.items()
            }

    # 保存 TF-IDF 数据到 tfidf.json
    save_tfidf(tfidf_data)

if __name__ == "__main__":
    calculate_tfidf()
