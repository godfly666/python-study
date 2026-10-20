import os
import hmac
from fastapi import FastAPI, UploadFile, File, HTTPException
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.responses import FileResponse
from pydantic import BaseModel          # 放在文件开头 import 区
BASE = os.path.dirname(os.path.abspath(__file__))
STUDY = r"C:\Users\l1809\PycharmProjects\WelcomeScreen\study"
UPLOAD_DIR = os.path.join(BASE, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)          # 不存在就建,存在也不报错

load_dotenv(os.path.join(STUDY, ".env"))         # 顺序!先读 .env 再取 key
client = OpenAI(api_key=os.environ["ZHIPU_API_KEY"],
                base_url="https://open.bigmodel.cn/api/paas/v4/")

# 第二个客户端:DeepSeek,管"把人话说明白"(和智谱那个管"变数字"的不是一回事)
ds = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com")

# 给模型的规矩:注意第 3 条 —— 出处不再让模型写,由后端从检索结果里直接给
RULES = """1. 只能根据我提供的【资料】回答，不许使用你自己的知识或常识补充。
2. 如果【资料】里找不到答案，就只回答："该问题不在文库中"。
3. 答案里不要写出处，也不要写"根据资料"之类的话，直接回答问题。"""

# ---- 演示口令:公网暴露时必须加,否则谁拿到链接都能传文件、刷我的余额 ----
# 写在 .env 里(DEMO_KEY=...),不进代码;为空则等于不设防(只在本机调试时这样用)
DEMO_KEY = os.environ.get("DEMO_KEY", "").strip()


def check_key(k: str):
    """比较口令。用 hmac.compare_digest:逐字符比较耗时恒定,不会被"按响应时间猜口令"攻击"""
    if DEMO_KEY and not hmac.compare_digest(k, DEMO_KEY):
        raise HTTPException(status_code=403, detail="口令不对:链接里要带 ?k=你的口令")


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
async def upload(file: UploadFile = File(...), k: str = ""):
    check_key(k)
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
class AskBody(BaseModel):               # 请求体的形状:{"q": "你的问题"}
    q: str

@app.post("/ask")
async def ask(body: AskBody, k: str = ""):
    check_key(k)                     # 先验口令,再花算力
    res = col.query(query_embeddings=[embed(body.q)], n_results=3)
    docs, metas, dists = res["documents"][0], res["metadatas"][0], res["distances"][0]

    # 一道很松的硬闸:第 1 名都远到这个程度,说明库里确实没有 → 连模型都不用调(省钱+不给它编的机会)
    if not docs or dists[0] > 0.75:
        return {"answer": "该问题不在文库中", "sources": []}

    # 空①:把 3 段资料拼成一段文字,格式 [文件名 第N段]\n正文,块与块之间空一行
    context = "\n\n".join(
        f"[{m['source']} 第{m['para']}段]\n{d}" for d, m in zip(docs, metas)
    )

    # 空②:调 DeepSeek 拿答案(和 mini_agent/chat_v2 里一模一样的用法)
    resp = ds.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": RULES},
            {"role": "user", "content": f"资料：\n{context}\n\n问题：{body.q}"},
        ],
    )
    answer = resp.choices[0].message.content.strip()

    sources = [{"source": m["source"], "para": m["para"], "distance": round(float(d), 4)}
               for m, d in zip(metas, dists)]      # ← 出处由后端给,模型碰不到

    # 模型说"没有"的时候,列出出处会自相矛盾(页面上一边说不在文库中,一边列 3 条来源)
    if "不在文库中" in answer:
        return {"answer": answer, "sources": []}
    return {"answer": answer, "sources": sources}


@app.get("/")
def home():
    """浏览器打开 http://127.0.0.1:8000/ 时,把这个 HTML 文件吐出去"""
    return FileResponse(os.path.join(BASE, "static", "index.html"))