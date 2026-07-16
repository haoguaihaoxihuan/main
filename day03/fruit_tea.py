# goods/fruit_tea.py - 果茶子类
# 继承BaseDrink，实现果茶专属优惠：全场折扣基础上额外95折
import sys
import os

from goods.base_drink import BaseDrink


class FruitTea(BaseDrink):
    def __init__(self, name: str, price: float):
        super().__init__(name, price)
        self.type = "果茶"

    def get_final_price(self, buy_num: int) -> float:
        """计算咖啡的最终价格"""
        origin = self.price * buy_num
        final = origin * self.shop_discount * 0.95
        print("=====")
        return round(final, 2)

#重写打印小票方法：显示果茶专属优惠信息
    def print_ticket(self, buy_num: int):
        total = self.get_final_price(buy_num)
        print(f"饮品：{self.name}，数量：{buy_num}，总价：{total}（果茶专属95折）")

#测试代码
if __name__ == "__main__":
    fruit_tea = FruitTea("棒打鲜橙", 5)
    fruit_tea.print_ticket(2)
    print(fruit_tea.get_final_price(2))
