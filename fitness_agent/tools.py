"""
Tools for the fitness agent.
"""
import logging
from typing import Optional, Any, Dict, List
from dataclasses import dataclass
from datetime import date, timedelta
from agents import function_tool

from .models import FitnessPlan, TrainingDay, IntensityLevel
from .memory import SessionManager, UserProfile

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTrainingDay:
    """A training day with an assigned date."""
    date: date
    training_day: TrainingDay
    split_name: str
    week_number: int
    day_in_week: int


def get_tool_functions():
    """Get the list of tool functions for the agent."""
    return [
        create_fitness_plan_tool,
        update_user_profile_tool,
        get_user_profile_tool,
    ]


def get_combined_instructions():
    """Get combined instructions for all tools."""
    return """
AVAILABLE TOOLS:

1. create_fitness_plan_tool: Create a personalized fitness plan for the user
   - Use this when the user asks for a fitness plan or workout routine
   - Include both training and meal planning
   - Consider the user's profile, goals, and available equipment

2. update_user_profile_tool: Update the user's profile information
   - Use this to store user information like age, fitness level, goals, equipment
   - Always update the profile when users provide personal information

3. get_user_profile_tool: Get the current user profile information
   - Use this to check what information you already have about the user
   - Helps avoid asking for information you already know

TOOL USAGE GUIDELINES:
- Always check the user profile first when creating plans
- Update the profile whenever users provide new information
- Create comprehensive plans that include both training and nutrition
- Consider user limitations, equipment, and preferences
"""


@function_tool
def create_fitness_plan_tool(
    plan_name: str,
    goal: str,
    description: str,
    training_plan_data: Dict[str, Any],
    meal_plan_data: Dict[str, Any],
    start_date: Optional[str] = None,
    target_date: Optional[str] = None
) -> str:
    """
    Create a comprehensive fitness plan for the user.
    
    Args:
        plan_name: Name for the fitness plan
        goal: Primary goal of the fitness plan
        description: Overview of the plan
        training_plan_data: Training plan structure with periods, splits, and exercises
        meal_plan_data: Meal plan with periods and daily templates
        start_date: Plan start date (YYYY-MM-DD format)
        target_date: Target completion date (YYYY-MM-DD format)
    
    Returns:
        Confirmation message about the created plan
    """
    try:
        # Get or create user session
        session = SessionManager.get_or_create_session()
        
        # Parse dates
        parsed_start_date = date.fromisoformat(start_date) if start_date else date.today()
        parsed_target_date = date.fromisoformat(target_date) if target_date else None
        
        # Create fitness plan (simplified - in real implementation would use proper model parsing)
        fitness_plan = FitnessPlan(
            name=plan_name,
            goal=goal,
            description=description,
            training_plan=training_plan_data,  # Would need proper model conversion
            meal_plan=meal_plan_data,  # Would need proper model conversion
            start_date=parsed_start_date,
            target_date=parsed_target_date
        )
        
        # Store in session
        session.set_fitness_plan(fitness_plan)
        
        logger.info(f"Created fitness plan: {plan_name}")
        return f"✅ Created your personalized fitness plan '{plan_name}'! The plan starts on {parsed_start_date} and focuses on {goal}. You can now start following your training and nutrition guidelines."
        
    except Exception as e:
        logger.error(f"Error creating fitness plan: {str(e)}")
        return f"❌ Sorry, I encountered an error creating your fitness plan: {str(e)}"


@function_tool
def update_user_profile_tool(
    name: Optional[str] = None,
    age: Optional[int] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    fitness_level: Optional[str] = None,
    goals: Optional[List[str]] = None,
    medical_conditions: Optional[List[str]] = None,
    equipment_available: Optional[List[str]] = None
) -> str:
    """
    Update the user's profile information.
    
    Args:
        name: User's name
        age: User's age
        height: Height in cm or inches
        weight: Weight in kg or lbs
        fitness_level: Fitness level (beginner, intermediate, advanced)
        goals: List of fitness goals
        medical_conditions: Any medical conditions to consider
        equipment_available: Available exercise equipment
    
    Returns:
        Confirmation message about the profile update
    """
    try:
        # Get or create user session
        session = SessionManager.get_or_create_session()
        
        # Update profile fields that were provided
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if age is not None:
            update_data['age'] = age
        if height is not None:
            update_data['height'] = height
        if weight is not None:
            update_data['weight'] = weight
        if fitness_level is not None:
            update_data['fitness_level'] = fitness_level
        if goals is not None:
            update_data['goals'] = goals
        if medical_conditions is not None:
            update_data['medical_conditions'] = medical_conditions
        if equipment_available is not None:
            update_data['equipment_available'] = equipment_available
        
        session.update_profile(**update_data)
        
        updated_fields = list(update_data.keys())
        logger.info(f"Updated user profile fields: {updated_fields}")
        
        return f"✅ Updated your profile! I've recorded your {', '.join(updated_fields)}. This will help me create better personalized recommendations for you."
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return f"❌ Sorry, I encountered an error updating your profile: {str(e)}"


@function_tool
def get_user_profile_tool() -> str:
    """
    Get the current user profile information.
    
    Returns:
        Summary of the user's current profile
    """
    try:
        session = SessionManager.get_current_session()
        if not session:
            return "No user profile found. Please provide some information about yourself to get started!"
        
        profile = session.profile
        profile_info = []
        
        if profile.name:
            profile_info.append(f"Name: {profile.name}")
        if profile.age:
            profile_info.append(f"Age: {profile.age}")
        if profile.fitness_level:
            profile_info.append(f"Fitness Level: {profile.fitness_level}")
        if profile.goals:
            profile_info.append(f"Goals: {', '.join(profile.goals)}")
        if profile.equipment_available:
            profile_info.append(f"Available Equipment: {', '.join(profile.equipment_available)}")
        if profile.medical_conditions:
            profile_info.append(f"Medical Considerations: {', '.join(profile.medical_conditions)}")
        
        if not profile_info:
            return "Your profile is empty. Please tell me about your fitness goals, experience level, and available equipment so I can help you better!"
        
        return "📋 Your current profile:\n" + "\n".join(f"• {info}" for info in profile_info)
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return f"❌ Sorry, I encountered an error retrieving your profile: {str(e)}"


__all__ = ['get_tool_functions', 'get_combined_instructions', 'ScheduledTrainingDay']
