"""
Response formatting utilities for the fitness app.
"""
import re
import logging
from typing import Any, Generator, List, Dict

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Handles formatting of various response types."""
    
    @staticmethod
    def format_fitness_plan(plan_obj: Any, style: str = "default") -> str:
        """
        Format a FitnessPlan object into a structured markdown string
        
        Args:
            plan_obj: The fitness plan object
            style: Formatting style ("default", "minimal", "detailed")
            
        Returns:
            Formatted markdown string
        """
        try:
            # First, try to handle structured FitnessPlan objects
            if hasattr(plan_obj, 'name') and hasattr(plan_obj, 'training_plan'):
                return ResponseFormatter._format_structured_fitness_plan(plan_obj, style)
            
            # Handle string representation of structured objects  
            elif isinstance(plan_obj, str) and 'training_plan_splits=' in plan_obj:
                return ResponseFormatter._format_structured_plan_string(plan_obj, style)
            
            # Legacy handling for older format objects
            elif not (hasattr(plan_obj, 'name') and 
                    hasattr(plan_obj, 'training_plan') and 
                    hasattr(plan_obj, 'meal_plan')):
                # Try to parse as string if it's not a proper object
                if isinstance(plan_obj, str):
                    # First try to parse as markdown-formatted plan (for Groq models)
                    parsed_plan = ResponseFormatter.parse_markdown_fitness_plan(plan_obj)
                    if parsed_plan:
                        return parsed_plan
                    # Fallback to original string parsing
                    parsed_plan = ResponseFormatter.parse_fitness_plan_from_string(plan_obj)
                    if parsed_plan and "**Fitness Plan**" not in parsed_plan[:50]:
                        return parsed_plan
                    # CATCH-ALL: If all parsing fails, display the raw content formatted nicely
                    return ResponseFormatter.format_raw_fitness_content(plan_obj)
                else:
                    return f"**Fitness Plan**\n\n{str(plan_obj)}"
            
            # Legacy formatting for basic objects
            if style == "minimal":
                return f"""**{plan_obj.name}**

**Training:** {plan_obj.training_plan}

**Meals:** {plan_obj.meal_plan}"""
            
            elif style == "detailed":
                return f"""# 🏋️ {plan_obj.name}

## 💪 Training Plan
{plan_obj.training_plan}

## 🥗 Meal Plan  
{plan_obj.meal_plan}

## 📊 Additional Information
- Plan created with AI assistance
- Customize as needed for your preferences
- Consult healthcare providers for medical advice

---
*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"""
            
            else:  # default style
                return f"""# 🏋️ {plan_obj.name}

## 💪 Training Plan
{plan_obj.training_plan}

## 🥗 Meal Plan
{plan_obj.meal_plan}

