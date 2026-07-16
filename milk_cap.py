# goods/milk_cap.py - 奶盖茶子类
# 继承BaseDrink，实现奶盖茶专属优惠：购买2杯及以上立减3元

import sys
import os
from platform import system

from goods.base_drink import BaseDrink

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MilkCapTea(BaseDrink):
    def __init__(self, name: str, price: float, milk_cap_cost: float = 0):
        super().__init__(name, price)
        # 实例属性，__milk_cap_cost
        self.__milk_cap_cost = milk_cap_cost
        self.type = "奶盖茶"

    def get_final_price(self, buy_num: int) -> float:
        origin = self.price * buy_num * self.shop_discount
        if buy_num >= 2:
            final = origin - 3
            return round(final, 2)
        else:
            return round(origin, 2)

# get_milk_cap_cost()   -->获取奶盖的单杯价格
    def get_milk_cap_cost(self):
        return self.__milk_cap_cost

#测试代码
if __name__ == "__main__":
    milk_cap = MilkCapTea("奶盖绿茶", 12, milk_cap_cost=3)
    MilkCapTea.set_shop_discount(0.9)
    print(f"购买1杯：{milk_cap.get_final_price(1)}")
    print(f"购买2杯：{milk_cap.get_final_price(2)}")
    print(f"购买3杯：{milk_cap.get_final_price(3)}")
    print(milk_cap.sell(2))
    print(f"当前库存：{milk_cap.get_stock()}")