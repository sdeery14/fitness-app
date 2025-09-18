import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from sqlalchemy.exc import InvalidRequestError
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Base(DeclarativeBase):
    pass


def _coerce_to_async_url(url: str) -> str:
    """Ensure SQLAlchemy URL uses an async driver when targeting Postgres.

    If user provides postgresql:// or postgres://, switch to postgresql+asyncpg://
    """
    lowered = url.lower()
    if lowered.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.split("://", 1)[1]
    if lowered.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.split("://", 1)[1]
    if lowered.startswith("postgresql+psycopg2://"):
        return "postgresql+asyncpg://" + url.split("://", 1)[1]
    return url


def get_database_url() -> str:
    """Return the required Postgres DATABASE_URL from the environment.

    Raises a clear exception if missing or not Postgres. No SQLite fallback.
    """
    raw = os.getenv("DATABASE_URL")
    if not raw:
        raise RuntimeError(
            "DATABASE_URL is not set. Please define it in your .env (e.g., postgresql+asyncpg://user:pass@host:5432/dbname)."
        )
    coerced = _coerce_to_async_url(raw)
    lowered = coerced.lower()
    if not lowered.startswith("postgresql+asyncpg://"):
        raise RuntimeError(
            f"Invalid DATABASE_URL. Expected Postgres. Got '{raw}'. Use a Postgres URL (postgresql:// or postgresql+asyncpg://)."
        )
    return coerced


def get_async_engine(url: Optional[str] = None) -> AsyncEngine:
    coerced = _coerce_to_async_url(url) if url else get_database_url()
    # If using asyncpg, we can set a DB schema via server_settings
    db_schema = os.getenv("DB_SCHEMA")
    connect_args = None
    if db_schema and coerced.startswith("postgresql+asyncpg://"):
        connect_args = {"server_settings": {"search_path": db_schema}}
    try:
        return create_async_engine(coerced, pool_pre_ping=True, connect_args=connect_args or {})
    except InvalidRequestError as e:
        raise InvalidRequestError(
            f"Failed to create async engine for URL '{coerced}'. If using Postgres, ensure the URL starts with postgresql+asyncpg://. Original: {e}"
        )


def get_sessions_engine(url: Optional[str] = None) -> AsyncEngine:
    """Engine intended for Agents SDK session tables.

    Uses AGENTS_DATABASE_URL if set; otherwise uses the main DATABASE_URL.
    Only Postgres is allowed; no SQLite fallback.
    """
    raw = url or os.getenv("AGENTS_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not raw:
        raise RuntimeError(
            "No database URL found. Set DATABASE_URL (or AGENTS_DATABASE_URL) in your .env to a Postgres URL."
        )
    coerced = _coerce_to_async_url(raw)
    lowered = coerced.lower()
    if not lowered.startswith("postgresql+asyncpg://"):
        raise RuntimeError(
            f"Invalid database URL for sessions. Expected Postgres. Got '{raw}'. Use postgresql:// or postgresql+asyncpg://."
        )
    db_schema = os.getenv("AGENTS_DB_SCHEMA")
    connect_args = None
    if db_schema and lowered.startswith("postgresql+asyncpg://"):
        connect_args = {"server_settings": {"search_path": db_schema}}
    return create_async_engine(coerced, pool_pre_ping=True, connect_args=connect_args or {})


async def init_db(engine: AsyncEngine) -> None:
    """Create tables for our local models if not present."""
    from models import Base as ModelsBase  # local import to avoid cyclic

    async with engine.begin() as conn:
        # If DB_SCHEMA is set for Postgres, ensure the schema exists and is in search_path
        db_schema = os.getenv("DB_SCHEMA")
        if db_schema:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{db_schema}"'))
            await conn.execute(text(f'SET search_path TO "{db_schema}"'))
        await conn.run_sync(ModelsBase.metadata.create_all)
        # Optionally, quick ping
        await conn.execute(text("SELECT 1"))
