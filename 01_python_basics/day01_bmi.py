# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


def hello_world():
    name = input("你叫什么名字？")
    print("老兵你好" + name + "!今天是你转行的第1天")
def weight():
    weight=float(input("请输入你的体重"))
    height=float(input("请输入你的身高"))/100
    bmi=weight/height**2
    print("你的体重指数是",bmi)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    weight()




# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
