"""
Pydantic models for structured LLM outputs.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class IntensityLevel(str, Enum):
    """Intensity levels for exercises."""
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    MAX_EFFORT = "max_effort"


class Exercise(BaseModel):
    """Model for a single exercise."""
    name: str = Field(
        description="The name of the exercise (e.g., 'Push-ups', 'Squats', 'Deadlift')"
    )
    description: Optional[str] = Field(
        default=None,
        description="Brief description of how to perform the exercise, including proper form and technique"
    )
    duration: Optional[int] = Field(
        default=None,
        description="Duration of the exercise in seconds (for time-based exercises like planks or cardio)"
    )
    sets: Optional[int] = Field(
        default=None,
        description="Number of sets to perform for this exercise (e.g., 3 sets). Used for strength training and resistance exercises."
    )
    reps: Optional[int] = Field(
        default=None,
        description="Number of repetitions per set (e.g., 10 reps). Used for strength training exercises. Can be a range like '8-12' for variety."
    )
    intensity: Optional[IntensityLevel] = Field(
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
    exercises: Optional[List[Exercise]] = Field(  # Made optional
        default=None,
        description="List of exercises to be performed on this training day, with full details including sets, reps, and intensity. Leave empty/null for complete rest days."
    )
    intensity: Optional[IntensityLevel] = Field(
        default=None,
        description="Overall intensity of the training day. Use 'light' for recovery/mobility, 'moderate' for standard training, 'heavy' for strength focus, 'max_effort' for testing. Leave blank for complete rest days."
    )
    rest_day: bool = Field(
        default=False,
        description="True if this is a complete rest day with no exercises"
    )


class TrainingPlanSplit(BaseModel):
    """A training split represents a complete cycle of training days (e.g., a weekly routine)."""
    name: str = Field(
        description="Descriptive name for the split approach (e.g., 'Push/Pull/Legs Split', 'Upper/Lower Split', 'Full Body Circuit')"
    )
    order: int = Field(
        description="Sequential order when multiple splits are used in periodization (1 for first phase, 2 for second phase, etc.)"
    )
    description: str = Field(
        description="Detailed explanation of the split's training philosophy, target muscle groups, and how days are organized"
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Optional start date for this specific split. If not provided, will be calculated based on previous splits. Useful for precise scheduling of periodized programs."
    )
    training_days: List[TrainingDay] = Field(
        description="All training days in the split, ordered sequentially. Include rest days for complete weekly schedules."
    )


class TrainingPlan(BaseModel):
    """Complete training plan containing one or more training splits."""
    name: str = Field(
        description="Catchy name that reflects the plan's focus (e.g., 'Beginner Strength Foundation', 'Advanced Powerlifting Prep')"
    )
    description: str = Field(
        description="Comprehensive overview including training philosophy, progression strategy, target audience, and expected timeline"
    )
    training_plan_splits: List[TrainingPlanSplit] = Field(
        description="Ordered list of training splits. Single split for consistent routines, multiple splits for periodized programs with distinct phases (base building → strength → peaking)"
    )


class FitnessPlan(BaseModel):
    """Structured fitness plan model for LLM output."""
    name: str = Field(
        description="Catchy, descriptive name for the fitness plan (e.g., 'Beginner Strength Builder', '30-Day Fat Loss Challenge')"
    )
    goal: str = Field(
        description="Primary goal of the fitness plan (e.g., 'Build muscle', 'Lose weight', 'Improve endurance'). Should be specific and measurable."
    )
    description: str = Field(
        description="Comprehensive overview of the fitness plan, including goals, target audience, and expected outcomes"
    )
    training_plan: TrainingPlan = Field(
        description="The training plan includes all of the workout splits, training days, and exercises"
    )
    meal_plan: str = Field(
        description="Detailed nutrition guidance including meal suggestions, macronutrient targets, and eating schedule. Should be practical and specific to the fitness goals."
    )
    start_date: Optional[date] = Field(
        default_factory=lambda: date.today(),
        description="The date when the user should start this fitness plan"
    )
    target_date: Optional[date] = Field(
        default=None,
        description="Optional target completion date or milestone date for the fitness plan"
    )
