"""【程序45】
题目：判断一个素数能被几个9整除  """

def func(n):
    for i in range(1, n):
        if (10 ** i - 1) % n == 0:
            print(f"能被 {i} 个9组成的数整除")
            return
    print("未找到")

n = int(input("请输入一个素数: "))
func(n)