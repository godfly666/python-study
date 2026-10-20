import os
from fastapi import FastAPI, UploadFile, File, HTTPException
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

BASE = os.path.dirname(os.path.abspath(__file__))
STUDY = r"C:\Users\l1809\PycharmProjects\WelcomeScreen\study"
UPLOAD_DIR = os.path.join(BASE, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)          # 不存在就建,存在也不报错

load_dotenv(os.path.join(STUDY, ".env"))         # 顺序!先读 .env 再取 key
client = OpenAI(api_key=os.environ["ZHIPU_API_KEY"],
                base_url="https://open.bigmodel.cn/api/paas/v4/")

db = chromadb.PersistentClient(path=os.path.join(BASE, "chroma_db_v3"))
col = db.get_or_create_collection(name="my_docs_v2", metadata={"hnsw:space": "cosine"})

app = FastAPI()

def embed(text):                 # 一个参数(一句话),一份职责(变成向量)。函数不打印,只返回
    resp = client.embeddings.create(
        model="embedding-3",     # 模型名决定维度:这个名字给 2048 维;换成别的模型,维度就变了
        input=text,              # 参数叫 input(不是 messages) —— 向量接口和对话接口是两套东西
    )
    vec = resp.data[0].embedding  # 一层层剥:resp -> .data(一批结果) -> [0](第一条) -> .embedding(数字列表)
    return vec                   # 行末千万别多一个逗号,否则整串数字会变成"元组"(len 就变成 1)


def split_text(text: str) -> list[str]:
    # 统一换行符:Windows 上传的文件是 \r\n,而 split("\n\n") 只认 \n\n
    # 不统一的话,整篇会被当成"一段"(chunks 永远 = 1)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    raw = [x.strip() for x in text.split("\n\n")]

    blocks, i = [], 0
    while i < len(raw):
        p = raw[i]                                    # 取出当前位置的一段
        if not p:
            i += 1
            continue
        nxt = raw[i + 1] if i + 1 < len(raw) else ""
        if p.startswith("#") and nxt and not nxt.startswith("#"):
            blocks.append(p + "\n\n" + nxt)           # 标题 + 正文 = 一块
            i += 2
        else:
            blocks.append(p)                          # 其他照原样
            i += 1

    return [b for b in blocks if len(b) >= 20]        # 过滤太短的(分隔线/空块)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # ① 先校验:不合法就别安排算力(别为一个 .png 花几十秒算 embedding)
    ALLOWED = (".md", ".txt")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail="只支持 .md / .txt 文件")

    # ② 读内容 + 原文件落盘留底
    raw = await file.read()
    text = raw.decode("utf-8")
    safe_name = os.path.basename(file.filename)        # 只取文件名,防止 ../ 目录穿越
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(save_path, "wb") as f:                   # "wb" 写 bytes
        f.write(raw)

    # ③ 切分
    blocks = split_text(text)
    if not blocks:
        raise HTTPException(status_code=400, detail="文件里没有可用内容")

    # ④ 入库:id 用 文件名#段号 → 同一文件重传只覆盖、不新增(幂等)
    stem = os.path.splitext(file.filename)[0]
    metas = [{"source": file.filename, "para": i + 1} for i in range(len(blocks))]
    col.upsert(
        ids=[f"{stem}#{i + 1}" for i in range(len(blocks))],
        documents=blocks,
        embeddings=[embed(b) for b in blocks],
        metadatas=metas,
    )
    return {"file": file.filename, "chunks": len(blocks)}