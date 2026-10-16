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
├── 04_rag_project/                # 阶段 E:项目一 RAG 企业知识库(进行中)
│   ├── rag_step1.py               #   R1:文本 → 向量(智谱 embedding-3,2048 维)
│   ├── rag_step2.py               #   R2:手写余弦相似度,看语义远近
│   └── rag_step3.py               #   R3:Chroma 向量库入库 + 语义检索
│
├── .env                           # 密钥(已被 .gitignore 忽略,永不提交)
└── README.md
```

> 关 5(SQL)是在牛客网手写刷题(要求 10 题,实际做了 20 题),没有代码文件。

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

**阶段 E · RAG 向量检索**

```bash
cd 04_rag_project
..\..\.venv\Scripts\python.exe rag_step1.py       # 看一个句子如何变成 2048 个数字
..\..\.venv\Scripts\python.exe rag_step2.py       # 手算余弦相似度
..\..\.venv\Scripts\python.exe rag_step3.py       # 向量库入库 + 语义检索
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

Python · FastAPI · Pydantic · SQLAlchemy · SQLite · OpenAI SDK(DeepSeek 兼容)
· 流式输出(stream)· Function Calling · Agent 循环(模型 + 工具 + 循环)
· Embedding(智谱 `embedding-3`)· 余弦相似度 · Chroma 向量库

## 📌 阶段进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| A | Python 基础六关(计算器 / 猜数字 / 乘法表 / 通讯录 / SQL / 记账本 + Git) | ✅ 10.11 |
| B | FastAPI 后端三关(BMI API / Todo API / 整理并推送) | ✅ 10.12 |
| C | 大模型应用(对话 / 流式 / 多轮记忆 / 工具调用 / 命令行 Agent) | ✅ 10.15 |
| E | 项目一:**RAG 企业知识库**(公网可访问)—— R1 向量 / R2 余弦 / R3 Chroma 检索 | 🚧 进行中(10.16) |
| F | 项目二:多工具 Agent + 简历 | ⏳ |

---

*记录每一步,比记住每一步更重要。*
