"""【程序31】
题目：将一个数组逆序输出。
1.程序分析：用第一个与最后一个交换。"""

def exchange(arr):
    left = 0
    right = len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1
    return arr

arr = list(map(int, input("请输入数组").split()))
print("逆序：", exchange(arr))