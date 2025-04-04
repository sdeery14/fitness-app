from pydantic import BaseModel, PositiveFloat, PositiveInt, Field
from typing import Literal

# Pydantic model for intake form validation
class UserProfile(BaseModel):
    height_in: PositiveFloat = None  # Enforce positive height, allow None
    weight_lbs: PositiveFloat = None  # Enforce positive weight, allow None
    age: PositiveInt = None  # Age must be a positive integer, allow None
    sex: Literal["male", "female", "other"] = None  # Restrict to valid choices, allow None
    activity_level: Literal["sedentary", "light", "moderate", "active", "very active"] = None  # Allow None
    goals: str = None  # Allow None
    diet_phase: Literal["cutting", "bulking", "maintenance"] = None  # Allow None

    def update_values(self, updates: dict):
        """Update the form fields with new values."""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)

    # Calculate BMR, TDEE, daily calories, and macros
        #bmr, tdee, daily_calories, macros = self.calculate_calories_and_macros()