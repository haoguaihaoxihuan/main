"""【程序24】
题目：给一个不多于5位的正整数，要求：一、求它是几位数，二、逆序打印出各位数字。  """

def main():
    s = input("请输入一个不多于5位的正整数：")
    if not s.isdigit():
        print("请输入数字！")
        return
    n = int(s)
    if n <= 0 or n > 99999:
        print("请输入1~5位的正整数！")
        return
    print(f"位数：{len(s)}")  
    print(f"逆序打印：{s[::-1]}")

if __name__ == "__main__":
    main()