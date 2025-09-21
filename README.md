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
# From repo root; run as a module so the app package is importable
poetry run python -m app.run_agent_demo
```

If `OPENAI_API_KEY` is not set, the script will initialize the database tables and exit.

### MLflow evaluation

This project includes a minimal MLflow evaluation harness that uses `mlflow.openai.autolog()` to capture LLM traces.

```powershell
# From repo root; run as a module
poetry run python -m app.evals.evaluate_agent_mlflow
```

Environment variables you may want to set:

- `MLFLOW_TRACKING_URI` – Where MLflow should log runs (e.g., http://127.0.0.1:5000 or a file path)
- `MLFLOW_RUN_NAME` – Optional run name label
- `OPENAI_API_KEY` – Required to make model calls
- `DATABASE_URL` – Postgres connection string (postgresql:// or postgresql+asyncpg://)
- `DB_SCHEMA` – Optional Postgres schema name to create/use
- `DEMO_USER_ID`, `DEMO_SESSION_ID`, `DEMO_USER_NAME`, `DEMO_USER_TZ` – Defaults used by the demo/eval scripts

### VS Code

A debug configuration is provided to run the MLflow eval as a module:

- Launch: “Python Debugger: Run eval module” (runs `python -m app.evals.evaluate_agent_mlflow` from the workspace root)

### Project layout

- `app/`
  - `db.py` – Async engine factory and database initialization
  - `fitness_agent.py` – Functions to build the agent and initialize engine/session (no side effects)
  - `memory.py` – `UserAwareSession` that composes `SQLAlchemySession` and manages user/profile binding
  - `models.py` – SQLAlchemy models for users, profiles, and user-sessions
  - `run_agent_demo.py` – Simple demo runner to send one message
  - `evals/`
    - `evaluate_agent_mlflow.py` – Minimal MLflow evaluation harness
