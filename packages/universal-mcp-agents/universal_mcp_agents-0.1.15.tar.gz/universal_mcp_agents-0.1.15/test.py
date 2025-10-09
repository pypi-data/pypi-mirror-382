import asyncio
import time

from loguru import logger

from universal_mcp.agents import get_agent


async def main():
    agent_cls = get_agent("simple")
    start_time = time.time()
    agent = agent_cls(
        name="Simple Agent",
        instructions="You are a simple agent that can answer questions.",
        model="anthropic/claude-sonnet-4-20250514",
    )
    logger.info(f"Time building agent taken: {time.time() - start_time} seconds")
    await agent.ainit()
    logger.info(f"Time initializing agent taken: {time.time() - start_time} seconds")
    result = await agent.invoke(user_input="What is the capital of France?")
    logger.info(f"Time invoking agent taken: {time.time() - start_time} seconds")


if __name__ == "__main__":
    asyncio.run(main())
