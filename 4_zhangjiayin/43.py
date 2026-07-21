"""【程序43】
题目：求0—7所能组成的奇数个数。"""

total = 0

for n in range(1, 9):
    if n == 1:
        count = 4
    elif n == 2:
        count = 4 * 6
    else:
        count = 4 * 6 * 6
        remaining = 5
        for i in range(n - 3):
            count *= remaining
            remaining -= 1

    total += count

print(f"0-7能组成的奇数个数: {total}")