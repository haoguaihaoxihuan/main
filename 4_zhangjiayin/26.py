"""【程序26】
题目：请输入星期几的第一个字母来判断一下是星期几，如果第一个字母一样，则继续   判断第二个字母。
1.程序分析：用情况语句比较好，如果第一个字母一样，则判断用情况语句或if语句判断第二个字母。  """

def func():
    first = input("输入第一个字母：")
    if first == "M" or first == "m":
        print("Monday")
    elif first == "T" or first == "t":
        second = input("请输入第二个字母：")
        if second == "u" or second == "U":
            print("Tuesday")
        elif second == "h" or second == "H":
            print("Thursday")
        else:
            print("输入正确字母！")
    elif first =="w" or first == "W":
        print("Wednesday")
    elif first =="F" or first == "f":
        print("Friday")
    elif first == "s" or first == "S":
        second = input("请输入第二个字母：")
        if second == "u" or second == "U":
            print("Sunday")
        elif second == "a" or second == "A":
            print("Saturday")
        else:
            print("输入正确字母！")
    else:
        print("输入正确字母！")

func()