"""【程序47】
题目：读取7个数（1—50）的整数值，每读取一个值，程序打印出该值个数的＊。  """

for _ in range(7):
    while True:
        n = int(input("请输入1-50的整数: "))
        if 1 <= n <= 50:
            break
        print("输入无效，请重新输入")
    print('*' * n)
    