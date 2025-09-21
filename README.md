## Fitness App

This Fitness App is an AI coach that connects a model to real tools and persistent memory to help you generate and continually update a personalized fitness plan. Under the hood, this project demonstrates a custom session memory that augments the OpenAI Agents SDK sessions with application users and profiles while delegating message storage to the SDK's SQLAlchemy session backend.

### What you get

- User accounts (`users`)
- User profiles (`user_profiles`)
- User-to-session mapping (`user_sessions`)
- Full conversation memory via Agents' `SQLAlchemySession`

### Requirements for Local Development

- Python 3.12
- Poetry
- Docker (for the Postgres database)

### Local Development Setup

1) Install dependencies

```powershell
poetry install
```

2) Configure environment

Create a `.env` file from the `.env.example` file.

Make sure to create and add your own `OPENAI_API_KEY`.

3) Start Postgres

Note: The tables will be added the first time the agent is called.

```powershell
# From repo root
docker compose up --build -d
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
