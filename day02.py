import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ==================== 1. 模型层 ====================
class AIModel:
    #父类`AIModel`：含 name、model_type
    
    def __init__(self, name, model_type):
        self.name = name
        self.model_type = model_type

    def predict(self, input_data):
        #`predict`抛出`NotImplementedError`
        raise NotImplementedError("子类必须实现 predict 方法")


class TextModel(AIModel):
    def predict(self, input_data):
        print(f"[{self.name}] 正在推理文本：{input_data}")
        #`TextModel`子类：推理休眠 1s
        time.sleep(1)    
        #返回推理结果与耗时                  
        return f"{input_data}的文本推理结果"


class ImageModel(AIModel):
    def predict(self, input_data):
        print(f"[{self.name}] 正在识别图像：{input_data}")
        #`ImageModel`子类：推理休眠 2s
        time.sleep(2)                 
        #返回识别结果与耗时     
        return f"{input_data} 的图像识别结果"


class AudioModel(AIModel):
    #新增语音模型 AudioModel，扩充任务列表
    def predict(self, input_data):
        print(f"[{self.name}] 正在转录音频：{input_data}")
        time.sleep(1.5)
        return f"音频转录结果：{input_data}"


# ==================== 2. 调度器 Scheduler ====================
class Scheduler:
#任务记录表`records`、线程锁`lock`
    def __init__(self):
        self.records = []              
        self.lock = threading.Lock()   # 线程锁

    #`_run_one`：执行单任务
    def _run_one(self, user_name, model, input_data):
        start = datetime.now()
        result = model.predict(input_data)
        end = datetime.now()
        cost = (end - start).total_seconds()

        # 加锁写入记录
        with self.lock:   
            self.records.append({
                "user": user_name,
                "model": model.name,
                "cost": cost,
                "result": result
            })

    def run_serial(self, tasks):
        #串行依次执行所有任务
        for task in tasks:
            self._run_one(*task)

    def run_concurrent(self, tasks):
        #多线程并发执行
        threads = []
        for task in tasks:
            t = threading.Thread(target=self._run_one, args=task)
            threads.append(t)
            #start+join 等待全部结束
            t.start()
        for t in threads:
            t.join()


    def report(self):
        #格式化打印每条任务详情
        lines = []
        lines.append("\n========== 任务 ==========")
        for idx, r in enumerate(self.records, 1):
            line = (f"任务{idx}: {r['user']} -> {r['model']}, 耗时 {r['cost']:.2f} 秒, 结果: {r['result']}")
            lines.append(line)
            print(line)
        lines.append(f"共 {len(self.records)} 条记录")
        print(lines[-1])
        return "\n".join(lines)


# ==================== 3. 主程序 ====================
def main():
    # 创建模型实例
    text_model = TextModel("DeepSeek", "文本生成")
    image_model = ImageModel("Canva", "图像分类")
    audio_model = AudioModel("Yin Pin AI", "音频转录")

    # 创建文本、图像模型，构造≥6 条混合用户任务
    tasks = [
        ("Max", text_model, "完成作业"),
        ("Joy", image_model, "joy.jpg"),
        ("Sherry", audio_model, "唱歌.mp3"),
        ("Jessie", text_model, "我要减肥"),
        ("Annie", image_model, "drawing.png"),
        ("Cecily", audio_model, "王者荣耀.mp3"),
        ("Hellary", text_model, "123456")
        ]

    # 运行串行
    scheduler_serial = Scheduler()
    start_serial = datetime.now()
    scheduler_serial.run_serial(tasks)
    end_serial = datetime.now()
    total_serial = (end_serial - start_serial).total_seconds()

    # 运行并发
    scheduler_concurrent = Scheduler()
    start_concurrent = datetime.now()
    scheduler_concurrent.run_concurrent(tasks)
    end_concurrent = datetime.now()
    total_concurrent = (end_concurrent - start_concurrent).total_seconds()

    # 输出对比报表
    print("\n" + "="*50)
    #串行总耗时
    print(f"串行总耗时: {total_serial:.2f} 秒") 
    #并发总耗时
    print(f"并发总耗时: {total_concurrent:.2f} 秒")

    save_time = total_serial - total_concurrent
    #节省时长
    print(f"节省时长: {save_time:.2f} 秒")
    if total_concurrent > 0:
        speedup = total_serial / total_concurrent
        #加速比
        print(f"加速比: {speedup:.2f}x")
    else:
        print("加速比: N/A")
    #当前系统时间
    print(f"当前系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


    # 打印并收集明细（来自并发调度器，因为我们要看并发执行的明细）
    report_text = scheduler_concurrent.report()

    # 将性能报表写入 report.txt
    with open("report.txt", "w", encoding="utf-8") as f:
        f.write("AI 推理任务性能报表\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"串行总耗时: {total_serial:.2f} 秒\n")
        f.write(f"并发总耗时: {total_concurrent:.2f} 秒\n")
        f.write(f"节省时长: {save_time:.2f} 秒\n")
        f.write(f"加速比: {speedup:.2f}x\n")
        f.write("\n--- 明细记录 ---\n")
        f.write(report_text)

    print("\n性能报表已写入 report.txt")


if __name__ == "__main__":
    main()

#ThreadPoolExecutor 实现线程池版本没搞起......