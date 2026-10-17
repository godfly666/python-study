# RAG 代码"作弊条"(照这个写就行,不用背)

> **先说结论:没有人背代码。** 工程师写代码时一直在看文档、看自己以前的代码、看 IDE 补全。
> 你要记住的不是"函数全名",而是**"有哪几步、数据长什么形状"**。这张卡片就是给你照着写的。

---

## 一、四个动作,四个卡片

### 卡片 1:把文本变成向量(embedding)

```python
resp = client.embeddings.create(
    model="embedding-3",
    input="要变成向量的文本",
)
vec = resp.data[0].embedding        # ← 一串 2048 个数字的列表
```

读懂它的意思:**"把 input 这段文字,换成向量"**。
- `input` 可以是**一句话**,也可以是**一串句子**(批量,更快更省)
- `resp.data` 是"一批结果",`[0]` 是第一条,`.embedding` 才是那串数字
- 不用记的东西:`base_url`、`api_key`、参数顺序 —— 抄一次就够

### 卡片 2:建/打开一个库

```python
import chromadb
db  = chromadb.PersistentClient(path="./chroma_db")     # 存到硬盘
col = db.get_or_create_collection(
    name="kefu",
    metadata={"hnsw:space": "cosine"},                  # 用余弦距离
)
```

读懂它:**"打开一个仓库,拿出一排货架"**。
- `PersistentClient` = 存硬盘(关掉程序还在);`Client` = 存内存(关掉就没了)
- `get_or_create` = **有就拿,没有就建**(所以重复运行不会报错)

### 卡片 3:存东西 / 查东西(最核心的一组)

```python
# 存:四样东西一起给
col.upsert(
    ids=["doc0", "doc1"],                       # 身份证(必填,唯一)
    documents=["第一段原文", "第二段原文"],         # 原文(查出来给人看)
    embeddings=[vec0, vec1],                    # 向量(拿来找)
    metadatas=[{"source": "日志.md", "para": 1}, {"source": "日志.md", "para": 2}],  # 标签
)

# 查:给一个向量,要最近的 3 个
res = col.query(query_embeddings=[问题的向量], n_results=3)

res["ids"][0][0]          # 第 1 名的身份证
res["documents"][0][0]    # 第 1 名的原文
res["distances"][0][0]    # 第 1 名的距离(越小越像)
res["metadatas"][0][0]    # 第 1 名的标签
```

**为什么每个结果都有 `[0][0]` 两层?** 因为你可以一次问多个问题 → 外层 `[0]` = "第 0 个问题",内层 `[0]` = "那个问题的第 0 名"。
**只用记住:向量库返回的永远是"一批问题 × 一批结果"。**

### 卡片 4:让大模型开口

```python
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "只能根据资料回答,没有就说没有"},
        {"role": "user",   "content": "资料:\n" + 资料 + "\n\n问题:" + 问题},
    ],
)
answer = resp.choices[0].message.content
```

读懂它:**"把资料和问题一起递过去,拿回一句话"**。
- 对比记忆:向量是 `.data[0].embedding`,对话是 `.choices[0].message.content`
- 流式的差别只有一句:`stream=True`,然后 `for chunk in resp: chunk.choices[0].delta.content`

---

## 二、真正要"理解"的三张图(这个比代码重要)

```
图 1  建库(一次性)
  文件 → 读文字 → 切段 → 每段变向量 → 存进库(带身份证和标签)

图 2  提问(每次)
  问题 → 变向量 → 库里找最近的 3 段 → 拿到【原文】

图 3  回答
  【原文】+ 问题 → 一起塞给大模型 → 带出处的一句话
```

**如果这三张图在你脑子里是清楚的,代码只是把图翻译成英文单词而已。** 忘了哪个单词?查这张卡片。

---

## 三、绝对不用背的清单

| 不用记 | 怎么办 |
|---|---|
| `base_url`、key、模型名 | 抄一次,或者看 `.env` 和这张卡片 |
| 导入路径(`import chromadb`) | 让 IDE 补全,或者看文件开头 |
| 参数顺序 | 用关键字参数(`n_results=3`),顺序就无所谓了 |
| `[0][0]` 到底几层 | 打印出来看一眼(`print(res)`),别猜 |
| 具体函数名(`upsert`/`query`) | 敲 `col.` 看编辑器弹出来的列表,**这就是正常用法** |

## 四、真正要"记住"的只有 5 件事

1. 文本 → 向量,用 embedding 接口(`input` 进,`data[0].embedding` 出)
2. 向量库要四样:身份证 / 原文 / 向量 / 标签
3. 查是**给向量、拿原文**,返回 `[问题序号][排名]`
4. 大模型要 `messages`(system + user),答案是 `choices[0].message.content`
5. 好答案 = 好检索(prompt 只是最后一步)

---

## 五、面试真正会问的(不是背 API)

1. 为什么不能把整篇文档变成一个向量?(分辨率)
2. 切分为什么要重叠?(边界)
3. 检索不准怎么排查?(先看切分 → 再看 embedding 模型 → 再看 top-K / rerank → 最后看 prompt)
4. 怎么防止它编?(prompt 约束 + 距离闸门 + 让它给出处)
5. 怎么评估一个 RAG 做得好不好?(准备一批问题 + 人工判定命中和正确率)

**面试官不会问你 `n_results` 的默认值是几。** 他问的是"你遇到过什么坑、怎么解决的"。

---

## 六、你自己那 25 行(`blank_test.py`)翻译成 6 块白话

> 这份表是给你"重写第二遍"时当地图用的。左边是"要干什么",不是"要写什么"。

| 块 | 在干嘛 | 一句话 | 删了或改错会怎样 |
|---|---|---|---|
| **A 通行证** | 读 `.env`、取 key、建 `client` | "让程序能打电话" | 报 401,电话打不出去 |
| **B 打字机** | `def embed(text)` | "文字 → 2048 个数字" | 没它既不能存也不能查 |
| **C 开柜子** | `PersistentClient(path=...)` + `get_or_create_collection(name=...)` | "找到那个柜子,没有就新建" | path/name 写错 = 打开**别人**的柜子(上次就在里面看见积分和发票) |
| **D 装货** | `docs` + `upsert(ids / documents / embeddings / metadatas)` | "四条船:编号、原文、向量、标签" | `embeddings` 少一个 → `Unequal lengths`;id 每次都换 → 库里堆重复数据 |
| **E 提问** | `q_vec = embed(问题)` + `col.query([q_vec], n_results=2)` | "问题也变成数字,拿去比" | 忘了先 embed(拿文字去比)→ 报错或结果乱 |
| **F 看结果** | `print(res["distances"])` / `print(res["documents"])` | "把找回的原文念出来" | 只看距离不看原文 = 不知道找回来的对不对 |

### 自查法(比看十遍代码有用)

随便挑一块,问自己一句:**"删掉它,程序会怎么坏?"**

- 能答上来 → 这块真长在你脑子里了
- 答不上来 → 这块还是"我的知识",不是"你的"

### 顺带一个真实的清理点

`blank_test.py` 里那行 `v = embed("红烧牛肉面要炖两小时")` 是**测试残渣**,删掉完全不影响程序 —— 留着会让"这块在干嘛"更乱。

