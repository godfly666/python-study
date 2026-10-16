import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["ZHIPU_API_KEY"], base_url="https://open.bigmodel.cn/api/paas/v4/")

def embed(text):
    resp = client.embeddings.create(model="embedding-3", input=text)
    return resp.data[0].embedding

def dot(a, b):
    """点积:对应位置相乘,再全部相加"""
    return sum(x*y for x, y in zip(a, b))     # 这一轮要乘的,是 x 和 y

def length(v):
    """长度:每个数平方、累加、开平方"""
    return sum(x*x for x in v) ** 0.5         # 这个 x 是啥,就平方啥

def cosine(a, b):
    return dot(a, b) / (length(a) * length(b))

sentences = [
    "AI Agent 是一种能自主决策并调用工具的智能系统",   # 0
    "智能体可以自己判断该用哪个工具来完成任务",          # 1
    "An AI agent can decide which tool to use.",      # 2
    "今天中午我吃了一碗牛肉面",                        # 3
    "家里的猫又把花瓶打碎了",                          # 4
    "Python 的列表推导式写起来很简洁",                  # 5
]

vecs = [embed(s) for s in sentences]




for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        print(f"{cosine(vecs[i], vecs[j]):.4f}   [{i}]  <->  [{j}]")