import json
from datetime import datetime

records = []  # 账本记录(列表)

def save():
    with open("records.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)

def Records():
    # 启动时读档:防两种坏——文件不存在 / 文件内容是坏的(比如空的)
    global records
    try:
        with open("records.json", "r", encoding="utf-8") as f:
            records = json.load(f)
    except FileNotFoundError:
        records = []
    except json.JSONDecodeError:
        records = []

    while True:
        menu = """===== 我的记账本 =====
1. 记一笔
2. 看流水
3. 看余额
4. 退出
"""
        print(menu)
        choice = input("请选择:")

        if choice == "1":
            # 记一笔:类型 + 金额 + 备注 + 自动记日期
            kind = input("收入还是支出：")
            amount = float(input("金额："))
            note = input("备注：")
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            records.append({"date": now, "type": kind, "amount": amount, "note": note})
            save()

        elif choice == "2":
            # 看流水
            if len(records) == 0:
                print("还没有任何记录")
            else:
                print("日期 | 类型 | 金额 | 备注")
                for r in records:
                    print(f"{r['date']} | {r['type']} | {r['amount']} | {r['note']}")

        elif choice == "3":
            # 看余额:收入总和 - 支出总和
            account = 0
            if len(records) == 0:
                print("还没有任何记录")
            else:
                for r in records:
                    if r['type'] == "收入":
                        account += float(r['amount'])
                    elif r['type'] == "支出":
                        account -= float(r['amount'])
                print(f"当前余额:{account}")

        elif choice == "4":
            print("再见!")
            break

        else:
            print("输入有误,重新选")

if __name__ == '__main__':
    Records()
