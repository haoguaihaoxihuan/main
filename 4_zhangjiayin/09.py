"""【程序9】
题目：一个数如果恰好等于它的因子之和，这个数就称为 "完数 "。例如6=1＋2＋3.编程   找出1000以内的所有完数。  """

def perfect_numbers(limit=1000):
    result = []
    for num in range(2, limit + 1):
        factors_sum = 0
        for i in range(1, num // 2 + 1):
            if num % i == 0:
                factors_sum += i
        if factors_sum == num:
            result.append(num)
    return result

perfect_nums = perfect_numbers(1000)
print("1000以内的完数有：", perfect_nums)
print("个数：", len(perfect_nums))
