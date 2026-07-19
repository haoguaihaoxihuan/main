"""类名: ChineseExam
独有属性:
  - essay_score: float  # 作文分（满分60）
等级规则:
  - ≥135优秀，≥120良好，≥90及格，<90不及格"""

from .base_exam import BaseExam

class ChineseExam(BaseExam):
    def __init__(self, student_name, essay_score=0.0):
        super().__init__("语文", 150.0, student_name)
        #  独有属性 - essay_score: float  # 作文分（满分60）
        self.essay_score = essay_score


    def get_grade(self, score):
        if score >= 135:
            return "优秀"
        elif score >= 120:
            return "良好"
        elif score >= 90:
            return "及格"
        else:
            return "不及格"