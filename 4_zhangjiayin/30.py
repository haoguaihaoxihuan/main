"""【程序30】
题目：有一个已经排好序的数组。现输入一个数，要求按原来的规律将它插入数组中。
1.程序分析：首先判断此数是否大于最后一个数，然后再考虑插入中间的数的情况，插入后此元素之后的数，依次后移一个位置。"""

def insert_sorted(arr, num):
    pos = 0
    while pos < len(arr) and arr[pos] < num:
        pos += 1
    arr.append(0)
    for i in range(len(arr) - 1, pos, -1):
        arr[i] = arr[i - 1]
    arr[pos] = num
    return arr

arr = list(map(int, input("请输入从小到大的数组: ").split()))
num = int(input("请输入要插入的数: "))

result = insert_sorted(arr, num)
print("插入后的数组:", result)