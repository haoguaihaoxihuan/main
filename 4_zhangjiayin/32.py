"""程序32】
题目：取一个整数a从右端开始的4～7位。
程序分析：可以这样考虑：
(1)先使a右移4位。
(2)设置一个低4位全为1,其余全为0的数。可用~(~0 < <4)
(3)将上面二者进行&运算。  """

# def extract_bits(a):
#     shifted = a >> 4
#     mask = ~(~0 << 4)
#     result = shifted & mask
#     return result
#
# a = int(input("请输入一个整数a: "))
# result = extract_bits(a)
# print(f"从右端第4～7位 = {result}")

def get_bits_bitwise(a):
    return (a >> 4) & 0xF

def get_bits_slice(a):
    bin_str = bin(a)[2:]
    bin_str = bin_str.zfill(7)
    bits = bin_str[-7 : -3]
    return int(bits, 2)

a = int(input("输入八位数（只由1、0组成）"))
print("原二进制:", bin(a))
print("位运算结果:", get_bits_bitwise(a))
print("切片结果:", get_bits_slice(a))