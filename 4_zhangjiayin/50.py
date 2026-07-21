"""【程序50】
题目：有五个学生，每个学生有3门课的成绩，从键盘输入以上数据（包括学生号，姓名，三门课成绩），计算出平均成绩，
况原有的数据和计算出的平均分数存放在磁盘文件 "stud "中。"""


def main():
    with open("stud.txt", "w", encoding="utf-8") as f:
        f.write("学号\t姓名\t成绩1\t成绩2\t成绩3\t平均分\n")

        for i in range(5):
            print(f"\n请输入第 {i + 1} 个学生的信息：")
            stu_id = input("学号: ")
            name = input("姓名: ")
            scores = []
            for j in range(1, 4):
                score = float(input(f"成绩{j}: "))
                scores.append(score)
            avg = sum(scores) / 3

            line = f"{stu_id}\t{name}\t{scores[0]}\t{scores[1]}\t{scores[2]}\t{avg:.2f}\n"
            f.write(line)

    print("\n所有数据已写入 stud.txt 文件。")


if __name__ == "__main__":
    main()