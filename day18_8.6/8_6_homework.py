import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatOpenAI(model=os.getenv("MODEL_NAME"),
                 api_key=os.getenv("API_KEY"),
                 base_url=os.getenv("BASE_URL"),
                 temperature=0.7)


#===================================定义 **5 个顾问 Chain**：===========================================================
def make_chain(role, prompt_text):
    """快速创建一个顾问 Chain"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"你是{role}专家。回答简洁，控制在100字以内。"),
        ("user", prompt_text)
    ])
    return prompt | llm

#* `destination`: 目的地顾问
#* `budget`: 预算规划师
#* `transportation`: 交通顾问
#* `food`: 美食顾问
#* `culture`: 文化顾问
destination = make_chain("目的地推荐", "推荐去{location}的必去景点和最佳季节：")
budget = make_chain("预算规划", "去{location}玩{days}天，预算{budget}元，给出花费明细：")
transportation = make_chain("交通出行", "去{location}旅游，从国内出发，推荐交通方式和市内出行方案：")
food = make_chain("美食推荐", "推荐{location}的特色美食和必吃餐厅：")
culture = make_chain("文化风俗", "介绍{location}的文化风俗、禁忌和注意事项：")

ADVISORS = {
    "destination": destination,
    "budget": budget,
    "transportation": transportation,
    "food": food,
    "culture": culture,
}

#主管节点分析用户需求，判断需要哪些顾问参与
async def ask_advisor(name: str, **kwargs):
    """调用单个顾问"""
    chain = ADVISORS[name]
    result = await chain.ainvoke(kwargs)
    content = result.content if hasattr(result, "content") else str(result)
    return name, content

async def dispatch(question: str, **kwargs):
    """主管分析问题/分发/汇总"""
    # LLM 分析用哪个顾问
    classify_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""分析用户问题，判断需要哪些顾问。可选：{list(ADVISORS.keys())}。
只返回顾问名称列表，用逗号分隔。如：destination,budget"""),
        ("user", question)
    ])
    chain = classify_prompt | llm
    result = await chain.ainvoke({})
    names = [n.strip() for n in result.content.strip().split(",") if n.strip() in ADVISORS]
    print(f"\n分发决策：{question[:30]}... → {names}")
    # 并发
    tasks = [ask_advisor(name, **kwargs) for name in names]
    results = await asyncio.gather(*tasks)
    return results

async def travel_plan(location: str, days: int, budget: int):
    print(f"\n生成旅行计划：{location} {days}天 ¥{budget}")

    tasks = [ask_advisor(name, location=location, days=days, budget=budget)
             for name in ADVISORS]
    results = await asyncio.gather(*tasks)
    print(f"  {location} {days}天旅行计划（预算¥{budget}）")
    for name, content in results:
        print(f"\n【{name}】")
        print(content)
    return results

async def main():
    print("旅游规划助手")
    print("  单问：'北京有哪些好吃的？'")
    print("  计划：'计划 成都 3天 3000'")
    print("  输入 exit 退出")

    while True:
        user_input = input("\n👤 你: ").strip()
        if user_input.lower() == 'exit':
            break
        if not user_input:
            continue

        if user_input.startswith("计划 "):
            parts = user_input[3:].strip().split()
            if len(parts) >= 3:
                import re
                loc = parts[0]
                days = int(re.sub(r"\D", "", parts[1]))
                money = int(re.sub(r"\D", "", parts[2]))
                await travel_plan(loc, days, money)
            else:
                print("格式：计划 目的地 天数 预算  如：计划 成都 3天 3000")
        else:
            results = await dispatch(user_input, location=user_input[-2:])
            print("\n" + "-" * 30)
            for name, content in results:
                print(f"\n【{name}】{content}")
            print("-" * 30)


if __name__ == "__main__":
    asyncio.run(main())