---
*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"""
            
        except Exception as e:
            logger.error(f"Error formatting fitness plan: {str(e)}")
            return f"**Fitness Plan**\n\nI created a fitness plan for you, but encountered an error while formatting it. Here's the raw content:\n\n{str(plan_obj)}"

    @staticmethod
    def _format_structured_fitness_plan(plan_obj: Any, style: str = "default") -> str:
        """Format a structured FitnessPlan object with proper training plan formatting."""
        try:
            # Extract basic plan info
            plan_name = getattr(plan_obj, 'name', 'Fitness Plan')
            plan_goal = getattr(plan_obj, 'goal', '')
            plan_description = getattr(plan_obj, 'description', '')
            meal_plan = getattr(plan_obj, 'meal_plan', '')
            
            # Format header
            formatted = f"# 🏋️ {plan_name}\n\n"
            
            if plan_goal:
                formatted += f"**🎯 Goal:** {plan_goal}\n\n"
            
            if plan_description:
                formatted += f"**📋 Overview:** {plan_description}\n\n"
            
            # Format training plan
            training_plan = getattr(plan_obj, 'training_plan', None)
            if training_plan:
                formatted += "## 💪 Training Plan\n\n"
                formatted += ResponseFormatter._format_training_plan_object(training_plan)
            
            # Format meal plan
            if meal_plan:
                formatted += "\n## 🥗 Meal Plan\n\n"
                formatted += f"{meal_plan}\n\n"
            
            # Add footer based on style
            if style in ["detailed", "default"]:
                formatted += "## 📊 Additional Information\n\n"
                formatted += "- Plan created with AI assistance\n"
                formatted += "- Customize as needed for your preferences\n"  
                formatted += "- Consult healthcare providers for medical advice\n\n"
                formatted += "---\n"
                formatted += "*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting structured fitness plan: {str(e)}")
            return f"**Error Formatting Plan**\n\n{str(e)}"

    @staticmethod
    def _format_training_plan_object(training_plan: Any) -> str:
        """Format a TrainingPlan object with proper structure."""
        try:
            formatted = ""
            
            # Get training plan details
            plan_name = getattr(training_plan, 'name', 'Training Plan')
            plan_description = getattr(training_plan, 'description', '')
            
            formatted += f"**{plan_name}**\n\n"
            if plan_description:
                formatted += f"{plan_description}\n\n"
            
            # Format training splits
            training_splits = getattr(training_plan, 'training_plan_splits', [])
            for split in training_splits:
                formatted += ResponseFormatter._format_training_split_object(split)
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting training plan object: {str(e)}")
            return f"Error formatting training plan: {str(e)}"

    @staticmethod
    def _format_training_split_object(split: Any) -> str:
        """Format a TrainingPlanSplit object."""
        try:
            formatted = ""
            
            # Get split details
            split_name = getattr(split, 'name', 'Training Split')
            split_description = getattr(split, 'description', '')
            
            formatted += f"### 📅 {split_name}\n\n"
            if split_description:
                formatted += f"{split_description}\n\n"
            
            # Format training days
            training_days = getattr(split, 'training_days', [])
            for day in training_days:
                formatted += ResponseFormatter._format_training_day_object(day)
                formatted += "\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting training split object: {str(e)}")
            return f"Error formatting training split: {str(e)}"

    @staticmethod 
    def _format_training_day_object(day: Any) -> str:
        """Format a TrainingDay object."""
        try:
            formatted = ""
            
            # Get day details
            day_name = getattr(day, 'name', 'Training Day')
            day_description = getattr(day, 'description', '')
            day_order = getattr(day, 'order_number', '')
            is_rest_day = getattr(day, 'rest_day', False)
            day_intensity = getattr(day, 'intensity', None)
            
            # Format day header
            day_emoji = "😴" if is_rest_day else "💪"
            formatted += f"#### {day_emoji} Day {day_order}: {day_name}\n\n"
            
            if day_description:
                formatted += f"*{day_description}*\n\n"
            
            if day_intensity and not is_rest_day:
                intensity_emojis = {
                    'light': '🟢', 'LIGHT': '🟢',
                    'moderate': '🟡', 'MODERATE': '🟡',
                    'heavy': '🔴', 'HEAVY': '🔴',
                    'max_effort': '🔥', 'MAX_EFFORT': '🔥'
                }
                # Handle both enum objects and string representations
                intensity_str = str(day_intensity).replace('IntensityLevel.', '').replace('<', '').replace('>', '').split(':')[0]
                intensity_emoji = intensity_emojis.get(intensity_str, '⚪')
                formatted += f"**Intensity:** {intensity_emoji} {intensity_str.title()}\n\n"
            
            # Format exercises
            if not is_rest_day:
                exercises = getattr(day, 'exercises', [])
                if exercises:
                    formatted += "**Exercises:**\n\n"
                    for i, exercise in enumerate(exercises, 1):
                        formatted += ResponseFormatter._format_exercise_object(exercise, i)
                        formatted += "\n"
            else:
                formatted += "**Rest Day** - Focus on recovery, light stretching, or gentle activities.\n\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting training day object: {str(e)}")
            return f"Error formatting training day: {str(e)}"

    @staticmethod
    def _format_exercise_object(exercise: Any, number: int) -> str:
        """Format an Exercise object."""
        try:
            # Get exercise details
            name = getattr(exercise, 'name', 'Exercise')
            description = getattr(exercise, 'description', '')
            sets = getattr(exercise, 'sets', None)
            reps = getattr(exercise, 'reps', None)
            duration = getattr(exercise, 'duration', None)
            intensity = getattr(exercise, 'intensity', None)
            
            formatted = f"{number}. **{name}**\n"
            
            # Add sets/reps/duration info
            workout_details = []
            if sets:
                workout_details.append(f"{sets} sets")
            if reps:
                workout_details.append(f"{reps} reps")
            if duration:
                workout_details.append(f"{duration}s")
            
            if workout_details:
                formatted += f"   *{' × '.join(workout_details)}*"
                
            if intensity:
                intensity_emojis = {
                    'light': '🟢', 'LIGHT': '🟢',
                    'moderate': '🟡', 'MODERATE': '🟡',
                    'heavy': '🔴', 'HEAVY': '🔴',
                    'max_effort': '🔥', 'MAX_EFFORT': '🔥'
                }
                # Handle both enum objects and string representations
                intensity_str = str(intensity).replace('IntensityLevel.', '').replace('<', '').replace('>', '').split(':')[0]
                intensity_emoji = intensity_emojis.get(intensity_str, '⚪')
                formatted += f" - {intensity_emoji} {intensity_str.title()}"
            
            formatted += "\n"
            
            if description:
                formatted += f"   *{description}*\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting exercise object: {str(e)}")
            return f"Error formatting exercise: {str(e)}"

    @staticmethod
    def _format_structured_plan_string(plan_str: str, style: str = "default") -> str:
        """Format a string representation of a structured fitness plan."""
        try:
            import re
            
            # Extract plan name
            name_match = re.search(r"🏋️\s*([^\n]*?)Training Plan", plan_str)
            if not name_match:
                name_match = re.search(r"name='([^']*)'", plan_str)
            plan_name = name_match.group(1).strip() if name_match else "Fitness Plan"
            
            # Extract meal plan section
            meal_match = re.search(r"🥗 Meal Plan\n(.*?)(?=📊|$)", plan_str, re.DOTALL)
            meal_plan = meal_match.group(1).strip() if meal_match else ""
            
            # Extract training plan section with structured data
            formatted = f"# 🏋️ {plan_name}\n\n"
            
            # Parse and format the structured training data
            training_match = re.search(r"training_plan_splits=\[(.*?)\]\]", plan_str, re.DOTALL)
            if training_match:
                formatted += "## 💪 Training Plan\n\n"
                formatted += ResponseFormatter._parse_and_format_training_data(training_match.group(1))
            
            # Add meal plan
            if meal_plan:
                formatted += "\n## 🥗 Meal Plan\n\n"
                formatted += f"{meal_plan}\n\n"
            
            # Add footer based on style
            if style in ["detailed", "default"]:
                formatted += "## 📊 Additional Information\n\n"
                formatted += "- Plan created with AI assistance\n"
                formatted += "- Customize as needed for your preferences\n"
                formatted += "- Consult healthcare providers for medical advice\n\n"
                formatted += "---\n"
                formatted += "*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error parsing structured plan string: {str(e)}")
            return f"**Error Parsing Structured Plan**\n\n{str(e)}\n\nRaw content:\n{plan_str}"

    @staticmethod
    def _parse_and_format_training_data(training_data: str) -> str:
        """Parse and format the training data from string representation."""
        try:
            import re
            
            formatted = ""
            
            # Extract split information
            split_name_match = re.search(r"name='([^']*)'", training_data)
            split_name = split_name_match.group(1) if split_name_match else "Weekly Split"
            
            split_desc_match = re.search(r"description='([^']*)'", training_data)
            split_desc = split_desc_match.group(1) if split_desc_match else ""
            
            formatted += f"**{split_name}**\n\n"
            if split_desc:
                formatted += f"{split_desc}\n\n"
            
            # Extract training days
            days_pattern = r"TrainingDay\((.*?)\)(?=, TrainingDay\(|$)"
            days = re.findall(days_pattern, training_data, re.DOTALL)
            
            for day_data in days:
                formatted += ResponseFormatter._parse_and_format_day_data(day_data)
                formatted += "\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error parsing training data: {str(e)}")
            return f"Error parsing training data: {str(e)}"

    @staticmethod
    def _parse_and_format_day_data(day_data: str) -> str:
        """Parse and format a single training day from string representation."""
        try:
            import re
            
            # Extract day details
            name_match = re.search(r"name='([^']*)'", day_data)
            day_name = name_match.group(1) if name_match else "Training Day"
            
            order_match = re.search(r"order_number=(\d+)", day_data)
            day_order = order_match.group(1) if order_match else "1"
            
            desc_match = re.search(r"description='([^']*)'", day_data)
            day_description = desc_match.group(1) if desc_match else ""
            
            rest_match = re.search(r"rest_day=(\w+)", day_data)
            is_rest_day = rest_match and rest_match.group(1) == "True"
            
            intensity_match = re.search(r"intensity=<IntensityLevel\.(\w+):", day_data)
            day_intensity = intensity_match.group(1) if intensity_match else None
            
            # Format day header
            day_emoji = "😴" if is_rest_day else "💪"
            formatted = f"#### {day_emoji} Day {day_order}: {day_name}\n\n"
            
            if day_description:
                formatted += f"*{day_description}*\n\n"
            
            if day_intensity and not is_rest_day:
                intensity_emojis = {
                    'LIGHT': '🟢',
                    'MODERATE': '🟡',
                    'HEAVY': '🔴',
                    'MAX_EFFORT': '🔥'
                }
                intensity_emoji = intensity_emojis.get(day_intensity, '⚪')
                formatted += f"**Intensity:** {intensity_emoji} {day_intensity.title()}\n\n"
            
            # Parse exercises if not rest day
            if not is_rest_day and 'exercises=[' in day_data:
                exercises_match = re.search(r"exercises=\[(.*?)\]", day_data, re.DOTALL)
                if exercises_match:
                    exercises_data = exercises_match.group(1)
                    formatted += "**Exercises:**\n\n"
                    formatted += ResponseFormatter._parse_and_format_exercises(exercises_data)
            elif is_rest_day:
                formatted += "**Rest Day** - Focus on recovery, light stretching, or gentle activities.\n\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error parsing day data: {str(e)}")
            return f"Error parsing day data: {str(e)}"

    @staticmethod
    def _parse_and_format_exercises(exercises_data: str) -> str:
        """Parse and format exercises from string representation."""
        try:
            import re
            
            formatted = ""
            
            # Extract individual exercises
            exercise_pattern = r"Exercise\((.*?)\)(?=, Exercise\(|$)"
            exercises = re.findall(exercise_pattern, exercises_data, re.DOTALL)
            
            for i, exercise_data in enumerate(exercises, 1):
                # Extract exercise details
                name_match = re.search(r"name='([^']*)'", exercise_data)
                name = name_match.group(1) if name_match else "Exercise"
                
                desc_match = re.search(r"description='([^']*)'", exercise_data)
                description = desc_match.group(1) if desc_match else ""
                
                sets_match = re.search(r"sets=(\d+)", exercise_data)
                sets = sets_match.group(1) if sets_match else None
                
                reps_match = re.search(r"reps=(\d+)", exercise_data)
                reps = reps_match.group(1) if reps_match else None
                
                duration_match = re.search(r"duration=(\d+)", exercise_data)
                duration = duration_match.group(1) if duration_match else None
                
                intensity_match = re.search(r"intensity=<IntensityLevel\.(\w+):", exercise_data)
                intensity = intensity_match.group(1) if intensity_match else None
                
                # Format exercise
                formatted += f"{i}. **{name}**\n"
                
                # Add workout details
                workout_details = []
                if sets:
                    workout_details.append(f"{sets} sets")
                if reps:
                    workout_details.append(f"{reps} reps")
                if duration:
                    workout_details.append(f"{duration}s")
                
                if workout_details:
                    formatted += f"   *{' × '.join(workout_details)}*"
                
                if intensity:
                    intensity_emojis = {
                        'LIGHT': '🟢',
                        'MODERATE': '🟡',
                        'HEAVY': '🔴',
                        'MAX_EFFORT': '🔥'
                    }
                    intensity_emoji = intensity_emojis.get(intensity, '⚪')
                    formatted += f" - {intensity_emoji} {intensity.title()}"
                
                formatted += "\n"
                
                if description:
                    formatted += f"   *{description}*\n"
                
                formatted += "\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error parsing exercises: {str(e)}")
            return f"Error parsing exercises: {str(e)}"

    @staticmethod
    def parse_fitness_plan_from_string(plan_str: str) -> str:
        """
        Parse a fitness plan from its string representation
        
        Args:
            plan_str: String representation of a fitness plan object
            
        Returns:
            Formatted markdown string
        """
        try:
            # Extract name - handle both single and double quotes
            name_match = re.search(r"name=['\"]([^'\"]*)['\"]", plan_str)
            name = name_match.group(1) if name_match else "Fitness Plan"
            
            # Extract training plan - handle both list format and simple string format
            training_plan = ""
            
            # Try list format first (with brackets and quotes)
            training_match = re.search(r"training_plan=['\"](\[.*?\])['\"]", plan_str, re.DOTALL)
            if training_match:
                training_raw = training_match.group(1)
                # Clean up the list format
                training_plan = training_raw.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
                training_plan = training_plan.replace(',', '\n').strip()
            else:
                # Try simple string format
                training_match = re.search(r"training_plan=['\"]([^'\"]*)['\"]", plan_str, re.DOTALL)
                if training_match:
                    training_plan = training_match.group(1)
            
            # Extract meal plan - handle both list format and simple string format
            meal_plan = ""
            
            # Try list format first (with brackets and quotes)
            meal_match = re.search(r"meal_plan=['\"](\[.*?\])['\"]", plan_str, re.DOTALL)
            if meal_match:
                meal_raw = meal_match.group(1)
                # Clean up the list format
                meal_plan = meal_raw.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
                meal_plan = meal_plan.replace(',', '\n').strip()
            else:
                # Try simple string format
                meal_match = re.search(r"meal_plan=['\"]([^'\"]*)['\"]", plan_str, re.DOTALL)
                if meal_match:
                    meal_plan = meal_match.group(1)
            
            # Format as markdown
            formatted_plan = f"""# 🏋️ {name}

