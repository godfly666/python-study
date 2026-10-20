# python-study —— 从零到 AI 应用开发的通关仓库

> 一个 25 岁退伍后、用 3 个月转行 AI 应用开发的实操仓库。
> 这里没有抄来的教程代码,只有我一关一关敲出来、跑通、推上来的东西。

## 🎯 这个仓库是什么

2026 年 10 月起,我用"闯关制"自学 Python → FastAPI → 大模型应用开发:每过一关就推一次代码,
三个月内的目标是**做出两个能公网访问的 AI 项目**,进 AI 应用开发岗。

规则很简单:**10 分钟做得出来 = 过关;做不出来 = 花 30 分钟补齐再重做。** 会就是会,不磨洋工。

## 📁 目录结构(按阶段分类)

```
study/
├── 01_python_basics/              # 阶段 A:Python 基础六关
│   ├── day01_bmi.py               #   关 1:BMI 计算器(输入 / 类型转换 / 格式化)
│   ├── day02_guess_number.py      #   关 2–3:猜数字 + 99 乘法表(if/while/for/列表/字典)
│   ├── day03_contacts.py          #   关 4:通讯录存档版(JSON 文件读写、数据持久化)
│   ├── day04_bookkeeping.py       #   关 6:记账本 CLI(JSON 存档 + 余额计算 + 日期)
│   ├── contacts.json              #   通讯录数据
│   └── records.json               #   账本数据
│
├── 02_fastapi/                    # 阶段 B:FastAPI 后端三关
│   ├── f1_example.py              #   FastAPI 最小示例(路径参数 / 查询参数 / Query 校验)
│   ├── bmi_api.py                 #   BMI 接口(两个接口 + 参数校验 + 健康评价)
│   ├── todo_api.py                #   Todo REST API(完整增删改查 + 404 + SQLAlchemy ORM → SQLite)
│   └── di_demo.py                 #   依赖注入(Depends)入门
│
├── 03_ai_agent/                   # 阶段 C:大模型应用
│   ├── deepseek_api.py            #   第一个大模型调用(密钥走 .env,不进代码)
│   ├── chat_v2.py                 #   多轮对话 + 流式输出(messages 攒上下文记忆)
│   ├── tool_demo.py               #   function calling:模型负责决策、代码负责执行
│   ├── no_tool.py                 #   对照组实验:不给工具时模型会算错(幻觉)
│   └── mini_agent.py              #   命令行 AI 助手:多轮工具循环 + 笔记落盘
│
├── 04_rag_project/                # 阶段 E:项目一 RAG 知识库(已公网上线)
│   ├── rag_step1.py               #   R1:文本 → 向量(智谱 embedding-3,2048 维)
│   ├── rag_step2.py               #   R2:手写余弦相似度,看语义远近
│   ├── rag_step3.py               #   R3:Chroma 向量库入库 + 语义检索
│   ├── rag_step4.py               #   R4:真实文档切分入库(109 段,metadata 记来源与段号)
│   ├── rag_step5.py               #   R5:检索 → 拼资料 → 大模型生成带来源的回答
│   ├── rag_api.py                 #   R6:FastAPI 服务(/ask 提问、/upload 上传文档)
│   ├── static/index.html          #   R7:网页界面(输入框 + 回答 + 出处列表)
│   ├── blank_test.py              #   白纸挑战:关掉所有参考,从零重写一遍最小 RAG
│   ├── rag-cheatsheet.md          #   自己总结的 RAG 速查卡(数据流图 + 代码骨架)
│   └── chroma_db*/                #   向量库目录(运行时生成,已忽略)
│
├── git-cheatsheet.md              # 自己踩坑总结的 Git 速查表(报错对照 + 收工五步)
├── .env                           # 密钥(已被 .gitignore 忽略,永不提交)
└── README.md
```

> 关 5(SQL)是在牛客网手写刷题(要求 10 题,实际做了 20 题),没有代码文件。

## 🌐 在线演示(项目一已上线)

**公网地址:** <https://432a1f4f.r15.vip.cpolar.cn>

> 免费版内网穿透,**重启隧道后地址会变**;随时可以自己起一个(下面两行命令)。

问它三个问题,能立刻看出它做对了什么:

| 你问 | 它应该答 | 说明 |
|---|---|---|
| 我的猫叫什么名字? | 咪咪 | 从上传的文档里检索到并回答 |
| 我奶奶叫什么名字? | 该问题不在文库中。 | 资料里没有就认输,不编 |
| 10.14 那天我为什么是零日? | 引用 `[转行日志.md 第N段]` | 从 109 段真实文档里定位,并给出出处 |

**自己起一份(两个终端,各开一个):**

```bash
# 终端 A:起服务(演示时不要加 --reload)
cd 04_rag_project
..\..\.venv\Scripts\python.exe -m uvicorn rag_api:app --port 8000

# 终端 B:起隧道(把本地 8000 搬到公网 https)
cpolar http 8000
```

**原理一句话:uvicorn 是货,cpolar 是快递员 —— 货不在,快递员送到的是空箱子。**
两个窗口缺一不可,演示完 `Ctrl+C` 关掉隧道。

