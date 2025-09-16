"""
Fitness agent tools with grouped function and prompt definitions.
"""
import logging
from typing import Optional, Any, Dict, List
from dataclasses import dataclass
from datetime import date, timedelta
from agents import function_tool, RunContextWrapper

from .fitness_plan_models import FitnessPlan
from .training_plan_models import TrainingDay, IntensityLevel
from .user_session import SessionManager, UserProfile

logger = logging.getLogger(__name__)


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
    logger.info(f"Building fitness schedule for plan: {fitness_plan.name}")
    
    if start_date is None:
        start_date = fitness_plan.start_date or date.today()
    logger.info(f"Schedule start date: {start_date}")
    
    # Use target_date as end_date if available
    end_date = fitness_plan.target_date
    logger.info(f"Schedule end date: {end_date}")
    
    schedule = []
    current_date = start_date
    logger.info(f"Training plan has {len(fitness_plan.training_plan.training_periods)} periods")
    
    # Process training periods in order
    for period_idx, period in enumerate(fitness_plan.training_plan.training_periods):
        logger.info(f"Processing period {period_idx + 1}: {period.name}")
        
        # Use period's start_date if provided, otherwise use current_date
        period_start_date = period.start_date if period.start_date else current_date
        period_current_date = period_start_date
        logger.info(f"Period {period_idx + 1} starts on: {period_start_date}")
        
        # Determine this period's end date
        next_period = None
        if period_idx < len(fitness_plan.training_plan.training_periods) - 1:
            next_period = fitness_plan.training_plan.training_periods[period_idx + 1]
            period_end_date = next_period.start_date - timedelta(days=1)
            logger.info(f"Period {period_idx + 1} ends on: {period_end_date} (before next period)")
        else:
            # Last period goes until the plan's target date
            period_end_date = end_date
            logger.info(f"Period {period_idx + 1} ends on: {period_end_date} (plan end date)")
        
        # Get the training split for this period
        training_split = period.training_split
        logger.info(f"Period {period_idx + 1} using split: {training_split.name} with {len(training_split.training_days)} days")
        
        # Calculate how many days this split's cycle is
        week_number = 1
        
        # Continue cycling through the split until we reach the period end date or plan end date
        while (period_end_date is None or period_current_date <= period_end_date) and (end_date is None or period_current_date <= end_date):
            logger.debug(f"Starting week {week_number} of {training_split.name} on {period_current_date}")
            cycle_completed = True
            
            for day_idx, training_day in enumerate(training_split.training_days):
                # Stop if we've reached the period end date or plan end date
                if (period_end_date and period_current_date > period_end_date) or (end_date and period_current_date > end_date):
                    logger.debug(f"Stopping at {period_current_date} - reached end date")
                    cycle_completed = False
                    break
                    
                scheduled_day = ScheduledTrainingDay(
                    date=period_current_date,
                    training_day=training_day,
                    split_name=training_split.name,
                    week_number=week_number,
                    day_in_week=day_idx + 1
                )
                schedule.append(scheduled_day)
                logger.debug(f"Scheduled {training_day.name} on {period_current_date} (Week {week_number}, Day {day_idx + 1})")
                period_current_date += timedelta(days=1)
            
            # Only increment week number if we completed a full cycle
            if cycle_completed:
                week_number += 1
                logger.debug(f"Completed full cycle, moving to week {week_number}")
        
        # Update current_date for the next period
        current_date = period_current_date
        logger.info(f"Period {period_idx + 1} completed. Next period will start from: {current_date}")
    
    logger.info(f"Schedule built successfully with {len(schedule)} scheduled days")
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
        
        # Check if this is a rest day (no exercises or rest intensity)
        is_rest_day = (not scheduled_day.training_day.exercises or 
                      len(scheduled_day.training_day.exercises) == 0 or
                      (scheduled_day.training_day.intensity and scheduled_day.training_day.intensity.value == "rest"))
        
        if is_rest_day:
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
    """Save a completed fitness plan to the user session for display in the UI.

    Args:
        fitness_plan: A fully completed FitnessPlan object with name, training_plan, and meal_plan
    """
    try:
        logger.info(f"Creating fitness plan: {fitness_plan.name}")
        logger.info(f"Plan goal: {fitness_plan.goal}")
        logger.info(f"Plan start date: {fitness_plan.start_date}")
        logger.info(f"Plan target date: {fitness_plan.target_date}")
        
        # Get or create user session
        logger.debug("Getting or creating user session")
        session = SessionManager.get_or_create_session()
        logger.info(f"User session obtained: {session.session_id}")
        
        # Save the fitness plan to the user session
        logger.debug("Saving fitness plan to user session")
        session.set_fitness_plan(fitness_plan)
        logger.info("Fitness plan saved to session successfully")
        
        # Build the schedule from the fitness plan
        logger.info("Building fitness schedule from plan")
        schedule = build_fitness_schedule(fitness_plan)
        logger.info(f"Schedule built with {len(schedule)} days")
        
        # Save the schedule to the user session
        logger.debug("Saving schedule to user session")
        session.set_schedule(schedule)
        logger.info("Schedule saved to session successfully")
        
        logger.debug("Formatting schedule summary")
        schedule_summary = format_schedule_summary(schedule)
        logger.debug("Schedule summary formatted successfully")
        
        # Format the plan for display
        logger.debug("Formatting plan for display")
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
            logger.info(f"Plan duration: {duration_days} days ({duration_weeks} weeks)")
        else:
            duration_text = "customized"
            logger.info("Plan duration: customized (no specific dates provided)")
        
        logger.info("Fitness plan creation completed successfully")
        return f"I've created and saved your personalized fitness plan with a {duration_text} schedule:\n\n{formatted_plan}\n\nThis plan has been tailored specifically for your requirements and is now available in the fitness plan section below. Please consult with a healthcare provider before starting any new fitness program."
        
    except Exception as e:
        logger.error(f"Error creating fitness plan: {str(e)}", exc_info=True)
        return f"I apologize, but I encountered an error while saving your fitness plan: {str(e)}. Please try again or contact support if the issue persists."


