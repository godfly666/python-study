import chromadb
import os                        # 管环境变量:os.environ["名字"] 就是从内存里按名字取东西
from dotenv import load_dotenv   # 把 .env 文件的内容"搬进内存"的函数
import chromadb                  # 向量库本体
from openai import OpenAI        # 客户端类;智谱兼容 OpenAI 协议,所以可以复用它


db  = chromadb.PersistentClient(path="./chroma_db_v2")
col = db.get_or_create_collection(name="my_docs", metadata={"hnsw:space": "cosine"})

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
db = chromadb.PersistentClient(path="./chroma_db_v2")        # path 是一个文件夹:换 path = 换一个柜子
col = db.get_or_create_collection(                       # 有就打开,没有就新建
    name="my_docs",                                         # 集合名,相当于一张表;换个 name 就是另一个抽屉
    metadata={"hnsw:space": "cosine"},                   # 声明用余弦距离;漏了默认不是余弦,后面距离数字会对不上
)
# ---------- E 提问:问题也变成向量,拿去比 ----------
questions = [
    "10.14 那天我为什么是零日?",
    "我奶奶叫什么名字?",
    "今天天气怎么样?",
]

for q in questions:
    res = col.query(query_embeddings=[embed(q)], n_results=3)
    print("\n问题:", q)
    for dist, doc in zip(res["distances"][0], res["documents"][0]):
        print(round(dist, 4) ,doc[:40] )
