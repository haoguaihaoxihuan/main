"""【程序44】
题目：一个偶数总能表示为两个素数之和。  """

def isprime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

def even(n):
    for i in range(2, n//2 + 1):
        if isprime(i) and isprime(n - i):
            return i, n - i
    return None

n = int(input("输入一个大于二的偶数"))
print(even(n))