@function_tool
async def get_user_profile(
    ctx: RunContextWrapper[Any],
) -> str:
    """Get the current user's profile information.

    Returns:
        String describing the user's profile or a message if no profile exists
    """
    try:
        session = SessionManager.get_current_session()
        
        if not session:
            return "No user session found. Your profile information will be saved as we talk."
        
        profile = session.profile
        
        if not any([profile.name, profile.age, profile.fitness_level, profile.goals]):
            return "No profile information saved yet. Tell me about yourself - your fitness level, goals, and preferences - and I'll remember them for future conversations."
        
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
        
        return "Here's your current profile:\n\n" + "\n".join(profile_info)
        
    except Exception as e:
        return f"I encountered an error while retrieving your profile: {str(e)}. Please try again."


@function_tool
async def update_user_profile(
    ctx: RunContextWrapper[Any],
    name: Optional[str] = None,
    age: Optional[int] = None,
    fitness_level: Optional[str] = None,
    goals: Optional[List[str]] = None,
    equipment_available: Optional[List[str]] = None,
) -> str:
    """Update the user's profile information.

    Args:
        name: User's name
        age: User's age
        fitness_level: User's fitness level (beginner, intermediate, advanced)
        goals: List of fitness goals
        equipment_available: List of available equipment
    """
    try:
        session = SessionManager.get_or_create_session()
        
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if age is not None:
            update_data['age'] = age
        if fitness_level is not None:
            update_data['fitness_level'] = fitness_level
        if goals is not None:
            update_data['goals'] = goals
        if equipment_available is not None:
            update_data['equipment_available'] = equipment_available
        
        session.update_profile(**update_data)
        
        # Note: In a production system, you might want to notify the agent
        # instance that the profile has been updated so it can refresh its context
        
        return "I've updated your profile information. This will help me create better personalized fitness plans for you."
        
    except Exception as e:
        return f"I encountered an error while updating your profile: {str(e)}. Please try again."


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
        # Get the current user session
        session = SessionManager.get_current_session()
        
        if not session:
            return "No user session found. Please create a fitness plan first."
        
        # First try to get the stored schedule
        schedule = session.get_schedule()
        
        if not schedule:
            # If no stored schedule, try to build it from the fitness plan
            fitness_plan = session.get_fitness_plan()
            
            if not fitness_plan:
                return "No fitness plan is currently available. Please create a fitness plan first."
            
            # Build and store the schedule
            schedule = build_fitness_schedule(fitness_plan)
            session.set_schedule(schedule)
        
        # Format the schedule
        schedule_summary = format_schedule_summary(schedule, days_ahead)
        
        return f"Here's your upcoming training schedule:\n\n{schedule_summary}"
        
    except Exception as e:
        return f"I encountered an error while retrieving your training schedule: {str(e)}. Please try again."


@function_tool
async def get_schedule_data(
    ctx: RunContextWrapper[Any],
) -> List[ScheduledTrainingDay]:
    """Get the raw training schedule data for calendar display.

    Returns:
        List of ScheduledTrainingDay objects for calendar interface
    """
    try:
        # Get the current user session
        session = SessionManager.get_current_session()
        
        if not session:
            raise Exception("No user session found")
        
        # Get the stored schedule
        schedule = session.get_schedule()
        
        if not schedule:
            # If no stored schedule, try to build it from the fitness plan
            fitness_plan = session.get_fitness_plan()
            
            if not fitness_plan:
                raise Exception("No fitness plan available")
            
            # Build and store the schedule
            schedule = build_fitness_schedule(fitness_plan)
            session.set_schedule(schedule)
        
        return schedule
        
    except Exception as e:
        logger.error(f"Error getting schedule data: {str(e)}", exc_info=True)
        return []


