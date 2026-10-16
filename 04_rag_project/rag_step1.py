import os
from dotenv import load_dotenv
from openai import OpenAI

from study.api.deepseek_api import resp

load_dotenv()

client = OpenAI(
    api_key=os.environ["ZHIPU_API_KEY"],
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

def embed(text: str):
    resp = client.embeddings.create(
        model="embedding-3",
        input=text,

    )
    return  resp.data[0].embedding

if __name__ == "__main__":
    vec = embed("AI Agent 是一种能自主感知环境、做出决策并采取行动的智能系统。")
    print("维度:", len(vec))
    print("前5个数字:", vec[:5])
    print("L2范数:", round(sum(x * x for x in vec) ** 0.5, 6))