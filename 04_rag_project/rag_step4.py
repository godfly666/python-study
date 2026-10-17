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
    for i, p in enumerate(text.split("\n\n")):
        p = p.strip()
        if len(p) < 20:          # 太短的是空行/分隔线,丢掉
            continue
        docs.append(p)
        # 空①:这一段的"身份证"要存什么?后面才能回答"这句话出自哪个文件第几段"
        #    提示:你需要文件名 + 段号 → 一个字典
        #    文件名的写法:os.path.basename(path)
        metas.append({"source": os.path.basename(path), "para": i})

print(f"共切成 {len(docs)} 段")

# ---------- 2. 入库(注意:换个库名,别覆盖 R3 的 kefu)----------
db  = chromadb.PersistentClient(path="./chroma_db_v2")
col = db.get_or_create_collection(name="my_docs", metadata={"hnsw:space": "cosine"})

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