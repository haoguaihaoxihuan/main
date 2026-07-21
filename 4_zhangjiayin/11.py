"""【程序11】
题目：有1、2、3、4个数字，能组成多少个互不相同且无重复数字的三位数？都是多少？
1.程序分析：可填在百位、十位、个位的数字都是1、2、3、4。组成所有的排列后再去掉不满足条件的排列。  """

count = 0
number = []

for a in range(1, 5):
    for b in range(1, 5):
        for c in range(1, 5):
            if a != b and a != c and b != c:
                num = a * 100 + b * 10 + c
                number.append(num)
                count += 1

print(count)
print(number)