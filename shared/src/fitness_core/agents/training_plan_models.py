"""Training plan related Pydantic models split from fitness_plan_model.

This module defines the training-side periodization hierarchy:
TrainingPlan > TrainingPeriod > TrainingSplit > TrainingDay > Exercise
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import date

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

__all__ = [
    "IntensityLevel",
    "Exercise",
    "TrainingDay",
    "TrainingSplit",
    "TrainingPeriod",
    "TrainingPlan",
]
