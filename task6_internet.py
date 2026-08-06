import asyncio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    client = MultiServerMCPClient({
        "internet": {
            "command": "python", "args": ["server_internet_try.py"], "transport": "stdio"
        }
    })
    tools = await client.get_tools()
    print(f"✅ 已连接 {len(tools)} 个工具：{[t.name for t in tools]}")

    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL"),
        temperature=0
    )
    agent = create_agent(llm, tools)

    print("🌐 万能查询助手已上线！(输入 exit 退出)")
    messages = []
    while True:
        user_input = input("\n👤 你: ")
        if user_input.lower() == 'exit':
            break
        if not user_input.strip():
            continue
        messages.append({"role": "user", "content": user_input})
        response = await agent.ainvoke({"messages": messages})
        ai_reply = response['messages'][-1].content
        print(f"🤖 助手: {ai_reply}")
        messages.append({"role": "assistant", "content": ai_reply})

if __name__ == "__main__":
    asyncio.run(main())
