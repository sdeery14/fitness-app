"""
Specialized fitness plan creation agent.
"""
from typing import Optional
from agents import Agent

from .models import FitnessPlan, AgentConfig


class FitnessPlanAgent(Agent):
    """
    Specialized agent for creating detailed fitness plans with structured output.
    
    This agent is designed to create comprehensive fitness plans including
    both training programs and meal plans based on user requirements.
    """

    def __init__(self, model: str, config: Optional[AgentConfig] = None):
        """
        Initialize the Fitness Plan Agent.
        
        Args:
            model: The AI model identifier to use
            config: Optional AgentConfig for additional configuration
        """
        self.config = config
        
        # Use structured output for all models
        instructions = self._get_structured_instructions()
        output_type = FitnessPlan

        super().__init__(
            name="Fitness Plan Assistant",
            instructions=instructions,
            model=model,
            output_type=output_type
        )

    def _get_structured_instructions(self) -> str:
        """Get instructions optimized for structured output models."""
        return """You are an expert fitness plan creation specialist. Create a detailed fitness plan with the following structure:

CRITICAL: You must respond with a valid FitnessPlan object containing exactly these three fields:
- name: A descriptive title for the plan
- training_plan: Complete workout program with exercises, sets, and reps  
- meal_plan: Detailed nutrition plan with specific foods and portions

TRAINING PLAN REQUIREMENTS:
- Organize by days (Day 1, Day 2, etc.) or muscle groups
- Include specific exercises with sets × reps (e.g., "Push-ups: 3 sets × 10 reps")
- Mention rest periods and progression tips
- Consider the user's fitness level and available equipment

MEAL PLAN REQUIREMENTS:
- Provide specific meals for breakfast, lunch, dinner, and snacks
- Include portion sizes and macronutrient balance
- Consider the user's goals (muscle gain, weight loss, etc.)
- Make it practical and achievable

IMPORTANT: Always fill in ALL three fields (name, training_plan, meal_plan) with detailed, specific content. Never leave any field empty or use placeholder text.

Example format:
- name: "Intermediate Muscle Building Program"
- training_plan: "Day 1: Upper Body\\n- Bench Press: 4 sets × 8-10 reps\\n- Pull-ups: 3 sets × 6-8 reps\\n\\nDay 2: Lower Body\\n- Squats: 4 sets × 8-10 reps"
- meal_plan: "Breakfast: 3 whole eggs + 2 egg whites, 1 cup oatmeal, 1 banana\\nLunch: 6oz chicken breast, 1.5 cups brown rice"

Now create a comprehensive fitness plan based on the user's request."""

    @classmethod
    def create_for_model(cls, model: str, config: Optional[AgentConfig] = None) -> 'FitnessPlanAgent':
        """
        Factory method to create a FitnessPlanAgent for a specific model.
        
        Args:
            model: The AI model identifier to use
            config: Optional AgentConfig for additional configuration
            
        Returns:
            Configured FitnessPlanAgent instance
        """
        return cls(model=model, config=config)
