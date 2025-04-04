def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation."""
    if sex.lower() == "male":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Calculate Total Daily Energy Expenditure (TDEE) based on activity level."""
    activity_factors = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "super active": 1.9,
    }
    return bmr * activity_factors.get(activity_level.lower(), 1.2)

def calculate_macros(calories: float, goal: str) -> dict:
    """Calculate macronutrient distribution based on fitness goal."""
    macro_ratios = {
        "cutting": {"protein": 0.40, "carbs": 0.35, "fats": 0.25},
        "maintenance": {"protein": 0.30, "carbs": 0.45, "fats": 0.25},
        "bulking": {"protein": 0.30, "carbs": 0.50, "fats": 0.20},
    }
    
    ratios = macro_ratios.get(goal.lower(), macro_ratios["maintenance"])
    protein_grams = (calories * ratios["protein"]) / 4
    fat_grams = (calories * ratios["fats"]) / 9
    carb_grams = (calories * ratios["carbs"]) / 4
    
    return {
        "calories": round(calories, 2),
        "protein_grams": round(protein_grams, 2),
        "fat_grams": round(fat_grams, 2),
        "carb_grams": round(carb_grams, 2)
    }

def get_daily_calories(tdee: float, goal: str) -> float:
    """Adjust calories based on the goal."""
    adjustments = {
        "cutting": -500,
        "maintenance": 0,
        "bulking": 300,
    }
    return tdee + adjustments.get(goal.lower(), 0)

def convert_weight_lbs_to_kg(weight_lbs: float) -> float:
    return weight_lbs * 0.453592

def convert_height_in_to_cm(height_in: float) -> float:
    return height_in * 2.54

def calculate_calories_and_macros(weight_lbs: float, height_in: float, age: int, sex: str, activity_level: str, goal: str):
    """Calculate BMR, TDEE, daily calories, and macros."""
    weight_kg = convert_weight_lbs_to_kg(weight_lbs)
    height_cm = convert_height_in_to_cm(height_in)
    bmr = calculate_bmr(weight_kg, height_cm, age, sex)
    tdee = calculate_tdee(bmr, activity_level)
    daily_calories = get_daily_calories(tdee, goal)
    macros = calculate_macros(daily_calories, goal)
    return bmr, tdee, daily_calories, macros