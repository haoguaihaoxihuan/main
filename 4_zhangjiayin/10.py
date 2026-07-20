"""【程序10】
题目：一球从100米高度自由落下，每次落地后反跳回原高度的一半；
再落下，求它在   第10次落地时，共经过多少米？第10次反弹多高？  """

def bounce(h0, times):
    total = 0          # 总路程
    height = h0        # 当前下落高度（初始为 100）
    for i in range(1, times + 1):
        # 第 i 次落地：先下落 height 米
        total += height
        # 如果不是最后一次落地，则反弹并再次下落
        if i < times:
            height /= 2            # 反弹高度 = 当前高度的一半
            total += 2 * height    # 上升 height 米 + 再次下落 height 米
        else:
            # 第 times 次落地后的反弹高度（不计入总路程）
            bounce_height = height / 2
    return total, bounce_height

h0 = 100
times = 10
total, bounce_h = bounce(h0, times)
print(f"第{times}次落地时共经过 {total} 米")
print(f"第{times}次反弹高度为 {bounce_h} 米")