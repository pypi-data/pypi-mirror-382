import asyncio

from langgraph.checkpoint.memory import MemorySaver
from rich import print
from universal_mcp.agentr.registry import AgentrRegistry

from universal_mcp.agents.codeact.agent import CodeActAgent
from universal_mcp.agents.utils import messages_to_list


async def main():
    memory = MemorySaver()
    agent = CodeActAgent(
        name="CodeAct Agent",
        instructions="Be very concise in your answers.",
        model="anthropic:claude-4-sonnet-20250514",
        tools={"google_mail": ["list_messages"]},
        registry=AgentrRegistry(),
        memory=memory,
    )
    print("Starting agent...")
    # await agent.ainit()
    # await agent.run_interactive()
    # async for event in agent.stream(
    #     user_input="Fetch unsubscribe links from my Gmail inbox for promo emails I have received in the last 7 days"
    # ):
    #     print(event.content, end="")
    result = await agent.invoke(user_input="Get the 50th fibonacci number")
    print(messages_to_list(result["messages"]))


if __name__ == "__main__":
    asyncio.run(main())
