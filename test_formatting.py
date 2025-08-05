#!/usr/bin/env python3
"""
Test script for structured fitness plan formatting
"""

# Sample structured output from your example
sample_output = """🏋️ Intermediate Muscle Hypertrophy Accelerator
💪 Training Plan
name='Muscle Hypertrophy Split' description='A 5-day split targeting different muscle groups with high volume and strategic intensity progression to maximize muscle growth.' training_plan_splits=[TrainingPlanSplit(name='Muscle Building Weekly Split', order=1, description='Advanced split focusing on targeted muscle group development with progressive overload techniques', start_date=datetime.date(2024, 2, 15), training_days=[TrainingDay(name='Chest and Triceps Day', order_number=1, description='High-volume chest and triceps workout with compound and isolation movements', exercises=[Exercise(name='Barbell Bench Press', description='Perform with a controlled tempo, focusing on chest muscle engagement', duration=None, sets=4, reps=8, intensity=<IntensityLevel.HEAVY: 'heavy'>), Exercise(name='Incline Dumbbell Press', description='Focus on full range of motion and mind-muscle connection', duration=None, sets=3, reps=10, intensity=<IntensityLevel.MODERATE: 'moderate'>), Exercise(name='Tricep Pushdowns', description='Keep elbows close to body, use a controlled movement', duration=None, sets=3, reps=12, intensity=<IntensityLevel.MODERATE: 'moderate'>)], intensity=<IntensityLevel.HEAVY: 'heavy'>, rest_day=False), TrainingDay(name='Back and Biceps Day', order_number=2, description='Comprehensive back and biceps muscle development workout', exercises=[Exercise(name='Deadlifts', description='Maintain proper form, engage core and back muscles', duration=None, sets=4, reps=6, intensity=<IntensityLevel.HEAVY: 'heavy'>), Exercise(name='Pull-ups', description='Use full range of motion, can use assisted pull-up machine if needed', duration=None, sets=3, reps=8, intensity=<IntensityLevel.MODERATE: 'moderate'>), Exercise(name='Barbell Curls', description='Controlled movement, focus on bicep contraction', duration=None, sets=3, reps=10, intensity=<IntensityLevel.MODERATE: 'moderate'>)], intensity=<IntensityLevel.HEAVY: 'heavy'>, rest_day=False), TrainingDay(name='Leg Day', order_number=3, description='Intense lower body workout targeting quads, hamstrings, and glutes', exercises=[Exercise(name='Barbell Squats', description='Maintain proper depth and form, engage core', duration=None, sets=4, reps=8, intensity=<IntensityLevel.HEAVY: 'heavy'>), Exercise(name='Romanian Deadlifts', description='Focus on hamstring stretch and contraction', duration=None, sets=3, reps=10, intensity=<IntensityLevel.MODERATE: 'moderate'>), Exercise(name='Leg Press', description='Full range of motion, controlled tempo', duration=None, sets=3, reps=12, intensity=<IntensityLevel.MODERATE: 'moderate'>)], intensity=<IntensityLevel.HEAVY: 'heavy'>, rest_day=False), TrainingDay(name='Shoulder Day', order_number=4, description='Comprehensive shoulder muscle development with varied movements', exercises=[Exercise(name='Overhead Military Press', description='Strict form, engage core for stability', duration=None, sets=4, reps=8, intensity=<IntensityLevel.HEAVY: 'heavy'>), Exercise(name='Lateral Raises', description='Controlled movement, avoid swinging', duration=None, sets=3, reps=12, intensity=<IntensityLevel.MODERATE: 'moderate'>), Exercise(name='Face Pulls', description='Focus on rear deltoid engagement', duration=None, sets=3, reps=15, intensity=<IntensityLevel.LIGHT: 'light'>)], intensity=<IntensityLevel.HEAVY: 'heavy'>, rest_day=False), TrainingDay(name='Arms and Core Day', order_number=5, description='Targeted arm muscle development with core strengthening', exercises=[Exercise(name='Close Grip Bench Press', description='Emphasize tricep engagement', duration=None, sets=3, reps=10, intensity=<IntensityLevel.MODERATE: 'moderate'>), Exercise(name='Hammer Curls', description='Controlled bicep curl variation', duration=None, sets=3, reps=12, intensity=<IntensityLevel.MODERATE: 'moderate'>), Exercise(name='Planks', description='Maintain proper form, engage entire core', duration=60, sets=3, reps=None, intensity=<IntensityLevel.MODERATE: 'moderate'>)], intensity=<IntensityLevel.MODERATE: 'moderate'>, rest_day=False), TrainingDay(name='Rest and Recovery', order_number=6, description='Complete rest day for muscle recovery and growth', exercises=None, intensity=None, rest_day=True), TrainingDay(name='Rest and Recovery', order_number=7, description='Complete rest day for muscle recovery and growth', exercises=None, intensity=None, rest_day=True)])]

🥗 Meal Plan
High-protein diet focusing on lean proteins, complex carbohydrates, and healthy fats. Aim for 1.6-2.2g of protein per kg of body weight. Consume 300-500 calories above maintenance level. Meal examples: Chicken breast with brown rice and vegetables, salmon with sweet potato, protein smoothies, egg white omelets with whole grain toast. Supplement with whey protein and creatine monohydrate.

📊 Additional Information
Plan created with AI assistance
Customize as needed for your preferences
Consult healthcare providers for medical advice
Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications."""

# Import the formatter
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared', 'src'))

from fitness_core.services.formatters import ResponseFormatter

# Test the formatter
print("=== Testing Structured Fitness Plan Formatting ===\n")

try:
    formatted_result = ResponseFormatter.format_fitness_plan(sample_output, style="detailed")
    print("FORMATTED OUTPUT:")
    print(formatted_result)
except Exception as e:
    print(f"Error: {e}")
    print(f"Raw input: {sample_output[:200]}...")
