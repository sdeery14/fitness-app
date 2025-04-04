from pydantic import BaseModel

class Food(BaseModel):
    food_name: str

class Meal(BaseModel):
    meal_name: str
    meal_summary: str
    foods: list[Food]

class MealPlan(BaseModel):
    meal_plan_name: str
    meal_plan_summary: str
    meals: list[Meal]

class Exercise(BaseModel):
    exercise_name: str
    exercise_summary: str

class Workout(BaseModel):
    workout_name: str
    workout_summary: str
    exercises: list[Exercise]

class WorkoutPlan(BaseModel):
    workout_plan_name: str
    workout_plan_summary: str
    workouts: list[Workout]

class FitnessPlan(BaseModel):
    fitness_plan_name: str
    fitness_plan_summary: str
    workout_plan: list[WorkoutPlan]
    meal_plan: list[MealPlan]