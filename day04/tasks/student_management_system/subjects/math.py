"""类名: MathExam
私有属性:
  - __bonus_points = 0  # 附加分
配套方法:
  - get_bonus_points()  # getter
  - set_bonus_points(points)  # setter
等级规则:
  - ≥140优秀，≥120良好，≥90及格，<90不及格
重写方法:
  - calc_weighted_score(weight)  # 数学加权分计算包含附加分"""

from .base_exam import BaseExam

class MathExam(BaseExam):
    def __init__(self, student_name):
        super().__init__("数学", 150.0, student_name)
        self.__bonus_points = 0  # 私有属性: __bonus_points = 0  # 附加分

    # 配套方法 get_bonus_points()  # getter
    def get_bonus_points(self):
        return self.__bonus_points

    #配套方法 set_bonus_points(points)  # setter
    def set_bonus_points(self, points):
        if points < 0:
            raise ValueError("附加分不能小于0")
        self.__bonus_points = points

    #等级规则：≥140优秀，≥120良好，≥90及格，<90不及格
    def get_grade(self, score):
        if score >= 140:
            return "优秀"
        elif score >= 120:
            return "良好"
        elif score >= 90:
            return "及格"
        else:
            return "不及格"

    #重写方法： calc_weighted_score(weight)  # 数学加权分计算包含附加分
    def calc_weighted_score(self, weight):
        base = super().calc_weighted_score(weight)
        return base + self.__bonus_points