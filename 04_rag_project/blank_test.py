# ============================================================
# blank_test.py —— 白纸挑战第一遍(2026-10-17)
# 目标:不抄任何旧文件,从零写出"存两条 -> 问一句 -> 找回原文"
# 六个块:A 通行证 / B 打字机 / C 开柜子 / D 装货 / E 提问 / F 看结果
# ============================================================

# ---------- 依赖:需要哪几样工具 ----------
import os                        # 管环境变量:os.environ["名字"] 就是从内存里按名字取东西
from dotenv import load_dotenv   # 把 .env 文件的内容"搬进内存"的函数
import chromadb                  # 向量库本体
from openai import OpenAI        # 客户端类;智谱兼容 OpenAI 协议,所以可以复用它

# ---------- A 通行证:让程序能打电话 ----------
load_dotenv()                    # 必须先跑它,后面 os.environ 才读得到 .env 里的东西(顺序反了就是 KeyError)

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
db = chromadb.PersistentClient(path="./blank_db")        # path 是一个文件夹:换 path = 换一个柜子
col = db.get_or_create_collection(                       # 有就打开,没有就新建
    name="test",                                         # 集合名,相当于一张表;换个 name 就是另一个抽屉
    metadata={"hnsw:space": "cosine"},                   # 声明用余弦距离;漏了默认不是余弦,后面距离数字会对不上
)

# ---------- D 装货:把资料存进柜子 ----------
docs = [
    "关 R4 是把真实文档切成 120 段存进向量库,每段带文件名和段号",
    "红烧牛肉面要先把牛肉炖两小时,再下面前煮面",
]

col.upsert(                                                    # upsert = 按 id 判断:有就覆盖,没有就新增
    ids=["a", "b"],                                            # 身份证:必须是字符串,而且要稳定(真实项目用"文件名+段号")
    documents=docs,                                            # 原文:以后从库里拿回来、喂给大模型的就是它
    embeddings=[embed(docs[0]), embed(docs[1])],               # 向量:几条原文就必须几个向量(数量不等会报 Unequal lengths)
    metadatas=[                                                # 标签:能过滤、能当出处
        {"source": "测试", "para": 1},
        {"source": "测试", "para": 2},
    ],
)

# ---------- E 提问:问题也变成向量,拿去比 ----------
q_vec = embed("我今天把文档切成很多小块存进库了吗?")           # 库只认数字,所以问题也要先过一遍 embed()

res = col.query(
    query_embeddings=[q_vec],      # 两层列表:外层是"一批问题",里层是一个向量(一次可以问好几个)
    n_results=2,                   # 要几段;向量库永远给你这么多,它不会说"我不知道"
)

# ---------- F 看结果:把找回来的原文念出来 ----------
print(res["distances"])            # 距离:越小越像(在 cosine 空间里,距离 = 1 - 相似度)
print(res["documents"])            # 找回的【原文】—— 大模型真正要看的是这个,不是向量
