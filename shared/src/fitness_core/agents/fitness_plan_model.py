"""
Pydantic models for structured LLM outputs.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class IntensityLevel(str, Enum):
    """Intensity levels for exercises."""
    REST = "rest"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    MAX_EFFORT = "max_effort"


class Exercise(BaseModel):
    """Model for a single exercise."""
    name: str = Field(
        description="The name of the exercise (e.g., 'Push-ups', 'Squats', 'Deadlift')"
    )
    description: str = Field(
        description="Brief description of how to perform the exercise, including proper form and technique"
    )
    duration: Optional[int] = Field(
        default=None,
        description="Duration of the exercise in seconds (for time-based exercises like planks or cardio)"
    )
    distance: Optional[float] = Field(
        default=None,
        description="Distance to be covered in meters (for running, cycling, etc.)"
    )
    sets: Optional[int] = Field(
        default=None,
        description="Number of sets to perform for this exercise (e.g., 3 sets). Used for strength training and resistance exercises."
    )
    reps: Optional[int] = Field(
        default=None,
        description="Number of repetitions per set (e.g., 10 reps). Used for strength training exercises. Can be a range like '8-12' for variety."
    )
    intensity: IntensityLevel = Field(
        default=None,
        description="Intensity level of the exercise. 'light' for warm-up/mobility work, 'moderate' for general training, 'heavy' for strength focus (80-90% effort), 'max_effort' for testing/competition lifts. Can be left blank for rest days or exercises where intensity is not applicable."
    )


class TrainingDay(BaseModel):
    """Model for a single training day."""
    name: str = Field(
        description="Descriptive name for the training day (e.g., 'Upper Body Strength', 'Cardio & Core', 'Active Recovery', 'Rest Day')"
    )
    order_number: int = Field(
        description="The sequential position of this day within the split (1-7 for weekly splits)"
    )
    description: str = Field(
        description="Brief overview of the day's focus and training objectives (e.g., 'Focus on compound upper body movements with moderate intensity')"
    )
    exercises: List[Exercise] = Field(
        description="List of exercises to be performed on this training day, with full details including sets, reps, and intensity. Include good rest activities for complete rest days."
    )
    intensity: IntensityLevel = Field(
        description="Overall intensity of the training day. Use 'light' for recovery/mobility, 'moderate' for standard training, 'heavy' for strength focus, 'max_effort' for testing. Leave blank for complete rest days."
    )

class TrainingSplit(BaseModel):
    """A training split represents a complete cycle of training days within a specific periodization phase."""
    name: str = Field(
        description="Descriptive name for the split approach (e.g., 'Push/Pull/Legs Split', 'Upper/Lower Split', 'Full Body Circuit')"
    )
    description: str = Field(
        description="Detailed explanation of the split's training philosophy, target muscle groups, how days are organized, and how this phase fits into the overall periodization strategy"
    )
    training_days: List[TrainingDay] = Field(
        description="All training days in the training split, ordered sequentially. Make sure to include all the rest days needed in the split."
    )

class TrainingPeriod(BaseModel):
    name: str = Field(
        description="Descriptive name for the period (e.g., 'Base Phase', 'Advanced Phase', 'Preparation Phase')"
    )
    description: str = Field(
        description="Overview of the period's focus, training goals, and how it fits into the overall plan"
    )
    start_date: date = Field(
        description="Start date for this specific training period."
    )
    intensity: IntensityLevel = Field(
        description="Overall intensity level for this period. Use 'light' for recovery, 'moderate' for general training, 'heavy' for strength focus, 'max_effort' for testing, 'rest' for complete rest."
    )
    training_split: TrainingSplit = Field(
        description="The training split that will be followed during this period. Should include all training days and rest days as the schedule will be created assuming a rolling schedule of training splits."
    )

class TrainingPlan(BaseModel):
    """Complete periodized training plan with progressive phases leading to a target goal/event."""
    name: str = Field(
        description="Name that reflects the plan's focus and target event"
    )
    description: str = Field(
        description="Comprehensive overview including training philosophy, periodization strategy, target audience, expected timeline, and how the phases progress toward the goal"
    )
    training_periods: List[TrainingPeriod] = Field(
        description="Ordered list of TrainingPeriod objects representing different phases of the training plan."
    )


class FitnessPlan(BaseModel):
    """Structured fitness plan model for LLM output."""
    name: str = Field(
        description="Name for the fitness plan"
    )
    goal: str = Field(
        description="Primary goal of the fitness plan"
    )
    description: str = Field(
        description="Comprehensive overview of the fitness plan, including a brief overview of how the training plan and meal plan meet the goal."
    )
    training_plan: TrainingPlan = Field(
        description="The training plan includes all of the workout splits, training days, and exercises"
    )
    meal_plan: str = Field(
        description="Detailed nutrition guidance including meal suggestions, macronutrient targets, and eating schedule. Should be practical and specific to the fitness goals."
    )
    start_date: date = Field(
        default_factory=lambda: date.today(),
        description="The date when the user should start this fitness plan"
    )
    target_date: date = Field(
        description="The target completion date or milestone date for the fitness plan"
    )
