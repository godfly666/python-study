import os, json, datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

# ── 真正干活的本地函数 ──
def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression: str):
    allowed = "0123456789+-*/(). "
    if not all(c in allowed for c in expression):
        return "表达式含非法字符"
    return str(eval(expression))          # ← 已经白名单校验过,所以敢用

# ── 工具的"说明书"(写给模型看的,不是给你看的)──
tools = [
    {"type": "function", "function": {
        "name": "get_current_time",
        "description": "获取当前的日期和时间。用户问现在几点、今天几号时必须调用。",
        "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {
        "name": "calculate",
        "description": "计算数学表达式,如 12345*6789。需要精确计算时必须调用。",
        "parameters": {"type": "object", "properties": {
            "expression": {"type": "string", "description": "要计算的表达式"}},
            "required": ["expression"]}}},
]

messages = [{"role": "user", "content": "现在几点了?顺便算一下 12345 * 6789"}]

# 第 1 次请求:带上工具说明书
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,                 # 空①:tools
)
msg = resp.choices[0].message
print("模型第一次说话:", msg.content)
print("模型要求的工具调用:", msg.tool_calls)      # 空②:tool_calls

# 把模型的"求助"先存进历史
messages.append(msg)

# 它可能要调用多个工具 → 循环执行
for tc in msg.tool_calls:
    name = tc.function.name
    args = json.loads(tc.function.arguments or "{}")   # 空③:arguments
    result = get_current_time() if name == "get_current_time" else calculate(**args)
    print(f"→ 我执行了 {name} → {result}")
    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})  # 空④:tool 空⑤:id

# 第 2 次请求:把工具结果带上,换最终回答
final = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=tools)
print("最终回答:", final.choices[0].message.content)
