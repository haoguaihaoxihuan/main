"""【程序5】
题目：利用条件运算符的嵌套来完成此题：学习成绩> =90分的同学用A表示，60-89分之间的用B表示，60分以下的用C表示。
1.程序分析：(a> b)?a:b这是条件运算符的基本例子。  """

def score_level(score):
    if 0 <= score <= 100:
        grade = 'A' if score >= 90 else ('B' if score >= 60 else 'C')
        print(grade)
    else:
        print("输入有效成绩(0-100)")

score = float(input("输入成绩(0-100):"))
score_level(score)