## 💪 Training Plan
{training_plan}

## 🥗 Meal Plan
{meal_plan}

---
*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"""
            
            return formatted_plan
            
        except Exception as e:
            logger.error(f"Error parsing fitness plan from string: {str(e)}")
            # Fallback to basic formatting
            return f"**Fitness Plan**\n\n{plan_str}"

    @staticmethod
    def parse_markdown_fitness_plan(plan_str: str) -> str:
        """
        Parse a markdown-formatted fitness plan (for Groq models)
        
        Args:
            plan_str: Markdown-formatted fitness plan string
            
        Returns:
            Formatted markdown string or None if parsing fails
        """
        try:
            # Remove <think> tags if present
            cleaned_str = re.sub(r'<think>.*?</think>', '', plan_str, flags=re.DOTALL)
            
            # Extract plan name
            name_match = re.search(r'\*\*Plan Name:\*\*\s*(.+?)(?:\n|$)', cleaned_str, re.IGNORECASE)
            if not name_match:
                # Try alternative formats
                name_match = re.search(r'##?\s*(.+?Plan.+?)(?:\n|$)', cleaned_str, re.IGNORECASE)
                if not name_match:
                    # Look for any header that might be the plan name
                    name_match = re.search(r'\*\*(.+?)\*\*', cleaned_str)
            
            name = name_match.group(1).strip() if name_match else "Custom Fitness Plan"
            
            # Extract training plan section
            training_match = re.search(r'\*\*Training Plan:?\*\*\s*(.*?)(?=\*\*Meal Plan|\*\*\s*Meal|$)', cleaned_str, re.DOTALL | re.IGNORECASE)
            if not training_match:
                # Try alternative headers
                training_match = re.search(r'##?\s*Training.*?\n(.*?)(?=##?\s*Meal|$)', cleaned_str, re.DOTALL | re.IGNORECASE)
            
            training_plan = training_match.group(1).strip() if training_match else ""
            
            # Extract meal plan section
            meal_match = re.search(r'\*\*Meal Plan:?\*\*\s*(.*?)(?=\*\*[^*]|\n\n\*\*|$)', cleaned_str, re.DOTALL | re.IGNORECASE)
            if not meal_match:
                # Try alternative headers
                meal_match = re.search(r'##?\s*Meal.*?\n(.*?)(?=##?|$)', cleaned_str, re.DOTALL | re.IGNORECASE)
            
            meal_plan = meal_match.group(1).strip() if meal_match else ""
            
            # Only return formatted plan if we found both training and meal sections
            if training_plan and meal_plan:
                return f"""# 🏋️ {name}

