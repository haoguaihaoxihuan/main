"""【程序40】
题目：字符串排序。  """


a = input("请输入第一个字符串: ")
b = input("请输入第二个字符串: ")
c = input("请输入第三个字符串: ")

if a > b:
    a, b = b, a
if a > c:
    a, c = c, a
if b > c:
    b, c = c, b

print("排序后:", a, b, c)