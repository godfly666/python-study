import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "现在几点了?12345*6789 等于多少?987654321*12345 等于多少?直接回答,别解释。"}],
)
print(resp.choices[0].message.content)