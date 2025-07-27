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
            if not (hasattr(plan_obj, 'name') and 
                    hasattr(plan_obj, 'training_plan') and 
                    hasattr(plan_obj, 'meal_plan')):
                # Try to parse as string if it's not a proper object
                if isinstance(plan_obj, str):
                    return ResponseFormatter.parse_fitness_plan_from_string(plan_obj)
                else:
                    return f"**Fitness Plan**\n\n{str(plan_obj)}"
            
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
