"""
Fitness agent tools with grouped function and prompt definitions.
"""
from typing import Optional, Any, Dict, List
from dataclasses import dataclass
from datetime import date, timedelta
from agents import function_tool, RunContextWrapper

from .models import FitnessPlan
from .structured_output_models import TrainingDay


@dataclass
class FunctionToolConfig:
    """Configuration for a function tool including its prompt instructions."""
    function: callable
    prompt_instructions: str


@dataclass
class ScheduledTrainingDay:
    """A training day with an assigned date."""
    date: date
    training_day: TrainingDay
    split_name: str
    week_number: int
    day_in_week: int


def build_fitness_schedule(fitness_plan: FitnessPlan, start_date: Optional[date] = None) -> List[ScheduledTrainingDay]:
    """
    Build a date-based schedule from a fitness plan.
    
    Args:
        fitness_plan: The FitnessPlan object to create a schedule from
        start_date: Optional start date, defaults to fitness_plan.start_date or today
    
    Returns:
        List of ScheduledTrainingDay objects with assigned dates
    """
    if start_date is None:
        start_date = fitness_plan.start_date or date.today()
    
    # Use target_date as end_date if available
    end_date = fitness_plan.target_date
    
    schedule = []
    current_date = start_date
    
    # Sort splits by order to ensure proper sequencing
    sorted_splits = sorted(fitness_plan.training_plan.training_plan_splits, key=lambda x: x.order)
    
    for split in sorted_splits:
        # Use split's start_date if provided, otherwise use current_date
        split_start_date = split.start_date if split.start_date else current_date
        split_current_date = split_start_date
        
        # Calculate how many days this split's cycle is
        days_per_cycle = len(split.training_days)
        week_number = 1
        
        # Continue cycling through the split until we reach the end date or run out of splits
        while (end_date is None or split_current_date <= end_date):
            for day_idx, training_day in enumerate(split.training_days):
                # Stop if we've reached the end date
                if end_date and split_current_date > end_date:
                    break
                    
                scheduled_day = ScheduledTrainingDay(
                    date=split_current_date,
                    training_day=training_day,
                    split_name=split.name,
                    week_number=week_number,
                    day_in_week=day_idx + 1
                )
                schedule.append(scheduled_day)
                split_current_date += timedelta(days=1)
            
            # Increment week number after completing a full cycle
            week_number += 1
            
            # If this is the last split and we don't have an end date, break after one cycle
            # to avoid infinite loops
            if end_date is None and split == sorted_splits[-1]:
                break
        
        # Update current_date for the next split (if no explicit start_date is set for next split)
        current_date = split_current_date
    
    return schedule


def format_schedule_summary(schedule: List[ScheduledTrainingDay], days_to_show: int = 14) -> str:
    """
    Format the schedule into a readable summary showing upcoming training days.
    
    Args:
        schedule: List of ScheduledTrainingDay objects
        days_to_show: Number of upcoming days to display
    
    Returns:
        Formatted string showing the schedule
    """
    if not schedule:
        return "No scheduled training days found."
    
    # Show only upcoming days (from today forward)
    today = date.today()
    upcoming_days = [day for day in schedule if day.date >= today][:days_to_show]
    
    if not upcoming_days:
        return "No upcoming training days scheduled."
    
    summary_lines = ["**Upcoming Training Schedule:**"]
    current_week = None
    
    for scheduled_day in upcoming_days:
        # Add week separator
        week_key = f"{scheduled_day.split_name} - Week {scheduled_day.week_number}"
        if week_key != current_week:
            summary_lines.append(f"\n*{week_key}*")
            current_week = week_key
        
        # Format the day
        day_str = scheduled_day.date.strftime("%a, %b %d")
        intensity_str = f" ({scheduled_day.training_day.intensity.value})" if scheduled_day.training_day.intensity else ""
        
        if scheduled_day.training_day.rest_day:
            summary_lines.append(f"• {day_str}: {scheduled_day.training_day.name}")
        else:
            exercise_count = len(scheduled_day.training_day.exercises) if scheduled_day.training_day.exercises else 0
            summary_lines.append(f"• {day_str}: {scheduled_day.training_day.name}{intensity_str} ({exercise_count} exercises)")
    
    return "\n".join(summary_lines)


