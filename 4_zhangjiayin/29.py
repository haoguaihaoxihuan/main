"""【程序29】
题目：求一个3*3矩阵对角线元素之和
1.程序分析：利用双重for循环控制输入二维数组，再将a累加后输出。  """

matrix = []
for i in range(3):
    row = list(map(int, input(f"请输入第{i+1}行的三个数：").split()))
    matrix.append(row)

sum = 0
for i in range(3):
    sum += matrix[i][i]
    if i != 3 - 1 - i:  # 避免中心重复
        sum += matrix[i][3 - 1 - i]

print("对角线之和：", sum)