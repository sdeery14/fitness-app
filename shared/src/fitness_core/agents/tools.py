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
    usage_examples: Optional[List[str]] = None
    when_to_use: Optional[str] = None


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
        When you need to save a completed fitness plan that has been generated as structured output, use the create_fitness_plan tool.
        
        This tool should be called with a fully completed FitnessPlan object that includes:
        - name: A descriptive name for the fitness plan
        - training_plan: Detailed training/workout information
        - meal_plan: Comprehensive nutrition and meal planning details

        The create_fitness_plan tool takes the following actions: 
        1. Saves the completed FitnessPlan object to the FitnessAgent class
        2. Makes the plan available for display in the UI
        3. Returns a formatted confirmation message with the plan details

        This tool should be used AFTER you have already generated a complete fitness plan as structured output, not for generating new plans.
        """,
        when_to_use="You have a completed FitnessPlan object that needs to be saved and displayed in the UI",
        usage_examples=[
            "After generating a structured FitnessPlan object from user requirements",
            "When you need to store a completed plan for UI display",
            "To save a plan that was created through structured output generation"
        ]
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
        if config.when_to_use:
            instructions.append(f"**When to use:** {config.when_to_use}")
        if config.usage_examples:
            instructions.append("**Examples:**")
            for example in config.usage_examples:
                instructions.append(f"- {example}")
        instructions.append("")
    
    return "\n".join(instructions)
