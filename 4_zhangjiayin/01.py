"""【程序1】
题目：古典问题：有一对兔子，从出生后第3个月起每个月都生一对兔子，小兔子长到第三个月后每个月又生一对兔子，假如兔子都不死，问每个月的兔子总数为多少？
1.程序分析： 兔子的规律为数列1,1,2,3,5,8,13,21....  """

def rabbit(n):
    if n <= 0:
        return []
    elif n == 1:
        return [1]
    elif n == 2:
        return [1, 1]

    # 前两个月都是1
    rabbit = [1, 1] #序列
    for i in range(2, n):
        # 每个月兔子数 = 前两个月之和
        rabbit.append(rabbit[i - 1] + rabbit[i - 2]) #上一个加上上一个
    return rabbit


def main():
    try:
        months = int(input("请输入月份 n (正整数)："))
        if months <= 0:
            print("请输入一个正整数！")
            return
        result = rabbit(months)
        print(f"前 {months} 个月每个月的兔子总对数分别为：")
        for i, count in enumerate(result, start=1):
            print(f"第{i}月：{count} 对", end="  ")
            if i % 10 == 0:
                print()  # 换行
        print()  # 最后再换行
        print(f"第 {months} 个月的兔子总数为：{result[-1]} 对")
    except ValueError:
        print("输入无效，请输入一个整数。")


if __name__ == "__main__":
    main()