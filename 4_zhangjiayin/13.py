"""【程序13】
题目：一个整数，它加上100后是一个完全平方数，再加上168又是一个完全平方数，请问该数是多少？
1.程序分析：在10万以内判断，先将该数加上100后再开方，再将该数加上168后再开方，如果开方后的结果满足如下条件，即是结果。
请看具体分析：  """

import math

def find_number(limit=100000):
    results = []
    for n in range(limit + 1):
        a = math.isqrt(n + 100)  
        if a * a == n + 100:
            b = math.isqrt(n + 268)
            if b * b == n + 268:
                results.append(n)
    return results

nums = find_number()
print("满足条件的数有：", nums)