@function_tool
async def create_fitness_plan(
    ctx: RunContextWrapper[Any],
    fitness_plan: FitnessPlan,
) -> str:
    """Save a completed fitness plan to the FitnessAgent for display in the UI.

    Args:
        fitness_plan: A fully completed FitnessPlan object with name, training_plan, and meal_plan
    """
    try:
        # Import here to avoid circular imports
        from .fitness_agent import FitnessAgent
        
        # Save the fitness plan to the agent class
        FitnessAgent.set_latest_fitness_plan(fitness_plan)
        
        # Build the schedule from the fitness plan
        schedule = build_fitness_schedule(fitness_plan)
        schedule_summary = format_schedule_summary(schedule)
        
        # Format the plan for display
        formatted_plan = f"""**{fitness_plan.name}**

**Goal:** {fitness_plan.goal}

**Training Plan:** {fitness_plan.training_plan.name}
{fitness_plan.training_plan.description}

{schedule_summary}

**Meal Plan:**
{fitness_plan.meal_plan}"""
        
        # Calculate duration for display
        if fitness_plan.target_date and fitness_plan.start_date:
            duration_days = (fitness_plan.target_date - fitness_plan.start_date).days
            duration_weeks = duration_days // 7
            duration_text = f"{duration_weeks}-week"
        else:
            duration_text = "customized"
        
        return f"I've created and saved your personalized fitness plan with a {duration_text} schedule:\n\n{formatted_plan}\n\nThis plan has been tailored specifically for your requirements and is now available in the fitness plan section below. Please consult with a healthcare provider before starting any new fitness program."
        
    except Exception as e:
        return f"I apologize, but I encountered an error while saving your fitness plan: {str(e)}. Please try again or contact support if the issue persists."


@function_tool
async def get_training_schedule(
    ctx: RunContextWrapper[Any],
    days_ahead: int = 14,
) -> str:
    """Get the upcoming training schedule from the current fitness plan.

    Args:
        days_ahead: Number of days ahead to show in the schedule (default: 14)
    """
    try:
        # Import here to avoid circular imports
        from .fitness_agent import FitnessAgent
        
        # Get the current fitness plan
        fitness_plan = FitnessAgent.get_latest_fitness_plan()
        
        if not fitness_plan:
            return "No fitness plan is currently available. Please create a fitness plan first."
        
        # Build and format the schedule
        schedule = build_fitness_schedule(fitness_plan)
        schedule_summary = format_schedule_summary(schedule, days_ahead)
        
        return f"Here's your upcoming training schedule:\n\n{schedule_summary}"
        
    except Exception as e:
        return f"I encountered an error while retrieving your training schedule: {str(e)}. Please try again."


# Tool configurations with their associated prompt instructions
FITNESS_TOOLS = {
    "create_fitness_plan": FunctionToolConfig(
        function=create_fitness_plan,
        prompt_instructions="""
        When the user requests a fitness plan, use the create_fitness_plan tool with a fully completed FitnessPlan object.
        
        The FitnessPlan object must include:
        - name: A descriptive name for the fitness plan
        - goal: The primary fitness goal
        - training_plan: Detailed training/workout information with splits and days
        - meal_plan: Comprehensive nutrition and meal planning details
        - start_date: When the plan should begin (defaults to today)
        - total_duration_weeks: Total duration of the plan

        This tool automatically builds a date-based schedule and saves the plan to the FitnessAgent class.

        Do not read the plan back to the user in the conversation. The user can already see it in the UI component.

        In one or two sentences, let the user know the plan has been created, and ask the user if they want to make any adjustments.
        """
    ),
    "get_training_schedule": FunctionToolConfig(
        function=get_training_schedule,
        prompt_instructions="""
        Use this tool when the user asks about their upcoming workouts, training schedule, or what they should do on specific days.
        
        The tool shows the next 14 days by default, but you can specify a different number of days if the user requests it.
        
        This tool requires that a fitness plan has already been created.
        """
    )
}


def get_tool_functions() -> List[callable]:
    """Get all function tools for the agent."""
    return [config.function for config in FITNESS_TOOLS.values()]


def get_combined_instructions() -> str:
    """Get combined prompt instructions for all tools."""
    instructions = []
    for tool_name, config in FITNESS_TOOLS.items():
        instructions.append(f"## {tool_name.replace('_', ' ').title()}")
        instructions.append(config.prompt_instructions)
        instructions.append("")
    
    return "\n".join(instructions)
