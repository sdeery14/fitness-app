import os
import contextvars
from contextlib import contextmanager
from typing import Tuple, Optional
from agents import Agent, function_tool
from dotenv import load_dotenv

from db import get_async_engine, init_db
from memory import UserAwareSession

load_dotenv()

# ---- Deterministic session context (never provided by the LLM) ----
_current_session: contextvars.ContextVar[Optional[UserAwareSession]] = contextvars.ContextVar(
    "current_useraware_session", default=None
)

def set_current_session(session: UserAwareSession) -> contextvars.Token[Optional[UserAwareSession]]:
    """Set the current UserAwareSession for tool functions. Returns a token for reset."""
    return _current_session.set(session)

def reset_current_session(token: contextvars.Token[Optional[UserAwareSession]]) -> None:
    """Reset the session context to a previous state using the provided token."""
    _current_session.reset(token)

def get_current_session() -> UserAwareSession:
    """Get the current session or raise if not set.

    Tools call this to ensure the session is deterministic and not LLM-provided.
    """
    session = _current_session.get()
    if session is None:
        raise RuntimeError(
            "No current session set. Set it via set_current_session() or with with_session(...) before running the agent."
        )
    return session

@contextmanager
def with_session(session: UserAwareSession):
    """Context manager to set/reset the current session deterministically."""
    token = set_current_session(session)
    try:
        yield
    finally:
        reset_current_session(token)

@function_tool
async def add_measurement(
    height_cm: int | None = None,
    weight_kg: float | None = None,
    measured_at_iso: str | None = None,
    note: str | None = None,
) -> str:
    """Record a height/weight measurement for the current user.

    measured_at_iso: Optional ISO-8601 timestamp (UTC recommended). Defaults to now.
    """
    from datetime import datetime

    ts = None
    if measured_at_iso:
        ts = datetime.fromisoformat(measured_at_iso)
    session = get_current_session()
    m = await session.add_measurement(
        height_cm=height_cm, weight_kg=weight_kg, measured_at=ts, note=note
    )
    return f"Recorded measurement id={m.id} at {m.measured_at.isoformat()} (height_cm={m.height_cm}, weight_kg={m.weight_kg})"


@function_tool
async def list_measurements(limit: int = 10) -> str:
    """List recent measurements for the current user."""
    session = get_current_session()
    rows = await session.get_measurements(limit=limit)
    if not rows:
        return "No measurements found."
    lines = [
        f"{r.measured_at.isoformat()} - height_cm={r.height_cm}, weight_kg={r.weight_kg}{' - ' + r.note if r.note else ''}"
        for r in rows
    ]
    return "\n".join(lines)

def build_fitness_agent() -> Agent:
    """Create and return the Fitness Agent with tools and instructions configured.

    This function has no side-effects (no network/db), making it safe to import.
    """
    return Agent(
        name="Assistant",
        instructions=(
            """
            You are an AI coach that helps users generate and continually update a personalized fitness plan.

            Use the add_measurement and list_measurements tools to track their height and weight over time.
            """
        ),
        tools=[add_measurement, list_measurements],
    )


async def init_engine_and_session() -> Tuple[object, UserAwareSession]:
    """Initialize the database engine and a user-aware session.

    Returns a tuple of (engine, session). The caller is responsible for driving any
    agent runs and closing resources when appropriate.
    """
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
        label=os.getenv("DEMO_SESSION_LABEL", "Main chat"),
        create_tables=True,  # ensures Agents' own tables are created
        display_name=os.getenv("DEMO_USER_NAME", "Alex"),
        timezone=os.getenv("DEMO_USER_TZ", "UTC"),
    )
    # Ensure user/profile/session rows exist
    await session.init_user()

    return engine, session


# Note: No __main__ execution block here. Use the dedicated demo or evaluation scripts instead.