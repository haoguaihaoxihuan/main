import asyncio
from datetime import datetime

class AIModel:
    async def predict(self, input_data):
        raise NotImplementedError

class TextModel(AIModel):
    async def predict(self, input_data):
        await asyncio.sleep(1)
        return f"文本结果:{input_data}"

class ImageModel(AIModel):
    async def predict(self, input_data):
        await asyncio.sleep(2)
        return f"图像结果:{input_data}"

async def user_request(user, model, input_data):
    start = datetime.now()
    result = await model.predict(input_data)
    end = datetime.now()
    cost = (end - start).total_seconds()
    return {
        "user": user,
        "model": model.__class__.__name__,
        "cost": cost,
        "result": result
    }

# ---------- 主函数 ----------
async def main():
    text_model = TextModel()
    image_model = ImageModel()

    tasks = [
        user_request("Joy", text_model, "20050216"),
        user_request("Sherry", text_model, "20050813"),
        user_request("Jessie", image_model, "健身.jpg"),
        user_request("Annie", image_model, "dpc.jpg")
    ]

    start_all = datetime.now()
    results = await asyncio.gather(*tasks)
    end_all = datetime.now()
    total_cost = (end_all - start_all).total_seconds()

    for res in results:
        print(f"用户 {res['user']}模型（{res['model']}）耗时 {res['cost']:.2f}s，结果：{res['result']}")

    print(f"总耗时：{total_cost:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())