@function_tool
async def clear_user_session(
    ctx: RunContextWrapper[Any],
) -> str:
    """Clear all user session data including profile and fitness plans.

    Returns:
        Confirmation message
    """
    try:
        session = SessionManager.get_current_session()
        
        if not session:
            return "No user session found to clear."
        
        # Clear all user data including schedule
        session.clear_all_data()
        
        return "I've cleared all your session data including your profile, fitness plans, and training schedule. We can start fresh whenever you're ready!"
        
    except Exception as e:
        return f"I encountered an error while clearing your session: {str(e)}. Please try again."


# Tool configurations with their associated prompt instructions
FITNESS_TOOLS = {
    "create_fitness_plan": FunctionToolConfig(
        function=create_fitness_plan,
        prompt_instructions="""
        When the user requests a fitness plan, use the create_fitness_plan tool with a fully completed FitnessPlan object.

        Fitness Plans are made up of Training Plans and Meal Plans that have a start and end date.
        If no start date is specified, assume the plan starts today.
        If no end date is given by the user assume they want a plan to be in better shape in 3 months.

        The FitnessPlan object must include:
        - name: A descriptive name for the fitness plan
        - goal: The primary fitness goal (should be specific and measurable)
        - description: Comprehensive overview of the plan and expected outcomes
        - training_plan: A TrainingPlan object with periodized phases that includes:
          * name: Name that reflects the plan's focus and target event
          * description: Comprehensive overview including training philosophy, periodization strategy, target audience, expected timeline, and how the phases progress toward the goal
          * training_periods: Ordered list of TrainingPeriod objects representing different phases:
            - Each period should have a name (e.g., 'Base Phase', 'Advanced Phase', 'Preparation Phase')
            - Include start_date for each period
            - Include intensity level (rest, light, moderate, heavy, max_effort)
            - Each period contains a training_split with training_days that include exercises
            - Follow periodization principles: typically base building → peak training → recovery for optimum performance at events
            - Each phase should build on the previous with appropriate progression
        - meal_plan: Detailed nutrition guidance including meal suggestions, macronutrient targets, and eating schedule. Should be practical and specific to the fitness goals.
        - start_date: When the plan should begin (defaults to today)
        - target_date: The target completion date or milestone date for the fitness plan

        Training Structure:
        - TrainingPeriod contains a TrainingSplit
        - TrainingSplit contains multiple TrainingDay objects
        - TrainingDay contains multiple Exercise objects
        - Each Exercise should have name, description, and appropriate fields (sets, reps, duration, distance, intensity)
        - Include rest days in the training split as needed

        Create periodized plans that progress intelligently toward the goal:
        - For events (hikes, competitions): Use base building → strength → peak → taper progression
        - For aesthetic goals (summer body): Use muscle building → strength → cutting/definition phases
        - For general fitness: Use base building → strength → maintenance cycles
        
        This tool automatically builds a date-based schedule from the periodized phases and saves the plan.

        Do not read the plan back to the user in the conversation. The user can already see it in the UI component.

        In one or two sentences, let the user know the plan has been created, and ask the user if they want to make any adjustments.
        """
    ),
    "get_user_profile": FunctionToolConfig(
        function=get_user_profile,
        prompt_instructions="""
        Use this tool only when:
        1. The user explicitly asks to see their profile information
        2. You need to refresh your memory in very long conversations (15+ exchanges)
        3. You suspect the user's profile may have been updated since the conversation started
        
        In most cases, you should already have the user's profile information available in your system context.
        This tool is primarily for displaying profile information to the user or refreshing context in extended conversations.
        """
    ),
    "update_user_profile": FunctionToolConfig(
        function=update_user_profile,
        prompt_instructions="""
        Use this tool when the user provides information about themselves that should be saved for future reference.
        
        This includes their name, age, fitness level (beginner/intermediate/advanced), goals, or available equipment.
        
        You can update any combination of profile fields - only pass the parameters that have new information.
        """
    ),
    "get_training_schedule": FunctionToolConfig(
        function=get_training_schedule,
        prompt_instructions="""
        Use this tool when the user asks about their upcoming workouts, training schedule, or what they should do on specific days.
        
        The tool shows the next 14 days by default, but you can specify a different number of days if the user requests it.
        
        This tool requires that a fitness plan has already been created.
        """
    ),
    "get_schedule_data": FunctionToolConfig(
        function=get_schedule_data,
        prompt_instructions="""
        Use this tool to get raw schedule data for calendar interfaces or when the system needs access to the ScheduledTrainingDay objects directly.
        
        This returns the actual schedule objects rather than formatted text, making it suitable for programmatic use.
        
        This tool requires that a fitness plan has already been created.
        """
    ),
    "clear_user_session": FunctionToolConfig(
        function=clear_user_session,
        prompt_instructions="""
        Use this tool when the user wants to start completely fresh or clear all their data.
        
        This will clear:
        - User profile information
        - Current fitness plan
        - Workout logs
        - All measurements
        
        Only use this when the user explicitly requests to clear/reset/start over with all their data.
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
