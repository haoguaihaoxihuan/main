"""【程序48】
题目：某个公司采用公用电话传递数据，数据是四位的整数，在传递过程中是加密的，加密规则如下：
每位数字都加上5,然后用和除以10的余数代替该数字，再将第一位和第四位交换，第二位和第三位交换。  """

def func(n):
    s = str(n)
    digits = []
    for i in range(4):
        digit = (int(s[i]) + 5) % 10
        digits.append(digit)
    digits[0], digits[3] = digits[3], digits[0]
    digits[1], digits[2] = digits[2], digits[1]
    return int(''.join(map(str, digits)))

n = int(input("输入四位数"))
print(func(n))