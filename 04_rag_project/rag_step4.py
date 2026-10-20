import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

STUDY = r"C:\Users\l1809\PycharmProjects\WelcomeScreen\study"
load_dotenv(os.path.join(STUDY, ".env"))

client = OpenAI(api_key=os.environ["ZHIPU_API_KEY"],
                base_url="https://open.bigmodel.cn/api/paas/v4/")

def embed(text):
    resp = client.embeddings.create(model="embedding-3", input=text)
    return resp.data[0].embedding

# ---------- 1. 读真实文件,按空行切段 ----------
FILES = [
    r"C:\Users\l1809\Documents\deepseek-harness\default-workspace\90天转行作战计划.md",
    r"C:\Users\l1809\Documents\deepseek-harness\default-workspace\转行日志.md",
]

docs, metas = [], []

for path in FILES:
    text = open(path, encoding="utf-8").read()
    raw = [x.strip() for x in text.split("\n\n")]

    # 【改进版切分】标题段(# 开头)+ 紧随其后的正文段,合并成一块
    # 为什么:标题和正文被切开时,模型手里只有一个孤立标题,
    #        很容易把"相邻的另一天"的正文缝到这个标题底下(错误归因)
    blocks, i = [], 0
    while i < len(raw):
        p = raw[i]
        if not p:
            i += 1
            continue
        nxt = raw[i + 1] if i + 1 < len(raw) else ""
        if p.startswith("#") and nxt and not nxt.startswith("#"):
            blocks.append(p + "\n\n" + nxt)       # 标题 + 正文 = 一块
            i += 2
        else:
            blocks.append(p)                      # 其他照原样
            i += 1

    for b in blocks:
        if len(b) < 20:                           # 太短的是分隔线/空块,丢掉
            continue
        docs.append(b)
        # 身份证 = 文件名 + 段号(从 1 开始数,方便人肉核对第几段)
        metas.append({"source": os.path.basename(path), "para": len(docs)})

print(f"共切成 {len(docs)} 段(标题与正文已合并)")

# ---------- 2. 入库(注意:换个库名,别覆盖 R3 的 kefu)----------
db  = chromadb.PersistentClient(path="./chroma_db_v3")
col = db.get_or_create_collection(name="my_docs_v2", metadata={"hnsw:space": "cosine"})

col.upsert(
    ids=[f"doc{i}" for i in range(len(docs))],
    documents=docs,
    embeddings=[embed(d) for d in docs],
    # 空②:upsert 的四件套里,哪一件装的是"身份证"?把它接上
    metadatas=metas,
)
print(f"入库完成,共 {col.count()} 段")

# ---------- 3. 提问,打印来源 ----------
while True:
    q = input("\n你的问题(exit 退出):").strip()
    if q == "exit":
        break
    res = col.query(query_embeddings=[embed(q)], n_results=3)

    for k in range(len(res["ids"][0])):
        src = res["metadatas"][0][k]
        print(f'[{src["source"]} 第 {src["para"]} 段] 距离 = {res["distances"][0][k]:.4f}')
        print("    正文:" + res["documents"][0][k][:60].replace("\n", " "))