### 验收清单(项目一的 Definition of Done)

| # | 验收项 | 怎么验 | 状态 |
|---|---|---|---|
| 1 | 公网可访问 | 手机 4G 打开链接能出页面 | ✅ |
| 2 | 能提问并得到回答 | 问"我的猫叫什么名字?" → 答"咪咪" | ✅ |
| 3 | 答案带出处 | 回答下方列出 `[文件名 第N段]`,**由后端从 metadata 直接返回,不让模型自己写** | ✅ |
| 4 | 不知道会说不知道 | 问"我奶奶叫什么名字?" → "该问题不在文库中。"且不列出处 | ✅ |
| 5 | 能上传自己的文档 | 传一个 `.md` / `.txt` → 后端切分入库 → 立刻能检索到 | ✅ |
| 6 | 2 分钟演示视频 | 待录 | ⬜ |

> 为什么要"后端给出处":正文是模型生成的,段号却是元数据。
> **让模型去引元数据,等于让它自己给自己作证** —— 它会编一个看起来很像的段号。所以出处由程序从 `metadatas` 直接返回。

## 🚀 怎么跑起来

> 统一用项目自带的虚拟环境解释器:
> `C:\Users\l1809\PycharmProjects\WelcomeScreen\.venv\Scripts\python.exe`

**阶段 A · 基础脚本**

```bash
cd 01_python_basics
python day01_bmi.py
```

**阶段 B · 后端接口**

```bash
cd 02_fastapi
..\..\.venv\Scripts\python.exe -m uvicorn bmi_api:app --reload     # BMI 接口
..\..\.venv\Scripts\python.exe -m uvicorn todo_api:app --reload    # Todo 接口
```

浏览器打开 <http://127.0.0.1:8000/docs> —— Swagger UI 会列出所有接口,可以直接点 "Try it out" 调用。
它是 FastAPI **读代码里的路由和类型标注自动生成**的,不是官网提供的;改完代码刷新页面,文档跟着变。

**阶段 C · 命令行 AI 助手**

```bash
cd 03_ai_agent
..\..\.venv\Scripts\python.exe mini_agent.py
```

支持多轮对话(有上下文记忆)、调用工具(查时间 / 计算 / 写笔记),`exit` 退出。

**阶段 E · RAG 检索与问答**

```bash
cd 04_rag_project
..\..\.venv\Scripts\python.exe rag_step1.py       # 看一个句子如何变成 2048 个数字
..\..\.venv\Scripts\python.exe rag_step2.py       # 手算余弦相似度
..\..\.venv\Scripts\python.exe rag_step3.py       # 向量库入库 + 语义检索
..\..\.venv\Scripts\python.exe rag_step4.py       # 把真实文档切成 109 段入库(带来源)
..\..\.venv\Scripts\python.exe rag_step5.py       # 检索 + 生成带来源的回答
..\..\.venv\Scripts\python.exe -m uvicorn rag_api:app --port 8000   # 起服务(网页在 http://127.0.0.1:8000)
```

⚠️ **必须在文件所在目录运行。** 脚本里的 `todos.db`、`notes.txt`、`./chroma_db` 都是**相对当前目录**的 ——
换个目录启动会新建一份空数据,看起来就像"我的数据丢了"。

## 🔐 密钥怎么处理

**代码里从不出现明文密钥。** 统一放在根目录的 `.env`(已被 `.gitignore` 忽略),运行时读环境变量:

```python
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
```

```
# .env(不提交、不分享)
DEEPSEEK_API_KEY=sk-你的key
ZHIPU_API_KEY=你的key
```

`python-dotenv` 会从**脚本所在目录逐级往上**找 `.env`,所以四个子目录里的脚本都能读到根目录这一份。

> 教训(真的踩过):密钥一旦推进 GitHub,**删文件也没用 —— Git 历史是永久的**;唯一的补救是
> **立刻去平台作废、重新签发**。提交前用 `git grep -n "sk-"` 自查一遍。

## 🧱 用到的技术

Python · FastAPI · Pydantic · SQLAlchemy · SQLite · OpenAI SDK(DeepSeek / 智谱兼容)
· 流式输出(stream)· Function Calling · Agent 循环(模型 + 工具 + 循环)
· Embedding(智谱 `embedding-3`,2048 维)· 余弦相似度 · Chroma 向量库(持久化 + metadata 过滤)
· 前端原生 JS(fetch / AbortController 超时 / 错误可见化)· 内网穿透(cpolar)

## 📌 阶段进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| A | Python 基础六关(计算器 / 猜数字 / 乘法表 / 通讯录 / SQL / 记账本 + Git) | ✅ 10.11 |
| B | FastAPI 后端三关(BMI API / Todo API / 整理并推送) | ✅ 10.12 |
| C | 大模型应用(对话 / 流式 / 多轮记忆 / 工具调用 / 命令行 Agent) | ✅ 10.15 |
| E | 项目一:**RAG 知识库**(切分入库 → 检索 → 生成 → 上传 → 网页 → **公网可访问**) | ✅ 10.20 已上线 |
| F | 项目二:多工具 Agent + 简历 | ⏳ |

---

*记录每一步,比记住每一步更重要。*
