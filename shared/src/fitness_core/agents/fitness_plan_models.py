"""Aggregate fitness plan model that composes training and meal plans.

Split from the original monolithic fitness_plan_model module.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import date
from .training_plan_models import TrainingPlan
from .meal_plan_models import MealPlan

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

__all__ = ["FitnessPlan"]
