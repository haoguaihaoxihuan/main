"""【程序14】
题目：输入某年某月某日，判断这一天是这一年的第几天？
1.程序分析：以3月5日为例，应该先把前两个月的加起来，然后再加上5天即本年的第几天，特殊情况，
闰年且输入月份大于3时需考虑多加一天。  """

def is_leap(year):
    return (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0)

def dates(year, month, day):
    monthes = [31, 28, 31 , 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total = sum(monthes[:month - 1]) + day

    if is_leap(year) and month > 2:
        total = total + 1
    return total

y = int(input("请输入年"))
m = int(input("请输入月"))
d = int(input("请输入日"))
print(f"{y}年{m}月{d}日是这一年的第{dates(y, m, d)}天")
