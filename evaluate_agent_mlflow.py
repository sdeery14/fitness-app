import os
import asyncio
from typing import List

import mlflow
from agents import Runner
import uuid  # NEW

from fitness_agent import build_fitness_agent, init_engine_and_session, with_session
from memory import UserAwareSession


async def evaluate_prompts(prompts: List[str]) -> None:
    """Run a simple evaluation over a list of prompts and log to MLflow.

    This uses mlflow.openai.autolog() to capture model I/O and metadata automatically.
    It also logs a few basic metrics like number of successful runs.
    """
    # Enable OpenAI autologging for GenAI traces
    mlflow.openai.autolog()

    # Initialize infra (creates tables and a baseline session we won't reuse)
    engine, _ = await init_engine_and_session()

    # Build agent
    agent = build_fitness_agent()

    success = 0
    failures = 0

    with mlflow.start_run(run_name=os.getenv("MLFLOW_RUN_NAME", "fitness-eval")):
        # Make IDs unique per eval run to avoid cross-run mixing
        active = mlflow.active_run()
        run_suffix = (os.getenv("EVAL_RUN_SUFFIX") or (active.info.run_id if active else uuid.uuid4().hex))[:8]
        mlflow.log_param("eval_run_suffix", run_suffix)

        for i, prompt in enumerate(prompts, 1):
            try:
                # Create an isolated user+session per test, namespaced by run
                base_user = os.getenv("DEMO_USER_ID", "user_123")
                base_sess = os.getenv("DEMO_SESSION_ID", "fitness_chat")
                user_id = f"{base_user}_eval_{run_suffix}_{i}"
                sess_id = f"{base_sess}_eval_{run_suffix}_{i}"

                case_session = UserAwareSession.for_user(
                    external_user_id=user_id,
                    session_id=sess_id,
                    engine=engine,
                    label=f"Eval run {run_suffix}#{i}",
                    create_tables=False,
                    display_name=f"EvalUser{run_suffix}_{i}",
                    timezone=os.getenv("DEMO_USER_TZ", "UTC"),
                )
                await case_session.init_user()

                with with_session(case_session):
                    result = await Runner.run(agent, prompt, session=case_session)

                mlflow.log_param(f"prompt_{i}", prompt)
                mlflow.log_text(result.final_output or "", f"outputs/output_{i}.txt")
                success += 1
            except Exception as e:  # noqa: BLE001
                mlflow.log_param(f"prompt_{i}", prompt)
                mlflow.log_text(str(e), f"errors/error_{i}.txt")
                failures += 1

        # Basic metrics
        mlflow.log_metric("num_samples", len(prompts))
        mlflow.log_metric("success", success)
        mlflow.log_metric("failures", failures)


if __name__ == "__main__":
    # Example prompt set for smoke evaluation; replace with your dataset or MLflow eval framework
    sample_prompts = [
        "Hello!",
        "Please record my weight as 82.5 kg today.",
        "List my recent measurements.",
    ]

    # Ensure we have an OpenAI key if we expect LLM calls
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set; cannot run MLflow evaluation.")

    asyncio.run(evaluate_prompts(sample_prompts))
