"""【程序3】
题目：打印出所有的 "水仙花数 "，所谓 "水仙花数 "是指一个三位数，其各位数字立方和等于该数本身。
例如：153是一个 "水仙花数 "，因为153=1的三次方＋5的三次方＋3的三次方。
1.程序分析：利用for循环控制100-999个数，每个数分解出个位，十位，百位。  """

def narcissistic(x):
    a = x // 100
    b = (x // 10) % 10
    c = x % 10
    if a**3 + b**3 + c**3 == x:
        return True
    return False

narcissistics = []
for i in range(100, 999):
    if narcissistic(i):
        narcissistics.append(i)

print("水仙数有：", narcissistics)