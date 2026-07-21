"""【程序37】
题目：有n个人围成一圈，顺序排号。从第一个人开始报数（从1到3报数），凡报到3的人退出圈子，问最后留下的是原来第几号的那位。"""

def func(n):
    arr = list(range(1, n+1))
    index = 0
    while len(arr)>1:
        index = (index + 2) % len(arr)
        arr.pop(index)
    return arr

n = int(input("人数: "))
print(f"最后留下的是 {func(n)} 号")