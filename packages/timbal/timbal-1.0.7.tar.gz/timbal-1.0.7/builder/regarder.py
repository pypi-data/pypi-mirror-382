import asyncio

from timbal import Agent
from timbal.tools import WebSearch
from timbal.platform.kbs.tables import search_table

from dotenv import load_dotenv

load_dotenv()


# async def get_makes():
#     await asyncio.sleep(0.1)
#     return "Toyota, Honda, Nissan"


# SYSTEM_PROMPT = r"These are your car makes: {::get_makes}"


def get_datetime():
    from datetime import datetime
    return datetime.now()


agent = Agent(
    name="test",
    model="openai/gpt-4.1-mini",
    tools=[WebSearch(), get_datetime],
    # system_prompt=SYSTEM_PROMPT
)


async def main():
    while True:
        prompt = input("User: ")
        if prompt == "q":
            break
        await agent(prompt=prompt).collect()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
