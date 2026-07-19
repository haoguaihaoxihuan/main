"""类名: BaseExam (ABC)
类属性:
  - passing_rate = 0.6  # 及格率（60%）
实例属性:
  - subject_name: str   # 学科名称
  - max_score: float    # 满分值
  - student_name: str   # 学生姓名
  - __score: float      # 私有成绩，默认0
方法:
  - __init__(subject_name, max_score, student_name)
  - get_score() → float
  - input_score(score)                    # 录入成绩，超出满分抛异常
  - set_passing_rate(cls, rate)           # 类方法
  - check_student_name(name) → bool       # 静态方法
  - get_grade(score) → str                # 抽象方法（子类必须实现等级规则）
  - calc_weighted_score(weight) → float   # 计算加权分（如期末占70%）
  - print_report_card()                   # 通用成绩单打印"""

from abc import ABC, abstractmethod

class BaseExam(ABC):
    passing_rate = 0.6  #类属性: - passing_rate = 0.6  # 及格率（60%）

    """实例属性:
  - subject_name: str   # 学科名称
  - max_score: float    # 满分值
  - student_name: str   # 学生姓名
  - __score: float      # 私有成绩，默认0"""

    #  __init__(subject_name, max_score, student_name)
    def __init__(self, subject_name, max_score, student_name):
        self.subject_name = subject_name
        self.max_score = max_score
        self.student_name = student_name
        self.__score = 0.0

    # get_score() → float
    def get_score(self):
        return self.__score

    # input_score(score)  # 录入成绩，超出满分抛异常
    def input_score(self, score):
        if not (0 <= score <= self.max_score):
            raise ValueError(f"成绩 {score} 超出 (0~{self.max_score})范围")
        self.__score = score

    # set_passing_rate(cls, rate)
    @classmethod # 类方法
    def set_passing_rate(cls, rate):
        cls.passing_rate = rate

    # check_student_name(name) → bool
    @staticmethod # 静态方法
    def check_student_name(name):
        return isinstance(name, str) and len(name.strip()) > 0

    # get_grade(score) → str
    @abstractmethod # 抽象方法（子类必须实现等级规则）
    def get_grade(self, score):
        pass

    # calc_weighted_score(weight) → float
    def calc_weighted_score(self, weight):
        return self.__score * weight # 计算加权分（如期末占70%）

    #  - print_report_card()  # 通用成绩单打印
    def print_report_card(self):
        grade = self.get_grade(self.__score)
        print(f"学生：{self.student_name}")
        print(f"满分：{self.max_score}, 分数：{self.__score}")
        print(f"等级：{grade}")
