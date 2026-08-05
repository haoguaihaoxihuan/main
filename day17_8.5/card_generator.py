# ============================================================
# 第1步：导入依赖
# ============================================================
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv


# ============================================================
# 第2步：加载环境变量 & 初始化模型
# ============================================================
load_dotenv()                                       # 使用 `load_dotenv()` 读取环境变量

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME")

# temperature` 设为 `0.3`（让输出稍微有点创意，但又不太离谱）
LLM = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0.3
)


# ============================================================
# 第3步：生成自我介绍（ChatPromptTemplate + LCEL管道 + StrOutputParser）
# ============================================================
def generate_intro(name, job, skills):
    # 创建对话消息模板
    intro_prompt = ChatPromptTemplate.from_messages([
        #system设定身份，human传入需求
        ("system", "你是一个专业的人力资源顾问，擅长帮人写简洁有力的自我介绍。"),
        #human` 角色：请根据以下信息，帮我写一段 50 字以内的自我介绍。姓名：`{name}`，职位：`{job}`，技能：`{skills}`
        ("human", "请根据以下信息，帮我写一段50字以内的自我介绍。\n姓名：{name}\n职位：{job}\n技能：{skills}")
    ])
    #用 LCEL 语法组装：`chain = prompt | llm | StrOutputParser()`
    chain = intro_prompt | LLM | StrOutputParser()
    # 调用 `chain.invoke()` 生成自我介绍
    result = chain.invoke({"name": name, "job": job, "skills": skills})
    # 打印结果，并验证返回类型是 `str`
    print(f"自我介绍（类型：{type(result).__name__}）：{result}")
    return result


# ============================================================
# 第4步：生成个人slogan（使用PromptTemplate）
# ============================================================
def generate_slogan(name, job):
    # 创建一个纯文本模板，内容如："请根据以下信息，生成一句 15 字以内的个人 slogan，要求朗朗上口。姓名：`{name}`，职位：`{job}`"
    slogan_prompt = PromptTemplate.from_template(
        "请根据以下信息，生成一句15字以内的个人slogan，要求朗朗上口。\n姓名：{name}\n职位：{job}"
    )
    # 调用模型生成 slogan
    prompt_text = slogan_prompt.format(name=name, job=job)
    # 把提示词发给大模型
    response = LLM.invoke(prompt_text)
    result = response.content
    print(f"个人slogan：{result}")
    return result


# ============================================================
# 第5步：生成结构化名片数据（JsonOutputParser）
# ============================================================
"""定义一个 Pydantic 类 `Card`，包含以下字段：
* `name`：姓名（字符串）
* `job`：职位（字符串）
* `intro`：自我介绍（字符串）
* `slogan`：个人 slogan（字符串）
* `skills`：技能列表（字符串数组）"""
class Card(BaseModel):
    name: str = Field(description="姓名")
    job: str = Field(description="职位")
    intro: str = Field(description="自我介绍")
    slogan: str = Field(description="个人slogan")
    skills: list[str] = Field(description="技能列表")


def generate_card(name, job, skills):
    #创建 `JsonOutputParser(pydantic_object=Card)`
    parser = JsonOutputParser(pydantic_object=Card)
    card_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个数据整理助手。请根据输入信息生成一张名片。\n{format_instructions}"),
        ("human", "姓名：{name}\n职位：{job}\n技能：{skills}")
    ])
    #使用 `parser.get_format_instructions()` 作为 system 提示词
    card_prompt = card_prompt.partial(format_instructions=parser.get_format_instructions())
    # 调用模型生成结构化名片数据
    chain = card_prompt | LLM | parser
    result = chain.invoke({"name": name, "job": job, "skills": skills})
    # 打印解析后的字典结果
    print(f" 结构化名片数据（类型：{type(result).__name__}）：")
    for key, value in result.items():
        print(f"  {key}: {value}")
    return result


# ============================================================
# 第6步：完整运行
# ============================================================
if __name__ == "__main__":
    # 测试数据：`name="张三"`，`job="Python 开发工程师"`，`skills="Python, LangChain, FastAPI"`
    name = "张三"
    job = "Python 开发工程师"
    skills = "Python, LangChain, FastAPI"

    # 第3步
    intro = generate_intro(name, job, skills)
    print()

    # 第4步
    slogan = generate_slogan(name, job)
    print()

    # 第5步
    card_data = generate_card(name, job, skills)
    print()

    # 最终打印一张完整的"名片"，格式如下：
    print(f"姓名：{name}")
    print(f"职位：{job}")
    print(f"自我介绍：{card_data.get('intro', intro)}")
    print(f"个人slogan：{card_data.get('slogan', slogan)}")
    print(f"技能：{skills}")
