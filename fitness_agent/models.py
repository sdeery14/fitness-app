"""
Data models for the fitness agent.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum

# Agent and Configuration Models
class AgentResponse(BaseModel):
    """Standard agent response format."""
    content: str
    metadata: Optional[dict] = None

class ConversationMessage(BaseModel):
    """Individual conversation message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class AgentConfig(BaseModel):
    """Configuration for the fitness agent."""
    model_name: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    custom_instructions: Optional[str] = None

# Training Models
class IntensityLevel(str, Enum):
    """Intensity levels for exercises."""
    REST = "rest"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    MAX_EFFORT = "max_effort"

class Exercise(BaseModel):
    """Model for a single exercise."""
    name: str = Field(description="The name of the exercise (e.g., 'Push-ups', 'Squats', 'Deadlift')")
    description: str = Field(description="Brief description of how to perform the exercise, including proper form and technique")
    duration: Optional[int] = Field(default=None, description="Duration in seconds (for time-based exercises)")
    distance: Optional[float] = Field(default=None, description="Distance in meters (for running, cycling, etc.)")
    sets: Optional[int] = Field(default=None, description="Number of sets to perform (used for resistance exercises)")
    reps: Optional[int] = Field(default=None, description="Number of repetitions per set (can be a range like '8-12')")
    intensity: Optional[IntensityLevel] = Field(default=None, description="Intensity level; may be omitted on rest / skill days")

class TrainingDay(BaseModel):
    """Model for a single training day."""
    name: str = Field(description="Descriptive name (e.g., 'Upper Body Strength', 'Cardio & Core')")
    order_number: int = Field(description="Sequential position of this day within the split (1-based)")
    description: str = Field(description="Brief overview of the day's focus and training objectives")
    exercises: List[Exercise] = Field(description="List of exercises performed on this day")
    intensity: IntensityLevel = Field(description="Overall intensity of the day")

class TrainingSplit(BaseModel):
    """A training split represents a complete cycle of training days within a specific periodization phase."""
    name: str = Field(description="Descriptive name (e.g., 'Push/Pull/Legs Split', 'Upper/Lower Split')")
    description: str = Field(description="Explanation of philosophy, target muscle groups, and day organization")
    training_days: List[TrainingDay] = Field(description="All training days in order, including rest days where relevant")

class TrainingPeriod(BaseModel):
    name: str = Field(description="Name for the training period (e.g., 'Base Phase', 'Peak Phase')")
    description: str = Field(description="Focus, goals, and context inside the overall plan")
    start_date: date = Field(description="Start date for this period")
    intensity: IntensityLevel = Field(description="Overall intensity emphasis of the period")
    training_split: TrainingSplit = Field(description="Training split followed during this period")

class TrainingPlan(BaseModel):
    """Complete periodized training plan with progressive phases leading to a target goal/event."""
    name: str = Field(description="Name that reflects the plan's focus / target event")
    description: str = Field(description="Overview including philosophy, periodization strategy, and progression")
    training_periods: List[TrainingPeriod] = Field(description="Ordered list of TrainingPeriod objects")

# Meal Models  
class FoodOption(BaseModel):
    """A specific food item with quantity."""
    name: str = Field(description="Name of the food item (e.g., 'Chicken Breast', 'Brown Rice')")

class MealOption(BaseModel):
    """A concrete meal option the user can pick for a slot."""
    name: str = Field(description="Name of the meal (e.g., 'Oatmeal with Berries', 'Grilled Chicken Bowl')")
    description: str = Field(description="Short description or preparation / substitution notes")
    ingredients: List[FoodOption] = Field(description="Ingredient items")

class MealSlot(BaseModel):
    """A meal occasion (e.g., Breakfast, Lunch, Snack) with interchangeable options."""
    name: str = Field(description="Slot name (e.g., 'Breakfast', 'Pre-Workout', 'Dinner')")
    order_number: int = Field(description="Order of this slot in the day (1 = earliest)")
    options: List[MealOption] = Field(description="Alternate meal options to choose from for this slot")

class MealDayTemplate(BaseModel):
    """Reusable daily meal structure with slots and their options."""
    name: str = Field(description="Name for this daily template (e.g., 'High Carb Training Day', 'Rest Day Template')")
    description: str = Field(description="Purpose, macro emphasis, and when to use this template")
    slots: List[MealSlot] = Field(description="Ordered meal slots comprising the day")

class CaloricPhase(str, Enum):
    deficit = "deficit"
    maintenance = "maintenance"
    surplus = "surplus"

class MealPeriod(BaseModel):
    """Nutrition phase aligned with training periodization (e.g., bulk, cut, maintenance)."""
    name: str = Field(description="Descriptive name (e.g., 'Lean Bulk Phase', 'Mini Cut Phase')")
    description: str = Field(description="Focus, macro strategy, and support for training goals during this period")
    start_date: date = Field(description="Start date for this meal period")
    daily_templates: List[MealDayTemplate] = Field(description="Reusable daily meal templates (choose one per day)")
    caloric_phase: CaloricPhase = Field(description="Energy balance focus for the period")
    intensity: float = Field(ge=0, le=100, description="How aggressively to apply the phase (0–100)")

class MealPlan(BaseModel):
    """Model for a meal plan."""
    name: str = Field(description="Name for the meal plan")
    description: str = Field(description="Overview of dietary philosophy and how it supports goals")
    meal_periods: List[MealPeriod] = Field(description="Ordered meal periods (cut, maintenance, bulk, etc.)")

# Combined Fitness Plan
class FitnessPlan(BaseModel):
    """Structured fitness plan model for LLM output.

    Combines training and nutrition periodization into a single artifact.
    """
    name: str = Field(description="Name for the fitness plan")
    goal: str = Field(description="Primary goal of the fitness plan")
    description: str = Field(description="Overview linking training + meal strategy to the goal")
    training_plan: TrainingPlan = Field(description="Training plan with periods, splits, days, and exercises")
    meal_plan: MealPlan = Field(description="Meal plan with periods and daily templates")
    start_date: date = Field(default_factory=date.today, description="Plan start date")
    target_date: date = Field(description="Target completion / milestone date")

__all__ = [
    'AgentResponse', 'ConversationMessage', 'AgentConfig',
    'IntensityLevel', 'Exercise', 'TrainingDay', 'TrainingSplit', 'TrainingPeriod', 'TrainingPlan',
    'FoodOption', 'MealOption', 'MealSlot', 'MealDayTemplate', 'CaloricPhase', 'MealPeriod', 'MealPlan',
    'FitnessPlan'
]
