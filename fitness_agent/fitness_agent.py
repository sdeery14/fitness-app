from pydantic import BaseModel
from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()


class FitnessPlan(BaseModel):
    name: str
    training_plan: str
    meal_plan: str


class FitnessAgent(Agent):
    """
    A helpful assistant for general fitness guidance and handoffs to a plan-building agent.
    """

    def __init__(self):
        fitness_plan_agent = Agent(
            name="Fitness Plan Assistant",
            instructions="You are a helpful assistant for creating personalized fitness plans.",
            model="litellm/anthropic/claude-3-haiku-20240307",
            output_type=FitnessPlan
        )

        super().__init__(
            name="Fitness Assistant",
            model="litellm/anthropic/claude-3-haiku-20240307",
            instructions="""
            You are a helpful assistant for fitness-related queries.
            
            If the user wants to create a fitness plan, hand them off to the Fitness Plan Assistant.
            """,
            handoffs=[fitness_plan_agent]
        )


if __name__ == "__main__":
    agent = FitnessAgent()
    result = Runner.run_sync(agent, "Hello. Please make me a fitness plan.")
    print(result.final_output)