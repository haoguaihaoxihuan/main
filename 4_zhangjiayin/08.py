"""【程序8】
题目：求s=a+aa+aaa+aaaa+aa...a的值，其中a是一个数字。
例如2+22+222+2222+22222(此时共有5个数相加)，几个数相加有键盘控制。
1.程序分析：关键是计算出每一项的值。  """

def calculate(x, y):
    total = 0
    term = 0
    for i in range(x):
        term = term * 10 + y
        total += term
    return total

x = int(input("请输入数字 x (1-9): "))
y = int(input("请输入项数 y: "))
result = calculate(x, y)
print(f"和为: {result}")