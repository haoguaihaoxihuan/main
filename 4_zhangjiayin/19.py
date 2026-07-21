"""题目：打印出如下图案（菱形）
*
***
*****
*******
*****
***
*
1.程序分析：先把图形分成两部分来看待，前四行一个规律，后三行一个规律，利用双重for循环，第一层控制行，第二层控制列。  """

for i in range(1,5):
    for j in range(4 - i):
        print(' ',end='')
    for k in range(2 * i - 1):
        print('*',end='')
    print()

for i in range(3, 0 ,-1):
    for j in range(4 - i):
        print(' ',end='')
    for k in range(2 * i - 1):
        print('*',end='')
    print()