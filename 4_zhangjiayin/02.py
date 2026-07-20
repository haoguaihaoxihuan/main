"""【程序2】
题目：判断101-200之间有多少个素数，并输出所有素数。
1.程序分析：判断素数的方法：用一个数分别去除2到sqrt(这个数)，如果能被整除，
则表明此数不是素数，反之是素数。"""

def check_prime(x):
    if x < 2:
        return False
    for i in range(2, x):
        if x % i == 0:
            return False
    return True

primes = []
for i in range(101, 200):
    if check_prime(i):
        primes.append(i)

print("素数总个数", len(primes))
print("素数有:", primes)