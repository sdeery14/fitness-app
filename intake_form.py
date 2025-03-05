from pydantic import BaseModel, PositiveFloat, PositiveInt, Field
from typing import Literal

# Pydantic model for intake form validation
class IntakeForm(BaseModel):
    height_in: PositiveFloat = None  # Enforce positive height, allow None
    weight_lbs: PositiveFloat = None  # Enforce positive weight, allow None
    body_fat: PositiveFloat = Field(None, ge=0, le=100.0)  # Body fat percentage must be between 0 and 100, allow None
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