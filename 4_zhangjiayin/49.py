"""【程序49】
题目：计算字符串中子串出现的次数  """

def count_substring(s, sub):
    return s.count(sub)

s = input("请输入原字符串: ")
sub = input("请输入子串: ")
print(f"子串出现次数: {count_substring(s, sub)}")