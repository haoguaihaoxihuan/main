"""【程序25】
题目：一个5位数，判断它是不是回文数。即12321是回文数，个位与万位相同，十位与千位相同。  """

def palindromic():
    s = input("输入一个五位数")
    n = int(s)
    if not (s.isdigit() and len(s) == 5):
        print("请输入5位的正整数！")
        return
    s.isdigit()
    if s[::-1] == s:
        print("是回文数")
    else:
        print("不是回文数")

palindromic()