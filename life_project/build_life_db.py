# -*- coding: utf-8 -*-
"""ask-life:把 HowToLiveBetter 的 582 段入库(批量 embedding),然后跑 3 个验收问题。"""
import json
import os
import sys
import time

BASE = r"C:\Users\l1809\PycharmProjects\WelcomeScreen\study"
sys.path.insert(0, BASE)

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(BASE, ".env"))

client = OpenAI(
    api_key=os.environ["ZHIPU_API_KEY"],
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

segs = []
with open(os.path.join(os.path.dirname(__file__), "segments.jsonl"), encoding="utf-8") as f:
    for line in f:
        segs.append(json.loads(line))
texts = [s["text"] for s in segs]
metas = [s["meta"] for s in segs]
ids = [s["id"] for s in segs]
print(f"读入 {len(segs)} 段")

db = chromadb.PersistentClient(path=os.path.join(os.path.dirname(__file__), "chroma_life"))
col = db.get_or_create_collection(name="how_to_live_better", metadata={"hnsw:space": "cosine"})

BATCH = 25
t0 = time.time()
for start in range(0, len(texts), BATCH):
    batch = texts[start:start + BATCH]
    resp = client.embeddings.create(model="embedding-3", input=batch)
    vecs = [d.embedding for d in resp.data]
    col.upsert(
        ids=ids[start:start + BATCH],
        documents=batch,
        embeddings=vecs,
        metadatas=metas[start:start + BATCH],
    )
    print(f"已入库 {min(start + BATCH, len(texts))}/{len(texts)}  ({time.time()-t0:.1f}s)")

print("库内片段数:", col.count())

tests = [
    "电动车电池在楼道充电到底多危险?",
    "被裁员时 N、N+1、2N 怎么算?",
    "老人摔倒了能不能扶?扶了被讹怎么办?",
]
for q in tests:
    qv = client.embeddings.create(model="embedding-3", input=[q]).data[0].embedding
    res = col.query(query_embeddings=[qv], n_results=3)
    print("\n" + "=" * 70)
    print("问:", q)
    for dist, meta, doc in zip(res["distances"][0], res["metadatas"][0], res["documents"][0]):
        head = doc.replace("\n", " ")[:70]
        print(f"  距离 {dist:.4f} | 第{meta['page']}页 | {meta['section'][:22]} | {head}")