## 💪 Training Plan
{training_plan}

## 🥗 Meal Plan
{meal_plan}

---
*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"""
            
            # If we couldn't parse properly, return None to try other parsing methods
            return None
            
        except Exception as e:
            logger.error(f"Error parsing markdown fitness plan: {str(e)}")
            return None

    @staticmethod
    def format_raw_fitness_content(content: str) -> str:
        """
        CATCH-ALL: Format any fitness content nicely, even if it doesn't follow expected patterns
        
        Args:
            content: Raw content string that might contain fitness plan information
            
        Returns:
            Formatted markdown string with proper headers
        """
        try:
            # Clean up the content
            cleaned = content.strip()
            
            # Remove <think> tags completely
            cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL)
            cleaned = cleaned.strip()
            
            # If content is empty after cleaning, return a message
            if not cleaned:
                return "**Fitness Plan Generated**\n\nI've created a fitness plan for you, but there was an issue displaying it. Please try again or ask me to clarify any specific part of your plan."
            
            # If the content already looks formatted (has headers), just clean it up and display
            if any(marker in cleaned for marker in ['**Plan Name:', '**Training Plan:', '**Meal Plan:', '## ', '# ']):
                # Add emoji headers if missing
                if not cleaned.startswith('#'):
                    cleaned = f"# 🏋️ Your Fitness Plan\n\n{cleaned}"
                
                # Ensure proper markdown formatting
                cleaned = re.sub(r'\*\*Training Plan\*\*', '## 💪 Training Plan', cleaned)
                cleaned = re.sub(r'\*\*Meal Plan\*\*', '## 🥗 Meal Plan', cleaned)
                
                # Add footer
                if not cleaned.endswith('*'):
                    cleaned += "\n\n---\n*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"
                
                return cleaned
            
            # If no clear structure, add basic formatting
            return f"""# 🏋️ Your Fitness Plan

