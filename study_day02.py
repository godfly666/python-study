import random


def gassnuber():
    nub=int(random.randint(1,100))
    count: int=0

    while True:
        guessnub = int(input("猜一个整数字1-100"))
        count+=1
        if nub==guessnub:
            print(f"恭喜,你用了 {count} 次猜对")
            break
        elif nub>guessnub:
            print("猜小了")
        else:
            print("猜大了")

def chengfa():
    for i in range(1, 10):  # 外层:i 依次 = 1, 2, 3
        for j in range(1, i+1):  # 内层:j 依次 = 1, 2, 3
            print(f"{i}*{j}={i*j}",end="\t")
        print()
def Contacts():
    # 存:把整个 accounts 塞进文件
    contacts = []  # 空通讯录(列表)

    while True:
        found = False  # 每轮先归零:上一轮找到过,不代表这一轮也能找到
        print("\n1 添加  2 删除  3 查找  4 修改  5 退出")
        choice = input("请选择:")

        if choice == "1":
            # 添加
            name=input("姓名：")
            phone=input("电话：")
            contacts.append({"name":name,"phone":phone})
            pass
        elif choice == "2":
            # 删除

            removename=input("你要删除谁")
            for i in contacts:
                if i["name"] == removename:
                    contacts.remove(i)
                    found=True
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
                    found=True
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