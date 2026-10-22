# -*- coding: utf-8 -*-
"""ask-life 问答接口:检索《高性价比人生指南》v2 库 → 拼 prompt → DeepSeek 回答 → 带回页码出处。"""
import os
import sys

BASE = r"C:\Users\l1809\PycharmProjects\WelcomeScreen\study"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

load_dotenv(os.path.join(BASE, ".env"))

zc = OpenAI(api_key=os.environ["ZHIPU_API_KEY"], base_url="https://open.bigmodel.cn/api/paas/v4/")
ds = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

db = chromadb.PersistentClient(path=os.path.join(HERE, "chroma_life"))
col = db.get_or_create_collection(name="how_to_live_v2", metadata={"hnsw:space": "cosine"})

RULES = """你是《高性价比人生指南》这本书的问答助手。规则:
1. 只能根据【资料】回答,不要用你自己的知识补充。
2. 资料里没有相关内容时,只回答:这本书里没有找到相关内容。
3. 答案里不要写出处(出处由程序另外给出)。
4. 用大白话,先给结论,再给关键动作。"""

GATE = 0.75   # 第一名距离超过它 → 认为书里没有

app = FastAPI(title="ask-life")


class AskBody(BaseModel):
    q: str


def do_ask(q: str):
    qv = zc.embeddings.create(model="embedding-3", input=[q]).data[0].embedding
    res = col.query(query_embeddings=[qv], n_results=3)
    dists, docs, metas = res["distances"][0], res["documents"][0], res["metadatas"][0]
    if not docs or dists[0] > GATE:
        return {"answer": "这本书里没有找到相关内容。", "sources": []}

    context = "\n\n".join(f"[第{m['page']}页]\n{d}" for d, m in zip(docs, metas))
    resp = ds.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": RULES},
            {"role": "user", "content": f"【资料】\n{context}\n\n【问题】{q}"},
        ],
        temperature=0.2,
    )
    answer = (resp.choices[0].message.content or "").strip()
    sources = [
        {"page": m["page"], "section": m["section"], "distance": round(d, 4)}
        for d, m in zip(dists, metas)
    ]
    if "没有找到" in answer:
        sources = []
    return {"answer": answer, "sources": sources}


@app.get("/ask")
def ask_get(q: str):
    return do_ask(q)


@app.post("/ask")
def ask_post(body: AskBody):
    return do_ask(body.q)


@app.get("/")
def root():
    return {"service": "ask-life", "usage": "/ask?q=你的问题"}
