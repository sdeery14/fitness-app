"""
Agents module for the fitness core library.
"""
from .fitness_agent import FitnessAgent
from .agent_models import AgentResponse, ConversationMessage, AgentConfig
from .fitness_plan_models import FitnessPlan
from .training_plan_models import TrainingPlan, TrainingPeriod, TrainingSplit, TrainingDay, Exercise, IntensityLevel
from .meal_plan_models import MealPlan, MealPeriod, MealDayTemplate, MealSlot, MealOption
from .providers import ModelProvider

__all__ = [
    'FitnessAgent',
    'FitnessPlan',
    'TrainingPlan', 'TrainingPeriod', 'TrainingSplit', 'TrainingDay', 'Exercise', 'IntensityLevel',
    'MealPlan', 'MealPeriod', 'MealDayTemplate', 'MealSlot', 'MealOption',
    'AgentResponse',
    'ConversationMessage',
    'AgentConfig',
    'ModelProvider'
]
