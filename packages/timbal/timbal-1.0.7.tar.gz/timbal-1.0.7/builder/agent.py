from dotenv import load_dotenv
from timbal import Agent
from timbal.tools import Read, Bash, Write, Edit, WebSearch

load_dotenv()


with open("SYSTEM_PROMPT", "r") as f:
    SYSTEM_PROMPT = f.read()


agent = Agent(
    name="eve",
    model="anthropic/claude-sonnet-4-5",
    tools=[Read(), Bash("*"), Write(), Edit(), WebSearch()],
    system_prompt=SYSTEM_PROMPT,
    model_params={
        "max_tokens": 32768,
    }
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
