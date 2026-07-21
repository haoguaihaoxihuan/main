"""【程序34】
题目：输入3个数a,b,c，按大小顺序输出。
1.程序分析：利用指针方法。  """

a = float(input("输入第一个数"))
b = float(input("输入第二个数"))
c = float(input("输入第三个数"))

if a > b:
    a, b = b, a
if b > c:
    b, c = c, b
if c > a:
    a,c = c,a

print(a, b, c)
print(c, b, a)