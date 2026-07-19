"""1. check_valid_score(score, max_score)  → 校验成绩是否在合法范围（0~满分）
2. calc_percentage(score, max_score)    → 计算得分率 = 分数/满分 × 100%
3. save_record(record_info)             → 使用 with 追加写入 exam_records.txt
4. read_all_records()                   → 使用 with 读取全部成绩记录
5. get_excellent_students(score_dict, threshold)  → 列表推导式筛选达到优秀的学生
6. report_card_generator(student_list)  → 生成器，yield 格式化成绩单字符串
7. input_score_thread_safe(student_name, subject, score)  → 线程锁安全录入成绩
8. multi_thread_input_test()            → 创建2个线程并发录入测试
* `student_records = {}` # 全局共享成绩字典，格式：{"张三": {"语文": 0, "数学": 0}}
* `record_lock = threading.Lock()`"""

import threading
from datetime import datetime

student_records = {}
record_lock = threading.Lock()

#1. check_valid_score(score, max_score)  → 校验成绩是否在合法范围（0~满分）
def check_valid_score(score, max_score):
    return 0 <= score <= max_score

#2. calc_percentage(score, max_score)    → 计算得分率 = 分数/满分 × 100%
def calc_percentage(score, max_score):
    return (score / max_score) * 100

#3. save_record(record_info)  → 使用 with 追加写入 exam_records.txt
def save_record(record_info):
    with open('exam_records.txt', 'a') as f:
        f.write(record_info + "\n")

#4. read_all_records()   → 使用 with 读取全部成绩记录
def read_all_records():
    try:
        with open("exam_records.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except (FileNotFoundError, UnicodeDecodeError):
        return []

#5. get_excellent_students(score_dict, threshold)  → 列表推导式筛选达到优秀的学生
def get_excellent_students(score_dict, threshold):
    return [name for name, score in score_dict.items() if score >= threshold]

#6. report_card_generator(student_list)  → 生成器，yield 格式化成绩单字符串
def report_card_generator(student_list):
    for student in student_list:
        name = student.get("name", "未知")
        chinese = student.get("chinese", "N/A")
        math = student.get("math", "N/A")
        english = student.get("english", "N/A")
        yield f"学生：{name}, 语文：{chinese}, 数学：{math}, 英语：{english}"

#7. input_score_thread_safe(student_name, subject, score)  → 线程锁安全录入成绩
def input_score_thread_safe(student_name, subject, score):
    with record_lock:
        if student_name not in student_records:
            student_records[student_name] = {}
        student_records[student_name][subject] = score
        timestamp = datetime.now().strftime("%Y%m%d %H%M%S")
        record_info = f"{timestamp}, {student_name}, {subject}, {score}"
        save_record(record_info)

#8. multi_thread_input_test()   → 创建2个线程并发录入测试
def multi_thread_input_test():
    def thread_task(name, subject, score):
        input_score_thread_safe(name, subject, score)

    t1 = threading.Thread(target=thread_task, args=("Joy", "英语", 100))
    t2 = threading.Thread(target=thread_task, args=("Sherry", "数学", 99))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("多线程测试")