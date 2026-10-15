# python-study —— 从零到 AI 应用开发的通关仓库

> 一个 25 岁退伍后、用 3 个月转行 AI 应用开发的实操仓库。
> 这里没有抄来的教程代码,只有我一关一关敲出来、跑通、推上来的东西。

## 🎯 这个仓库是什么

2026 年 10 月起,我用"闯关制"自学 Python → FastAPI → 大模型应用开发:每过一关就推一次代码,
三个月内的目标是**做出两个能公网访问的 AI 项目**,进 AI 应用开发岗。

## 📁 目录结构

```
study/
├── study_day1.py        # 关 1:BMI 计算器(Python 基础:输入 / 类型转换 / 格式化)
├── study_day02.py       # 关 2–3:猜数字 + 99 乘法表 + 通讯录
├── study_day03.py       # 关 4:通讯录存档版(JSON 读写持久化)
├── study-day04.py       # 关 6:记账本 CLI(JSON 存档 + 余额计算)
└── api/                 # 阶段 B/C:后端接口 + 大模型应用
    ├── f1_example.py    # FastAPI 最小示例(路径参数 / 查询参数 / Query 校验)
    ├── bmi_api.py       # BMI 接口(两个接口 + 参数校验 + 健康评价)
    ├── todo_api.py      # Todo REST API(完整增删改查 + 404 + SQLAlchemy ORM → SQLite)
    ├── deepseek_api.py  # 第一个大模型接口调用(密钥走 .env,不进代码)
    ├── chat_v2.py       # 多轮对话 + 流式输出(messages 攒上下文记忆)
    ├── tool_demo.py     # function calling:模型负责决策、代码负责执行
    ├── no_tool.py       # 对照组实验:不给工具时模型会算错(幻觉)
    └── mini_agent.py    # 命令行 AI 助手:多轮工具循环 + 笔记落盘
```

## 🚀 怎么跑起来

### 1. 后端接口(FastAPI)

```bash
cd api
python -m uvicorn bmi_api:app --reload      # BMI 接口
python -m uvicorn todo_api:app --reload     # Todo 接口
```

浏览器打开 <http://127.0.0.1:8000/docs> —— Swagger UI 会列出所有接口,可以直接点 "Try it out" 调用。
它是 FastAPI **读代码里的路由和类型标注自动生成**的,不是官网提供的,改完代码刷新页面文档就跟着变。

### 2. 命令行 AI 助手

```bash
cd api
python mini_agent.py
```

支持多轮对话(有上下文记忆)、调用工具(查时间 / 计算 / 写笔记),`exit` 退出。

## 🔐 密钥怎么处理

**代码里从不出现明文密钥。** 统一放在 `.env`(已被 `.gitignore` 忽略),运行时读取环境变量:

```python
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
```

```
# .env(不提交、不分享)
DEEPSEEK_API_KEY=sk-你的key
```

## 🧱 用到的技术

Python · FastAPI · Pydantic · SQLAlchemy · SQLite · OpenAI SDK(DeepSeek 兼容)
· 流式输出(stream)· Function Calling · Agent 循环(模型 + 工具 + 循环)

## 📌 阶段进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| A | Python 基础六关(计算器 / 猜数字 / 乘法表 / 通讯录 / SQL / 记账本 + Git) | ✅ |
| B | FastAPI 后端三关(BMI API / Todo API / 整理并推送) | ✅ |
| C | 大模型应用(对话 / 流式 / 多轮记忆 / 工具调用 / 命令行 Agent) | ✅ |
| E | 项目一:**RAG 企业知识库**(公网可访问) | 🚧 进行中 |
| F | 项目二:多工具 Agent + 简历 | ⏳ |

---

*记录每一步,比记住每一步更重要。*
