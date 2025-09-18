import os
import asyncio
from agents import Agent, Runner
from dotenv import load_dotenv

from db import get_async_engine, init_db
from memory import UserAwareSession

load_dotenv()


async def main() -> None:
    # Create DB engine (requires DATABASE_URL pointing to Postgres; no SQLite fallback)
    engine = get_async_engine()
    await init_db(engine)  # create our user/profile tables

    # Create session bound to a specific app user and session id
    external_user_id = os.getenv("DEMO_USER_ID", "user_123")
    session_id = os.getenv("DEMO_SESSION_ID", "fitness_chat")

    session = UserAwareSession.for_user(
        external_user_id=external_user_id,
        session_id=session_id,
        engine=engine,
        label="Main chat",
        create_tables=True,  # ensures Agents' own tables are created
        display_name=os.getenv("DEMO_USER_NAME", "Alex"),
        timezone=os.getenv("DEMO_USER_TZ", "UTC"),
    )

    # Ensure user/profile/session rows exist
    await session.init_user()

    # Only run the agent if an OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set. Skipping agent run after initializing session.")
        return

    agent = Agent(name="Assistant", instructions="Be concise and helpful.")
    result = await Runner.run(agent, "Hello!", session=session)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())