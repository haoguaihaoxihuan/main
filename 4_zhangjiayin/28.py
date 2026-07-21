"""程序28】
题目：对10个数进行排序
1.程序分析：可以利用选择法，即从后9个比较过程中，选择一个最小的与第一个元素交换，
下次类推，即用第二个元素与后8个进行比较，并进行交换。  """

def sort(arr):
    n = len(arr)
    for i in range(n-1):
        min = i
        for j in range(i+1, n):
            if arr[j] < arr[min]:
                min = j
        arr[i], arr[min] = arr[min], arr[i]
    return arr

nums = []
for _ in range(10):
    nums.append(float(input("输入一个数:")))
sorted = sort(nums)
print(sorted)