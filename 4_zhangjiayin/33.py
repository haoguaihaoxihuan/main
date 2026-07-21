"""【程序33】
题目：打印出杨辉三角形（要求打印出10行如下图）
1.程序分析：
          1
        1   1
      1   2   1
    1   3   3   1
  1   4   6   4   1
1   5   10   10   5   1  """

n = 6

def yanghui_triangle(n):
    triangle = []
    for i in range(n):
        row = [1] * (i+1)
        for j in range(1, i):
            row[j] = triangle[i-1][j-1] + triangle[i-1][j]
        triangle.append(row)
    return triangle

triangle = yanghui_triangle(n)

for row in triangle:
    print(' '.join(map(str, row)).center(40))