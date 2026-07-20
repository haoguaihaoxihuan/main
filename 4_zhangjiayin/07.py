"""【程序7】
题目：输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。
1.程序分析：利用while语句,条件为输入的字符不为 '\n '.  """

def characters(string):
    letter = space = num = other = 0
    i = 0
    while i < len(string):
        if ('a' <= string[i] <= 'z' or 'A' <= string[i] <= 'Z'):
            letter += 1
        elif '0' <= string[i] <= '9':
            num += 1
        elif string[i] == ' ':
            space += 1
        else:
            other += 1
        i += 1
    return letter, space, num, other

line = input("请输入一行字符: ")
l, sp, d, o = characters(line)
print(f"英文字母: {l}, 空格: {sp}, 数字: {d}, 其他: {o}")
