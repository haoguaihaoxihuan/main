"""【程序6】
题目：输入两个正整数m和n，求其最大公约数和最小公倍数。
1.程序分析：利用辗除法。  """

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a, b):
    return a // gcd(a, b) * b

try:
    m = int(input("请输入第一个正整数 m: "))
    n = int(input("请输入第二个正整数 n: "))
    if m <= 0 or n <= 0:
        print("请输入正整数！")
    else:
        g = gcd(m, n)
        l = lcm(m, n)
        print(f"{m} 和 {n} 的最大公约数是: {g}")
        print(f"{m} 和 {n} 的最小公倍数是: {l}")
except ValueError:
    print("请输入有效的整数！")