"""Meal / nutrition plan related Pydantic models split from fitness_plan_model.

Hierarchy:
MealPlan > MealPeriod > MealDayTemplate > MealSlot > MealOption
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum

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

__all__ = [
    "MealOption",
    "MealSlot",
    "MealDayTemplate",
    "MealPeriod",
    "MealPlan",
]
