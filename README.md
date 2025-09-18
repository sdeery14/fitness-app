## Fitness App – Custom Session Memory

This project demonstrates a custom session memory that augments the OpenAI Agents SDK sessions with application users and profiles while delegating message storage to the SDK's SQLAlchemy session backend.

### What you get

- User accounts (`users`)
- User profiles (`user_profiles`)
- User-to-session mapping (`user_sessions`)
- Full conversation memory via Agents' `SQLAlchemySession`

### Requirements

- Python 3.12
- Poetry
- A running Postgres instance

### Setup

1) Install dependencies

```powershell
poetry install
```

2) Configure environment

Create a `.env` with at least:

```env
# OpenAI (optional for running actual conversations)
OPENAI_API_KEY=sk-...

# Database (Postgres only)
# Examples:
#   postgres://fitness_user:fitness_password@localhost:5432/fitness_app
#   postgresql://fitness_user:fitness_password@localhost:5432/fitness_app
#   postgresql+asyncpg://fitness_user:fitness_password@localhost:5432/fitness_app
DATABASE_URL=postgresql://fitness_user:fitness_password@localhost:5432/fitness_app

# Optional: use a separate schema for app tables
# DB_SCHEMA=public

# (Optional) Separate DB/schema for Agents SDK tables
# AGENTS_DATABASE_URL=postgresql://fitness_user:fitness_password@localhost:5432/fitness_app
# AGENTS_DB_SCHEMA=agents

# Demo identifiers
DEMO_USER_ID=user_123
DEMO_USER_NAME=Alex
DEMO_USER_TZ=UTC
DEMO_SESSION_ID=fitness_chat
```

3) (Optional) Start Postgres

```powershell
# From repo root
docker compose up -d
```

4) Run the demo

```powershell
poetry run python fitness_agent.py
```

If `OPENAI_API_KEY` is not set, the script will initialize the database tables and exit; if set, it will perform a quick agent run with session memory.

### Files

- `models.py` – SQLAlchemy models for users, profiles, and user-sessions
- `db.py` – Async engine factory and database initialization
- `memory.py` – `UserAwareSession` that composes `SQLAlchemySession` for items and manages user/profile binding
- `fitness_agent.py` – Example showing how to create and use the user-aware session

### Notes

- Postgres is required. The app raises a clear error if `DATABASE_URL` is missing or not Postgres.
- The URL is automatically coerced to `postgresql+asyncpg://` for async usage when `postgres://`, `postgresql://`, or `postgresql+psycopg2://` are provided.
- The Agents SDK's own tables for conversations/messages are created by the `SQLAlchemySession(create_tables=True)` delegate.
- Our own app tables are created via `init_db(engine)`.

### Reference

- OpenAI Agents SDK Sessions: https://openai.github.io/openai-agents-python/sessions/
