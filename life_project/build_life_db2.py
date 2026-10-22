# -*- coding: utf-8 -*-
"""ask-life v2:把每页再切成 600 字窗口(重叠 100),重新建库,对比检索精度。"""
import json
import os
import sys
import time

BASE = r"C:\Users\l1809\PycharmProjects\WelcomeScreen\study"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(BASE, ".env"))
client = OpenAI(api_key=os.environ["ZHIPU_API_KEY"], base_url="https://open.bigmodel.cn/api/paas/v4/")

WIN, STEP = 600, 500
segs = [json.loads(l) for l in open(os.path.join(HERE, "segments.jsonl"), encoding="utf-8")]

texts, metas, ids = [], [], []
for s in segs:
    t = s["text"]
    if len(t) <= 700:
        parts = [t]
    else:
        parts = [t[i:i + WIN] for i in range(0, len(t), STEP)]
        if len(parts) > 1 and len(parts[-1]) < 120:   # 尾巴太短就并进上一块
            parts[-2] += parts[-1]
            parts.pop()
    for n, part in enumerate(parts):
        ids.append(f"{s['id']}_c{n}")
        texts.append(part)
        metas.append({**s["meta"], "chunk": n})

print(f"原 {len(segs)} 页 → 细粒度 {len(texts)} 块")

db = chromadb.PersistentClient(path=os.path.join(HERE, "chroma_life"))
try:
    db.delete_collection("how_to_live_v2")
except Exception:
    pass
col = db.get_or_create_collection(name="how_to_live_v2", metadata={"hnsw:space": "cosine"})

BATCH = 25
t0 = time.time()
for start in range(0, len(texts), BATCH):
    batch = texts[start:start + BATCH]
    resp = client.embeddings.create(model="embedding-3", input=batch)
    col.upsert(
        ids=ids[start:start + BATCH],
        documents=batch,
        embeddings=[d.embedding for d in resp.data],
        metadatas=metas[start:start + BATCH],
    )
print(f"入库完成 {col.count()} 块,耗时 {time.time()-t0:.0f}s")

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
        print(f"  {dist:.4f} | 第{meta['page']}页 | {meta['section'][:20]} | {doc.replace(chr(10),' ')[:66]}")
