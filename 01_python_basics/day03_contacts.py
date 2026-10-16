import json

accounts = []  # 空通讯录(列表)

def save():
    with open("contacts.json", "w", encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False)
def Contacts():
    # 存:把整个 accounts 塞进文件
    global accounts
    try:
        with open("contacts.json", "r", encoding="utf-8") as f:
            contacts = json.load(f)      # 把文件里的通讯录读回来
    except FileNotFoundError:
        contacts = []                    # 第一次运行没有文件,从空开始


    while True:
        found = False
        print("\n1 添加  2 删除  3 查找  4 修改  5 退出")
        choice = input("请选择:")

        if choice == "1":
            # 添加
            name=input("姓名：")
            phone=input("电话：")
            contacts.append({"name":name,"phone":phone})
            save()

            pass
        elif choice == "2":
            # 删除

            removename=input("你要删除谁")
            for i in contacts:
                if i["name"] == removename:
                    contacts.remove(i)
                    found=True
                    save()
                    print("删除完成")
                    break
            if not found:
                    print("查无此人")
            pass
        elif choice == "3":
            # 查找
            find=input("你找谁")
            for i in contacts:
                if i["name"]==find :
                    print(find+"他的电话是"+i["phone"])
                    found=True
                    break
            if not found:
                    print("查无此人")
            pass
        elif choice == "4":
            # 修改
            find = input("你修改谁的电话")
            for i in contacts:
                if i["name"] == find:
                    i["phone"]=input("新电话：")
                    print(find + "已修改，他的电话是" + i["phone"])
                    save()
                    found=True
                    break
            if not found:
                print("查无此人")
            pass
        elif choice == "5":
            print("再见!")
            break
        else:
            print("输入有误,重新选")
if __name__ == '__main__':
    Contacts()