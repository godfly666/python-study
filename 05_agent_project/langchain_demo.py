import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="deepseek-chat",
                 api_key=os.environ["DEEPSEEK_API_KEY"],
                 base_url="https://api.deepseek.com",
                 temperature=1.2)
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个简洁的中文助手。"),
    ("user", "{q}"),
])
chain = prompt | llm | StrOutputParser()          # 管道:提示词 → 模型 → 取文本
print(chain.invoke({"q": "给我的 AI 知识库项目起 5 个中文名字,每个不超过 5 个字"}))