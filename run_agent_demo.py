import os
import asyncio
from agents import Runner

from app.fitness_agent import build_fitness_agent, init_engine_and_session, with_session


async def main() -> None:
    engine, session = await init_engine_and_session()

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set. Initialized DB and session; skipping agent run.")
        return

    agent = build_fitness_agent()
    # Provide the deterministic session to tools via contextvar
    with with_session(session):
        result = await Runner.run(agent, "Hello!", session=session)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
