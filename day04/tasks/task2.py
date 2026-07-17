"""🎯 任务二（进阶关，约 15 分钟）：三种方式大对比
要求：
1. 写一个"模拟推理"的活：等 1 秒，返回结果。
2. 分别用**串行**（一个一个来）、**多线程**、**异步**三种方式跑 5 个活。
3. 用 `datetime` 记录每种方式的总耗时，打印出来对比。"""
import threading
import time
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

def simulate_inference(n):
    time.sleep(1)
    return n**5

async def simulate_inference_async(n):
    await asyncio.sleep(1)
    return n**5

test =[1, 2, 3, 4, 5]

#串行
def serial():
    start = datetime.now()
    results = [simulate_inference(n) for n in test]
    end = datetime.now()
    past_time = end - start
    print(f"串行：结果{results}, 耗时{past_time}")

#多线程
import threading
import time
from datetime import datetime


def simulate_inference(n):
    time.sleep(1)
    return n**5


def thread():
    start = datetime.now()
    test = [1, 2, 3, 4, 5]
    results = [None] * len(test)
    def worker(idx, n):
        res = simulate_inference(n)
        results[idx] = res
    threads = []
    for i, n in enumerate(test):
        t = threading.Thread(target=worker,args=(i, n))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    end = datetime.now()
    print(f"多线程：结果 {results}，耗时 {end - start}")

#异步
async def run_async():
    start = datetime.now()
    # 一次性 gather 所有任务，并发执行
    results = await asyncio.gather(*[simulate_inference_async(n) for n in test])
    end = datetime.now()
    print(f"异步：结果 {results}，耗时 {end - start}")

def main():
    serial()
    thread()
    asyncio.run(run_async())

if __name__ == "__main__":
    main()