{cleaned}

---
*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"""
            
        except Exception as e:
            logger.error(f"Error formatting raw fitness content: {str(e)}")
            # Last resort - just return the content with minimal formatting
            return f"**Your Fitness Plan**\n\n{content}"

    @staticmethod
    def extract_response_content(result: Any) -> str:
        """
        Extract content from agent response with proper error handling
        
        Args:
            result: Agent response object
            
        Returns:
            Formatted response string
        """
        try:
            if hasattr(result, 'final_output'):
                content = result.final_output
                
                # Check if this looks like a fitness plan
                if hasattr(content, 'name') and hasattr(content, 'training_plan'):
                    return ResponseFormatter.format_fitness_plan(content)
                elif isinstance(content, str) and ('training_plan=' in content or 'meal_plan=' in content):
                    return ResponseFormatter.parse_fitness_plan_from_string(content)
                else:
                    return str(content)
            elif hasattr(result, 'content'):
                return str(result.content)
            elif isinstance(result, str):
                return result
            else:
                return str(result)
        except Exception as e:
            logger.error(f"Error extracting content from result: {str(e)}")
            return f"Sorry, I encountered an error while formatting the response: {str(e)}"

    @staticmethod
    def stream_response(
        response: str, 
        history: List[Dict], 
        chunk_size: int = 3
    ) -> Generator[List[Dict], None, None]:
        """
        Stream response text with configurable chunk size for better UX
        
        Args:
            response: Response text to stream
            history: Current chat history
            chunk_size: Number of characters per chunk
            
        Yields:
            Updated history with streaming response
        """
        try:
            # Add empty assistant message to history
            history = history + [{"role": "assistant", "content": ""}]
            
            # Stream the response character by character or in chunks
            for i in range(0, len(response), chunk_size):
                chunk = response[i:i + chunk_size]
                history[-1]["content"] += chunk
                yield history
                
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            # Fallback to complete response
            history = history + [{"role": "assistant", "content": response}]
            yield history
