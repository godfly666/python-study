import os                        # 管环境变量:os.environ["名字"] 就是从内存里按名字取东西
from dotenv import load_dotenv   # 把 .env 文件的内容"搬进内存"的函数
import chromadb                  # 向量库本体
from openai import OpenAI        # 客户端类;智谱兼容 OpenAI 协议,所以可以复用它

#---------------格式要求(给模型的规矩)
RULES = """
1. 只能根据我提供的【资料】回答，不许使用你自己的知识或常识补充。
2. 如果【资料】里找不到答案，就只回答：“该问题不在文库中”，不要再补充任何内容。
3. 回答的最后单独一行列出处，格式：[文件名 第N段]，例如 [转行日志.md 第23段]
4. 你的每一条结论都必须能在【资料】原文里找到对应句子；资料里没写的内容一律不许说。
"""
# ---------- A 通行证:让程序能打电话 ----------
load_dotenv()                    # 必须先跑它,后面 os.environ 才读得到 .env 里的东西(顺序反了就是 KeyError)
ds = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")


client = OpenAI(
    api_key=os.environ["ZHIPU_API_KEY"],                 # 通行证:方括号里写 .env 里的变量名;写错会立刻报错,不会悄悄变 None
    base_url="https://open.bigmodel.cn/api/paas/v4/",    # 门牌号:智谱的地址;不写就默认 OpenAI 官方,会走错门
)


# ---------- B 打字机:文字 -> 2048 个数字 ----------
def embed(text):                 # 一个参数(一句话),一份职责(变成向量)。函数不打印,只返回
    resp = client.embeddings.create(
        model="embedding-3",     # 模型名决定维度:这个名字给 2048 维;换成别的模型,维度就变了
        input=text,              # 参数叫 input(不是 messages) —— 向量接口和对话接口是两套东西
    )
    vec = resp.data[0].embedding  # 一层层剥:resp -> .data(一批结果) -> [0](第一条) -> .embedding(数字列表)
    return vec                   # 行末千万别多一个逗号,否则整串数字会变成"元组"(len 就变成 1)


# ---------- C 开柜子:找到(或新建)一个存在硬盘上的库 ----------
db = chromadb.PersistentClient(path="./chroma_db_v3")        # path 是一个文件夹:换 path = 换一个柜子
col = db.get_or_create_collection(                       # 有就打开,没有就新建
    name="my_docs_v2",                                     # 集合名,相当于一张表;换个 name 就是另一个抽屉
    metadata={"hnsw:space": "cosine"},                   # 声明用余弦距离;漏了默认不是余弦,后面距离数字会对不上
)
# ---------- E 提问:问题也变成向量,拿去比 ----------
questions = [
    "10.14 那天我为什么是零日?",
    "我奶奶叫什么名字?",
    "今天天气怎么样?",
]
def retrieve(q, k=3):
    """检索：一个问题 -> 3 段原文 + 3 个出处 + 3 个距离"""
    res = col.query(query_embeddings=[embed(q)], n_results=k)
    return res["documents"][0], res["metadatas"][0], res["distances"][0]

def build_context(docs, metas):
    parts = []
    for doc, meta in zip(docs, metas):        # ← 只传外层列表，两个
        parts.append(f"[{meta['source']} 第{meta['para']}段]\n{doc}")
    return "\n\n".join(parts)



def ask(q):
    docs, metas, dists = retrieve(q)              # ① 检索
    print("\n" + "=" * 60)
    print("问题:", q)
    for d, m in zip(dists, metas):                # 调试信息:这次到底命中了哪几段
        print(f"  命中 [{m['source']} 第{m['para']}段] 距离={d:.4f}")
    context = build_context(docs, metas)          # ② 拼资料
    messages = [                                   # ③ 拼对话
        {"role": "system", "content": RULES},
        {"role": "user",   "content": f"资料：\n{context}\n\n问题：{q}"},
    ]
    resp = ds.chat.completions.create(model="deepseek-chat", messages=messages)   # ④ 问模型
    print("回答:", resp.choices[0].message.content)                                # ⑤ 打印

ask("我奶奶叫什么名字?")
ask("10.14 那天我为什么是零日?")
ask("今天天气怎么样?")