import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()
client = OpenAI(api_key=os.environ["ZHIPU_API_KEY"], base_url="https://open.bigmodel.cn/api/paas/v4/")

def embed(text):
    """把一段文字变成向量(2048 个数字)"""
    resp = client.embeddings.create(model="embedding-3", input=text)
    return resp.data[0].embedding

# ---------- ① 开库:数据落在当前目录的 chroma_db 文件夹里 ----------
db = chromadb.PersistentClient(path="./chroma_db")
col = db.get_or_create_collection(name="kefu", metadata={"hnsw:space": "cosine"})

# ---------- ② 入库:原文 + 向量,两份都存(索书号 + 书) ----------
docs = [
    "订单签收后 7 天内可以无理由退货,商品需保持完好,运费由买家承担。",
    "发票会在订单完成后 24 小时内开具,可在订单详情页下载电子发票。",
    "普通快递一般 48 小时内发货,偏远地区可能需要 3 到 5 天。",
    "会员积分在订单完成后发放,每消费 1 元积 1 分,积分可抵扣现金。",
]

col.upsert(
    ids=[f"doc{i}" for i in range(len(docs))],
    documents=docs,
    embeddings=[embed(d) for d in docs],
)

# ---------- ③ 提问:把问题也变成向量,去库里找最近的几段 ----------
q1 = "我买的东西不想要了,钱能退回来吗?"        # ← 实验开关 A:只改这一行
q2 = "发票怎么下载?"
q3 = "今天天气怎么样?"
n_results=4
res = col.query(query_embeddings=[embed(q1)], n_results=4)   # ← 实验开关 B:n_results

print("提问:", q1)
for i, (doc, dist) in enumerate(zip(res["documents"][0], res["distances"][0]), 1):
    print(f"第 {i} 名(距离 {dist:.4f}): {doc}")