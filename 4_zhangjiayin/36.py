"""【程序36】
题目：有n个整数，使其前面各数顺序向后移m个位置，最后m个数变成最前面的m个数  """

arr = list(map(int, input("输入一个数组").split()))
m = int(input("输入移动位次"))
n = len(arr)

if n > 0:
    m = m%n
    arr = arr[-m:] + arr[:-m]

print(arr)