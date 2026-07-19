"""类名: EnglishExam
等级规则:
  - ≥90优秀，≥75良好，≥60及格，<60不及格
重写方法:
  - print_report_card()  # 打印"听力/阅读/写作分项成绩"标语"""

from .base_exam import BaseExam

class EnglishExam(BaseExam):
    def __init__(self, student_name):
        super().__init__("英语", 100.0, student_name)

    #等级规则: ≥90优秀，≥75良好，≥60及格，<60不及格
    def get_grade(self, score):
        if score >= 90:
            return "优秀"
        elif score >= 75:
            return "良好"
        elif score >= 60:
            return "及格"
        else:
            return "不及格"

    # print_report_card()  # 打印"听力/阅读/写作分项成绩"标语
    def print_report_card(self):
        print("听力/阅读/写作分项成绩")
        super().print_report_card()