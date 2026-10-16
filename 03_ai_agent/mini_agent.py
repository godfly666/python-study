import os, json, datetime


from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression: str):
    allowed = "0123456789+-*/(). "
    if not all(c in allowed for c in expression):
        return "表达式含非法字符"
    return str(eval(expression))

# ── ③ 你来写:把 content 追加写入 notes.txt,返回一句"已保存"的具体描述(含总条数)──
def save_note(content: str):
    with open("notes.txt", "a", encoding="utf-8") as f:     # a = 追加,不是覆盖
        f.write(content + "\n")                            # 纯文本,自己加换行
    with open("notes.txt", "r", encoding="utf-8") as f:    # 再读一遍用来数条数
        count = sum(1 for line in f if line.strip())        # 非空行 = 笔记条数
    return f"已保存到 notes.txt(当前共 {count} 条笔记)"

# ── ④ 你来写:把 save_note 的"说明书"加进这个列表(照前两个的样子写,参数名 content)──
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
    {"type": "function", "function": {
        "name": "save_note",
        "description": "把一条笔记追加保存到本地 notes.txt。当用户要求记住某事、记笔记时必须调用。",
        "parameters": {"type": "object", "properties": {
            "content": {"type": "string", "description": "要记录的笔记内容"}},
                       "required": ["content"]}}},
]


messages = [{"role": "system", "content": "你是一个严谨的助手:凡涉及时间或计算,必须先调用工具,不许自己猜。"}]

while True:
    user_input = input("\n你: ")
    if user_input.strip().lower() in ("exit", "quit"):     # ← 空①:这里该写什么?
        break
    messages.append({"role": "user", "content": user_input})

    # ── 内层循环:反复"问模型 → 执行工具",直到它不再要工具 ──
    while True:
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=tools)
        msg = resp.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:            # ②:它没要工具,说明这轮结束了
            print(f"\n助手: {msg.content}")
            break

        for tc in msg.tool_calls:         # ③:遍历它要的每个工具
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            # ── 我要你自己写这段"按名字找函数"的分发 ──
            if name == "get_current_time":
                result = get_current_time()
            elif name == "calculate":
                result = calculate(**args)
            elif name == "save_note":
                result = save_note(**args)  # 和上面 calculate 一模一样的形式
            else:
                result = f"没有名为 {name} 的工具"          # ← 防御:模型可能编出一个不存在的工具名
            print(f"  [工具] {name}({args}) → {result}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})