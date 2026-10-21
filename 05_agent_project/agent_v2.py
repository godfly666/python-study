# 项目二 · 第 1 步:把"检索"包装成一个工具,让模型自己决定要不要查
#
# 跑通标准(两条):
#   问"10.14 那天我为什么是零日?" → 它会自己调 search_docs,再基于结果回答
#   问"3 乘 7 等于几?"           → 它不调工具,直接答 21
#
# 这份骨架是完整的,只有 3 个空(空① 空② 空③)要你填。
# 运行:
#   cd C:\Users\l1809\PycharmProjects\WelcomeScreen\study\05_agent_project
#   ..\..\.venv\Scripts\python.exe agent_v2.py

import os
import json
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

STUDY = r"C:\Users\l1809\PycharmProjects\WelcomeScreen\study"
load_dotenv(os.path.join(STUDY, ".env"))

# 两个客户端:智谱管"把字变数字",DeepSeek 管"说话 + 决定用不用工具"
zp = OpenAI(api_key=os.environ["ZHIPU_API_KEY"],
            base_url="https://open.bigmodel.cn/api/paas/v4/")
ds = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com")

# 直接复用项目一建好的库(写成绝对路径 → 不管在哪个目录启动都找得到)
db = chromadb.PersistentClient(path=os.path.join(STUDY, "04_rag_project", "chroma_db_v3"))
col = db.get_or_create_collection(name="my_docs_v2", metadata={"hnsw:space": "cosine"})


def embed(text: str):
    """一句话 → 2048 个数字(和项目一里那个一模一样)"""
    resp = zp.embeddings.create(model="embedding-3", input=text)
    return resp.data[0].embedding


def search_docs(query: str) -> str:
    """【给大模型用的工具】输入一个问题,返回最相关的 3 段原文(带出处)

    注意:返回值必须是字符串 —— 大模型只收文本,不收 list。
    """
    res = col.query(query_embeddings=[embed(query)], n_results=3)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]

    # 空① —— 一道硬闸:第 1 名都远到这个程度,说明库里没有,直接告诉模型"没查到"。
    #         (项目一 rag_api.py 里你写过同样的判断,阈值一样)
    if not docs or dists[0] > 0.75:          # ★空① = 0.75
        return "(没有检索到相关内容)"

    # 空② —— 把 3 段拼成一段文本:每段前面带 [文件名 第N段],块与块之间空一行。
    #         (项目一 rag_api.py 里那个 context = ... 写得一模一样,搬过来即可)
    return "\n\n".join(                      # ★空② = 拼字符串的表达式
        f"[{m['source']} 第{m['para']}段]\n{d}"
        for d, m in zip(docs, metas)
    )


# 说明书:告诉模型"有这么个工具、什么时候用、参数是什么"
TOOLS = [{
    "type": "function",
    "function": {
        "name": "search_docs",
        "description": "查询我自己的笔记、转行日志、学习记录。当问题涉及我的个人信息、项目进度、学习经历时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "要检索的问题,用原话即可"}
            },
            "required": ["query"],
        },
    },
}]

SYSTEM = """你是一个助手,可以调用 search_docs 工具查询用户的私人笔记。
规则:
1. 问题涉及用户的个人信息、项目、学习记录时,先调用 search_docs 再回答。
2. 数学计算、常识问题直接回答,不要调用工具。
3. 工具返回"(没有检索到相关内容)"时,老老实实说资料里没有,不许编。"""


def main():
    q = input("你: ").strip()
    if not q:
        return

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": q},
    ]

    # ---- 第 1 次问模型:连 tools 说明书一起给它,让它自己决定"答"还是"调工具" ----
    resp = ds.chat.completions.create(model="deepseek-chat", messages=messages, tools=TOOLS)
    msg = resp.choices[0].message

    # 空③ —— 判断:模型这次是"要调工具"还是"直接回答"?
    #         要调工具时 msg.tool_calls 是个列表;直接回答时它是 None。
    if msg.tool_calls:                       # ★空③
        tc0 = msg.tool_calls[0]
        print(f"[模型决定调用工具] {tc0.function.name}({tc0.function.arguments})")

        # ① 把模型"我要调工具"这个决定,也当成一条历史记下来
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })

        # ② 逐个执行工具,把结果作为 role="tool" 的消息塞回历史
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)   # arguments 是 JSON 字符串,先解析
            result = search_docs(**args)               # 真正干活的是你自己写的函数
            print(f"[工具返回] 前 80 字:{result[:80]}...")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,                 # 回执单号,必须带,不然模型对不上
                "content": result,
            })

        # ③ 第 2 次问模型:这次它能看到工具结果了
        resp2 = ds.chat.completions.create(model="deepseek-chat", messages=messages, tools=TOOLS)
        print("\n助手:", resp2.choices[0].message.content)
    else:
        print("\n助手:", msg.content)


if __name__ == "__main__":
    main()
