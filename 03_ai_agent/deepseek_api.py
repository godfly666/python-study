import os

from dotenv import load_dotenv
from openai import OpenAI

# 从同目录的 .env 读密钥(.env 被 .gitignore 挡住,永远不进 Git)
load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用一句话解释什么是 AI Agent"}],
)

print(resp.choices[0].message.content)
