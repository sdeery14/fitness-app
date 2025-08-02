"""
Fitness agent tools with grouped function and prompt definitions.
"""
from typing import Optional, Any, Dict, List
from dataclasses import dataclass
from agents import function_tool, RunContextWrapper

from .models import FitnessPlan


@dataclass
class FunctionToolConfig:
    """Configuration for a function tool including its prompt instructions."""
    function: callable
    prompt_instructions: str


@function_tool
async def create_fitness_plan(
    ctx: RunContextWrapper[Any],
    fitness_plan: FitnessPlan,
) -> str:
    """Save a completed fitness plan to the FitnessAgent for display in the UI.

    Args:
        fitness_plan: A fully completed FitnessPlan object with name, training_plan, and meal_plan
    """
    try:
        # Import here to avoid circular imports
        from .fitness_agent import FitnessAgent
        
        # Save the fitness plan to the agent class
        FitnessAgent.set_latest_fitness_plan(fitness_plan)
        
        # Format the plan for display
        formatted_plan = f"""**{fitness_plan.name}**

**Training Plan:**
{fitness_plan.training_plan}

**Meal Plan:**
{fitness_plan.meal_plan}"""
        
        return f"I've created and saved your personalized fitness plan:\n\n{formatted_plan}\n\nThis plan has been tailored specifically for your requirements and is now available in the fitness plan section below. Please consult with a healthcare provider before starting any new fitness program."
        
    except Exception as e:
        return f"I apologize, but I encountered an error while saving your fitness plan: {str(e)}. Please try again or contact support if the issue persists."


# Tool configurations with their associated prompt instructions
FITNESS_TOOLS = {
    "create_fitness_plan": FunctionToolConfig(
        function=create_fitness_plan,
        prompt_instructions="""
        When the user requests a fitness plan, use the create_fitness_plan tool with a fully completed FitnessPlan object.
        
        The FitnessPlan object must include:
        - name: A descriptive name for the fitness plan
        - training_plan: Detailed training/workout information
        - meal_plan: Comprehensive nutrition and meal planning details

        This tool saves the plan to the FitnessAgent class, makes it available for UI display, and returns a formatted confirmation message.
        Do not read the plan back to the user in the conversation as they can see it in the UI component.
        """
    )
}


def get_tool_functions() -> List[callable]:
    """Get all function tools for the agent."""
    return [config.function for config in FITNESS_TOOLS.values()]


def get_combined_instructions() -> str:
    """Get combined prompt instructions for all tools."""
    instructions = []
    for tool_name, config in FITNESS_TOOLS.items():
        instructions.append(f"## {tool_name.replace('_', ' ').title()}")
        instructions.append(config.prompt_instructions)
        instructions.append("")
    
    return "\n".join(instructions)
