"""【程序35】
题目：输入数组，最大的与第一个元素交换，最小的与最后一个元素交换，输出数组。  """

def swap(arr):
    max_idx = arr.index(max(arr))
    arr[max_idx], arr[0] = arr[0], arr[max_idx]
    min_idx = arr.index(min(arr))
    arr[min_idx], arr[-1] = arr[-1], arr[min_idx]
    return arr

arr = list(map(int, input("输入一个数组").split()))
print(swap(arr))