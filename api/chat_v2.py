import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

messages = [{"role": "system", "content": "你是一个简洁的中文助手,回答不超过三句话。"}]

while True:
    user_input = input("\n你:")
    if user_input == "exit":
        break

    # ① 把这句存进历史(role="user");content 必须是上面真正接住输入的那个变量名
    messages.append({"role": "user", "content": user_input})

    # ② stream=True:让回答变成"一块一块"回来,而不是等整段
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True,
    )

    answer = ""
    for chunk in stream:
        # ③ 一包数据 → .choices[0] → .delta → .content;没文字时是 None,用 or "" 兜住
        piece = chunk.choices[0].delta.content or ""
        print(piece, end="", flush=True)
        answer += piece
    print()

    # ④ 模型这段回答也要存进历史(role="assistant"),下一轮它才"记得"
    messages.append({"role": "assistant", "content": answer})
