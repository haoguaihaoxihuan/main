"""1. 基础得分率计算测试
2. 成绩保存与读取测试
3. 多线程录入测试
4. 设置及格率为 0.65
5. 语文测试（创建、录入成绩、查看作文分、评定等级、保存记录）
6. 数学测试（创建、录入成绩、设置附加分、查看加权分、保存记录）
7. 英语测试（创建、录入成绩、打印分项成绩单、评定等级、保存记录）
8. 优秀学生筛选测试（用字典 + 列表推导式）
9. 成绩单生成器测试
10. 批量统计多态测试（3门学科各1份答卷，遍历调用 calc_weighted_score）"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from subjects import ChineseExam, MathExam, EnglishExam, BaseExam
import grade_utils as gu


def main():
    print("学生成绩管理系统测试")

    # 1. 基础得分率计算测试
    print("\n1. 基础得分率计算测试")
    score = 120
    max_score = 150
    rate = gu.calc_percentage(score, max_score)
    print(f"满分 {max_score}，得分 {score}，得分率：{rate:.2f}%")

    # 2. 成绩保存与读取测试
    print("\n2. 成绩保存与读取测试")
    gu.save_record("2026-05-20 13:14:00, Joy, 英语, 150, 优秀")
    gu.save_record("2026-05-21 12:22:00, Sherry, 数学, 130, 良好")
    records = gu.read_all_records()
    print("已读取：")
    for r in records:
        print("  " + r)

    # 3. 多线程录入测试
    print("\n3. 多线程录入测试")
    gu.multi_thread_input_test()
    print("当前全局成绩字典：", gu.student_records)

    # 4. 设置及格率为 0.65
    print("\n4. 设置及格率为 0.65")
    BaseExam.set_passing_rate(0.65)
    print(f"当前及格率：{BaseExam.passing_rate}")

    # 5. 语文测试
    print("\n5. 语文测试")
    chinese = ChineseExam("Jessie", essay_score=45)
    try:
        chinese.input_score(135)
    except ValueError as e:
        print(f"录入失败：{e}")
    else:
        print(f"语文成绩：{chinese.get_score()}")
        print(f"作文分：{chinese.essay_score}")
        grade = chinese.get_grade(chinese.get_score())
        print(f"等级：{grade}")
        gu.save_record(f"2026-12-22 10:01:00, Hailiry, 语文, {chinese.get_score()}, {grade}")

    # 6. 数学测试
    print("\n6. 数学测试")
    math = MathExam("A")
    try:
        math.input_score(145)
    except ValueError as e:
        print(f"录入失败：{e}")
    else:
        math.set_bonus_points(5)
        print(f"数学成绩：{math.get_score()}")
        print(f"附加分：{math.get_bonus_points()}")
        # 计算加权分（假设期末占70%）
        weighted = math.calc_weighted_score(0.7)
        print(f"加权分（70%）：{weighted}")
        grade = math.get_grade(math.get_score())
        print(f"等级：{grade}")
        gu.save_record(f"2026-07-19 10:15:00, A, 数学, {math.get_score()}, {grade}")

    # 7. 英语测试
    print("\n7. 英语测试")
    english = EnglishExam("B")
    try:
        english.input_score(88)
    except ValueError as e:
        print(f"录入失败：{e}")
    else:
        english.print_report_card()
        grade = english.get_grade(english.get_score())
        print(f"等级：{grade}")
        gu.save_record(f"2026-07-18 10:01:00, B, 英语, {english.get_score()}, {grade}")

    # 8. 优秀学生筛选测试（用字典 + 列表推导式）
    print("\n8. 优秀学生筛选测试（语文≥135）")
    score_dict = {"C": 135, "A": 145, "B": 88, "D": 138}
    threshold = 135
    excellent = gu.get_excellent_students(score_dict, threshold)
    print(f"优秀学生名单（≥{threshold}）：{excellent}")

    # 9. 成绩单生成器测试
    print("\n9. 成绩单生成器测试")
    students_data = [
        {"name": "C", "chinese": 135, "math": 145, "english": 88},
        {"name": "A", "chinese": 120, "math": 140, "english": 92},
        {"name": "B", "chinese": 90, "math": 95, "english": 60},
    ]
    gen = gu.report_card_generator(students_data)
    for report in gen:
        print(report)

    # 10. 批量统计多态测试（3门学科各1份答卷，遍历调用 calc_weighted_score）
    print("\n10. 批量统计多态测试（加权分，权重0.6）")
    exams = [
        ChineseExam("Joy", essay_score=50),
        MathExam("Sherry"),
        EnglishExam("Jessie")
    ]
    # 录入成绩
    exams[0].input_score(130)
    exams[1].input_score(135)
    exams[1].set_bonus_points(3)
    exams[2].input_score(76)

    for exam in exams:
        weighted = exam.calc_weighted_score(0.6)
        print(f"{exam.subject_name} 加权分（0.6）：{weighted}")

    print("\n所有测试完成。")


if __name__ == "__main__":
    main()