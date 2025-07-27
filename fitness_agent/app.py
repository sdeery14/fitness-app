import gradio as gr
import time
import asyncio
import logging
import re
from typing import List, Dict, Any, Optional, Union, Generator
from concurrent.futures import ThreadPoolExecutor
from fitness_agent import FitnessAgent
from agents import Agent, ItemHelpers, Runner, function_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check what streaming methods are available
logger.info(f"Available Runner methods: {[method for method in dir(Runner) if not method.startswith('_')]}")


class FitnessUIError(Exception):
    """Custom exception for UI-related errors"""
    pass


class ConversationManager:
    """Manages conversation history and state for the fitness agent"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.thread_id = "fitness_thread_001"  # Could be made dynamic per session
        
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history"""
        self.conversation_history.append({"role": "user", "content": content})
        
    def get_input_for_agent(self) -> Union[str, List[Dict[str, str]]]:
        """Get the input format needed for the agent"""
        if not self.conversation_history:
            return "Hello"
        elif len(self.conversation_history) == 1:
            # First message - just send the content
            return self.conversation_history[0]["content"]
        else:
            # Multiple messages - send the full history
            return self.conversation_history
            
    def update_from_result(self, result) -> None:
        """Update conversation history from agent result"""
        if hasattr(result, 'to_input_list'):
            # Update our history with the complete conversation from the agent
            self.conversation_history = result.to_input_list()
        else:
            # Fallback: manually add the assistant response
            if hasattr(result, 'final_output'):
                response_content = result.final_output
            else:
                response_content = str(result)
            
            self.conversation_history.append({"role": "assistant", "content": str(response_content)})
    
    def clear_history(self) -> None:
        """Clear the conversation history"""
        self.conversation_history = []
        
    def get_history_summary(self) -> str:
        """Get a summary of the conversation for debugging"""
        return f"Conversation has {len(self.conversation_history)} messages"


def get_or_create_agent(model_name: str = None) -> FitnessAgent:
    """
    Get the current agent or create a new one with the specified model
    
    Args:
        model_name: Name of the Anthropic model to use
        
    Returns:
        FitnessAgent instance
    """
    global current_agent, current_model
    
    # Use default if no model specified
    if model_name is None:
        model_name = current_model
    
    # Create new agent if model changed or no agent exists
    if current_agent is None or current_model != model_name:
        logger.info(f"Creating new agent with model: {model_name}")
        current_agent = FitnessAgent(model_name)
        current_model = model_name
    
    return current_agent


def change_model(new_model: str) -> str:
    """
    Change the current model and reset the agent
    
    Args:
        new_model: New model to use
        
    Returns:
        Status message
    """
    global current_agent, current_model
    
    try:
        # Validate model exists in our supported list
        available_models = FitnessAgent.list_supported_models()
        is_valid, validation_message = FitnessAgent.validate_model_name(new_model)
        
        if not is_valid:
            return f"❌ **Model Validation Failed**\n\n{validation_message}"
        
        # Test if we can create an agent with this model (basic validation)
        try:
            logger.info(f"Attempting to create test agent with model: {new_model}")
            test_agent = FitnessAgent(new_model)
            logger.info(f"Successfully created test agent with model: {new_model}")
            # If we get here, the model is likely available
        except Exception as model_error:
            # Get the full error details for debugging
            error_str = str(model_error)
            error_repr = repr(model_error)
            error_type = type(model_error).__name__
            
            logger.error(f"Model initialization error for {new_model}:")
            logger.error(f"  Error type: {error_type}")
            logger.error(f"  Error string: {error_str}")
            logger.error(f"  Error repr: {error_repr}")
            
            # Clean up error message for display
            clean_error = error_str.replace('\n', ' ').replace('\r', ' ')
            clean_error = clean_error[:400] + "..." if len(clean_error) > 400 else clean_error
            
            # Check for specific error types
            if "not_found_error" in error_str.lower() or "notfounderror" in error_str.lower():
                recommended = ", ".join(FitnessAgent.get_recommended_models())
                return f"""❌ **Model Not Available**

🚫 **Error:** Model `{new_model}` is not currently available on your API account.

💡 **This could mean:**
- The model requires special access or higher tier subscription
- The model has been deprecated
- The model name is incorrect

🎯 **Try these recommended models instead:**
{recommended}

🔧 **Current Model:** `{current_model}` (unchanged)"""
            elif "api" in error_str.lower() and "key" in error_str.lower():
                return f"""❌ **API Configuration Error**

🚫 **Error:** There seems to be an issue with your Anthropic API configuration.

💡 **Please check:**
- Your ANTHROPIC_API_KEY environment variable is set
- Your API key is valid and has the necessary permissions
- Your account has access to the requested model

📝 **Error Details:** {clean_error}

🔧 **Current Model:** `{current_model}` (unchanged)

💡 **Tip:** Try using an OpenAI model if Anthropic models are not working."""
            else:
                return f"""❌ **Model Error**

🚫 **Error:** Failed to initialize model `{new_model}`

📝 **Error Type:** {error_type}
📝 **Details:** {clean_error}

🔧 **Current Model:** `{current_model}` (unchanged)

💡 **Debugging Info:**
- Provider: {"Anthropic" if "claude" in new_model else "OpenAI" if any(x in new_model for x in ["gpt", "o1", "o3"]) else "Unknown"}
- Try using a different model or check your API configuration"""
        
        # Reset agent to force recreation with new model
        current_agent = None
        current_model = new_model
        
        # Get model info for user feedback
        model_info = FitnessAgent.get_model_info(new_model)
        
        logger.info(f"Model changed to: {new_model}")
        return f"""✅ **Model Successfully Changed!**

🤖 **Current Model:** `{new_model}`

💡 **Description:** {model_info}

🔄 **Status:** Ready to chat with the new model. Your conversation history is preserved."""
        
    except Exception as e:
        logger.error(f"Error changing model: {str(e)}")
        return f"❌ **Unexpected Error:** {str(e)}"


def filter_model_table(filter_choice: str) -> list:
    """Filter the model table based on user selection."""
    all_data = FitnessAgent.get_models_table_data()
    
    if filter_choice == "🔵 Anthropic Only":
        return [row for row in all_data if "🔵 Anthropic" in row[1]]
    elif filter_choice == "🟢 OpenAI Only":
        return [row for row in all_data if "🟢 OpenAI" in row[1]]
    elif filter_choice == "⭐ Recommended Only":
        return [row for row in all_data if row[0] == "⭐"]
    else:  # All Models
        return all_data


def select_model_from_table(table_data, evt: gr.SelectData):
    """Select a model from the table"""
    try:
        if evt is None:
            return "", "Please select a model from the table"
        
        # Get the selected row index
        row_index = evt.index[0] if evt.index else 0
        
        # Handle both DataFrame and list formats
        try:
            # Try pandas DataFrame access first
            if hasattr(table_data, 'iloc') and row_index < len(table_data):
                row = table_data.iloc[row_index]
                if len(row) >= 7:
                    rating = row.iloc[0]  # Recommendation star
                    provider = row.iloc[1]  # Provider
                    selected_model = row.iloc[2]  # Model name
                    capability = row.iloc[3]  # Capability rating
                    speed = row.iloc[4]  # Speed rating
                    cost = row.iloc[5]  # Cost rating
                    description = row.iloc[6]  # Description
                else:
                    return "", "Invalid table row - insufficient columns"
            # Fall back to list access
            elif isinstance(table_data, list) and row_index < len(table_data) and len(table_data[row_index]) >= 7:
                rating = table_data[row_index][0]  # Recommendation star
                provider = table_data[row_index][1]  # Provider
                selected_model = table_data[row_index][2]  # Model name
                capability = table_data[row_index][3]  # Capability rating
                speed = table_data[row_index][4]  # Speed rating
                cost = table_data[row_index][5]  # Cost rating
                description = table_data[row_index][6]  # Description
            else:
                return "", "Invalid selection - please try clicking on a model row"
                
        except (IndexError, KeyError) as data_error:
            logger.error(f"Data access error: {str(data_error)} - Table type: {type(table_data)}, Row index: {row_index}")
            return "", "Error accessing table data - please try again"
        
        # Update the model and get the change result
        change_result = change_model(selected_model)
        
        if "✅" in change_result:
            model_info = f"""✅ **Model Successfully Selected!**

🤖 **Current Model:** `{selected_model}`
{provider}
**Capability:** {capability} | **Speed:** {speed} | **Cost:** {cost}

💡 **Description:** {description}

📊 **Status:** Ready to chat with the new model!"""
        else:
            model_info = change_result  # Show the error message
        
        return selected_model, model_info
        
    except Exception as e:
        logger.error(f"Error in select_model_from_table: {str(e)} - Table type: {type(table_data)}, Row index: {row_index if 'row_index' in locals() else 'unknown'}")
        return "", f"Error selecting model: {str(e)}"


def update_model_and_display(selected_model: str) -> str:
    """
    Update both the model and the display when dropdown selection changes
    
    Args:
        selected_model: Selected model from dropdown
        
    Returns:
        Formatted model information
    """
    # Ignore separator selections
    separators = [
        "--- Anthropic Models ---", 
        "--- OpenAI Models ---", 
        "--- Other Models ---",
        "--- Legacy/Experimental ---"
    ]
    if selected_model in separators:
        return f"""⚠️ **Please select a specific model**

The separator "{selected_model}" is not a valid model choice.

Please choose one of the actual model names from the dropdown."""
    
    # Update the actual model
    change_result = change_model(selected_model)
    
    # If the change was successful, return success message, otherwise return the error
    if "✅" in change_result:
        try:
            model_info = FitnessAgent.get_model_info(selected_model)
            
            # Determine provider emoji
            provider_emoji = "🔵" if "claude" in selected_model else "🟢" if any(x in selected_model for x in ["gpt", "o1", "o3"]) else "⚪"
            
            return f"""{provider_emoji} **Current Model:** `{selected_model}`

💡 **Description:** {model_info}

📊 **Status:** Model updated and ready to chat!"""
        except Exception as e:
            return f"""🤖 **Current Model:** `{selected_model}`

❌ *Model information not available*

📊 **Status:** Ready to chat!"""
    else:
        # Return the error message from change_model
        return change_result


def print_like_dislike(x: gr.LikeData) -> None:
    """Log user feedback on messages"""
    logger.info(f"User feedback - Index: {x.index}, Value: {x.value}, Liked: {x.liked}")


# Global conversation manager instance
conversation_manager = ConversationManager()

# Global agent instance that can be updated with model changes
current_agent = None
current_model = "claude-3.5-haiku"  # Updated default model


def add_message(history: List[Dict], message: Dict) -> tuple:
    """
    Add user message to chat history with proper validation
    
    Args:
        history: Current Gradio chat history (for display)
        message: User message containing text and/or files
        
    Returns:
        Tuple of (updated_history, cleared_input)
    """
    try:
        user_content_parts = []
        
        # Handle file uploads
        if message.get("files"):
            for file_path in message["files"]:
                if file_path:  # Validate file path exists
                    file_content = f"[File uploaded: {file_path}]"
                    user_content_parts.append(file_content)
                    # Add to Gradio history for display
                    history.append({
                        "role": "user", 
                        "content": {"path": file_path}
                    })
        
        # Handle text input
        if message.get("text") and message["text"].strip():
            text_content = message["text"].strip()
            user_content_parts.append(text_content)
            # Add to Gradio history for display
            history.append({
                "role": "user", 
                "content": text_content
            })
        
        # Add to conversation manager (combine file and text content)
        if user_content_parts:
            combined_content = "\n".join(user_content_parts)
            conversation_manager.add_user_message(combined_content)
            logger.info(f"Added user message to conversation. {conversation_manager.get_history_summary()}")
            
        return history, gr.MultimodalTextbox(value=None, interactive=False)
        
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}")
        # Add error message to history
        history.append({
            "role": "assistant", 
            "content": "Sorry, there was an error processing your message. Please try again."
        })
        return history, gr.MultimodalTextbox(value=None, interactive=False)


async def run_agent_with_streaming(agent: FitnessAgent, agent_input: Union[str, List[Dict[str, str]]]):
    """
    Run the agent with streaming support using the correct Runner.run_streamed API
    
    Args:
        agent: The fitness agent instance
        agent_input: Input for the agent (string for first message, list for conversation)
        
    Yields:
        Streaming response chunks from the agent with content and final result
    """
    try:
        logger.info(f"Running agent with streaming. Input type: {type(agent_input)}")
        
        # Use the correct streaming API
        result = Runner.run_streamed(agent, agent_input)
        
        accumulated_content = ""
        final_result = None
        has_content = False
        
        try:
            async for event in result.stream_events():
                # Skip raw response events as suggested in the example
                if event.type == "raw_response_event":
                    continue
                    
                # Handle different event types
                elif event.type == "agent_updated_stream_event":
                    logger.debug(f"Agent updated: {event.new_agent.name}")
                    continue
                    
                elif event.type == "run_item_stream_event":
                    if event.item.type == "tool_call_item":
                        logger.debug("Tool was called")
                        
                    elif event.item.type == "tool_call_output_item":
                        logger.debug(f"Tool output: {event.item.output}")
                        
                    elif event.item.type == "message_output_item":
                        # This is where the actual message content comes from
                        try:
                            message_content = ItemHelpers.text_message_output(event.item)
                            if message_content:
                                accumulated_content = message_content
                                has_content = True
                                # Yield a chunk-like object for streaming display
                                yield {
                                    'type': 'content_chunk',
                                    'content': message_content,
                                    'accumulated': accumulated_content
                                }
                        except Exception as item_error:
                            logger.warning(f"Error extracting message content: {item_error}")
                            # Continue processing other events
                            continue
        
        except Exception as streaming_error:
            # Check if this is the specific Pydantic validation error for Anthropic models
            error_str = str(streaming_error)
            if "validation error for ResponseTextDeltaEvent" in error_str and "logprobs" in error_str:
                logger.warning("Detected Anthropic model streaming validation error, falling back to non-streaming mode")
                
                # Fall back to non-streaming execution
                try:
                    fallback_result = await Runner.run(agent, agent_input)
                    final_result = fallback_result
                    
                    # Extract content from fallback result
                    if hasattr(fallback_result, 'final_output'):
                        accumulated_content = str(fallback_result.final_output)
                    else:
                        accumulated_content = str(fallback_result)
                    
                    has_content = True
                    
                    # Yield the content as if it was streamed
                    yield {
                        'type': 'content_chunk',
                        'content': accumulated_content,
                        'accumulated': accumulated_content
                    }
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback execution also failed: {fallback_error}")
                    raise streaming_error  # Re-raise original error
            else:
                # Re-raise if it's a different type of error
                raise streaming_error
        
        # Get the final result if we haven't already from fallback
        if final_result is None:
            try:
                final_result = await result.get_final_result()
            except Exception as final_error:
                logger.warning(f"Error getting final result: {final_error}")
                # Create a mock final result if we have content
                if has_content:
                    class MockResult:
                        def __init__(self, content):
                            self.final_output = content
                        def to_input_list(self):
                            return [{"role": "assistant", "content": self.final_output}]
                    
                    final_result = MockResult(accumulated_content)
        
        # Yield the final result for conversation management
        yield {
            'type': 'final_result',
            'result': final_result,
            'content': accumulated_content
        }
            
    except Exception as e:
        logger.error(f"Agent streaming error: {str(e)}")
        # Return error as a final result-like object
        class ErrorResult:
            def __init__(self, error_message):
                self.final_output = error_message
                
            def to_input_list(self):
                return []
                
        yield {
            'type': 'error',
            'result': ErrorResult(f"Sorry, I encountered an error while processing your request: {str(e)}"),
            'content': f"Sorry, I encountered an error while processing your request: {str(e)}"
        }


def run_agent_safely_sync(agent: FitnessAgent, agent_input: Union[str, List[Dict[str, str]]]) -> Any:
    """
    Synchronous wrapper for the agent execution - now using proper Runner.run method
    
    Args:
        agent: The fitness agent instance
        agent_input: Input for the agent (string for first message, list for conversation)
        
    Returns:
        Final agent result
    """
    def _run_agent():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                logger.info(f"Running agent sync with input type: {type(agent_input)}")
                
                # Use the correct async method
                async def run_async():
                    return await Runner.run(agent, agent_input)
                
                result = loop.run_until_complete(run_async())
                return result
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Agent execution error: {str(e)}")
            
            # Create a mock result object for error cases
            class ErrorResult:
                def __init__(self, error_message):
                    self.final_output = error_message
                    
                def to_input_list(self):
                    return []
            
            return ErrorResult(f"Sorry, I encountered an error while processing your request: {str(e)}")
    
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_run_agent)
            # Add timeout to prevent hanging
            return future.result(timeout=60)  # 60 second timeout
    except Exception as e:
        logger.error(f"Executor error: {str(e)}")
        
        # Create a mock result object for error cases
        class ErrorResult:
            def __init__(self, error_message):
                self.final_output = error_message
                
            def to_input_list(self):
                return []
        
        return ErrorResult("Sorry, I'm having trouble processing your request right now. Please try again.")


def parse_fitness_plan_from_string(plan_str: str) -> str:
    """
    Parse a fitness plan from its string representation
    
    Args:
        plan_str: String representation of a fitness plan object
        
    Returns:
        Formatted markdown string
    """
    try:
        import re
        
        # Extract name - handle both single and double quotes
        name_match = re.search(r"name=['\"]([^'\"]*)['\"]", plan_str)
        name = name_match.group(1) if name_match else "Fitness Plan"
        
        # Extract training plan - handle both list format and simple string format
        training_plan = ""
        
        # Try list format first (with brackets and quotes)
        training_match = re.search(r"training_plan=['\"](\[.*?\])['\"]", plan_str, re.DOTALL)
        if training_match:
            training_raw = training_match.group(1)
            # Clean up the training plan format
            training_items = re.findall(r'"([^"]*)"', training_raw)
            training_plan = "\n".join(f"• {item.strip()}" for item in training_items if item.strip())
        else:
            # Try simple string format
            training_match = re.search(r"training_plan=['\"]([^'\"]*)['\"]", plan_str)
            if training_match:
                training_raw = training_match.group(1)
                # Split by common delimiters and format as bullet points
                if ',' in training_raw:
                    training_items = [item.strip() for item in training_raw.split(',')]
                    training_plan = "\n".join(f"• {item}" for item in training_items if item)
                else:
                    training_plan = f"• {training_raw}"
        
        # Extract meal plan - handle both list format and simple string format
        meal_plan = ""
        
        # Try list format first (with brackets and quotes)
        meal_match = re.search(r"meal_plan=['\"](\[.*?\])['\"]", plan_str, re.DOTALL)
        if meal_match:
            meal_raw = meal_match.group(1)
            # Clean up the meal plan format
            meal_items = re.findall(r'"([^"]*)"', meal_raw)
            meal_plan = "\n".join(f"• {item.strip()}" for item in meal_items if item.strip())
        else:
            # Try simple string format
            meal_match = re.search(r"meal_plan=['\"]([^'\"]*)['\"]", plan_str)
            if meal_match:
                meal_raw = meal_match.group(1)
                # Handle multi-line format with dashes or bullet points
                if '\n-' in meal_raw or '\n•' in meal_raw:
                    # Already has bullet points, just clean up
                    meal_plan = meal_raw.strip()
                elif ',' in meal_raw:
                    # Split by commas and format as bullet points
                    meal_items = [item.strip() for item in meal_raw.split(',')]
                    meal_plan = "\n".join(f"• {item}" for item in meal_items if item)
                else:
                    meal_plan = f"• {meal_raw}"
        
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
            return str(plan_obj)
        
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

## 📝 Additional Notes
- Follow the plan consistently for best results
- Adjust portions based on your energy levels
- Stay hydrated throughout your workouts
- Rest days are important for recovery

---
*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"""
        
        else:  # default
            return f"""# 🏋️ {plan_obj.name}

## 💪 Training Plan
{plan_obj.training_plan}

## 🥗 Meal Plan
{plan_obj.meal_plan}

---
*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*"""
            
    except Exception as e:
        logger.error(f"Error formatting fitness plan: {str(e)}")
        return str(plan_obj)


def extract_response_content(result: Any) -> str:
    """
    Extract content from agent response with proper error handling
    
    Args:
        result: Agent response object
        
    Returns:
        Formatted response string
    """
    try:
        # Handle different response types
        if hasattr(result, 'final_output'):
            response_data = result.final_output
        else:
            response_data = result
        
        # Check if this is a structured FitnessPlan output
        if (hasattr(response_data, 'name') and 
            hasattr(response_data, 'training_plan') and 
            hasattr(response_data, 'meal_plan')):
            logger.info(f"Detected fitness plan object: {response_data.name}")
            return format_fitness_plan(response_data)
        
        # Check if the response_data is a string representation of a fitness plan
        response_str = str(response_data)
        if ("name=" in response_str and "training_plan=" in response_str and "meal_plan=" in response_str):
            logger.info("Detected fitness plan in string format, attempting to parse")
            return parse_fitness_plan_from_string(response_str)
        
        elif isinstance(response_data, str):
            return response_data
        else:
            return str(response_data)
            
    except Exception as e:
        logger.error(f"Error extracting response content: {str(e)}")
        return "Sorry, I had trouble formatting my response. Please try asking again."


def stream_response(response: str, history: List[Dict], chunk_size: int = 3) -> Generator[List[Dict], None, None]:
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
        history.append({"role": "assistant", "content": ""})
        
        # Stream in chunks rather than character by character for better performance
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i + chunk_size]
            history[-1]["content"] += chunk
            time.sleep(0.01)  # Faster streaming
            yield history
            
    except Exception as e:
        logger.error(f"Error streaming response: {str(e)}")
        # Fallback to showing full response
        history[-1]["content"] = response
        yield history


def bot_with_real_streaming(history: List[Dict], model_name: str = None) -> Generator[List[Dict], None, None]:
    """
    Bot function with real-time streaming from the agent using Runner.run_streamed
    
    Args:
        history: Current Gradio chat history (for display only)
        model_name: Model to use for the agent
        
    Yields:
        Updated history with real-time streaming response
    """
    try:
        # Get agent instance with specified model
        agent = get_or_create_agent(model_name)
        
        # Get input for agent from conversation manager
        agent_input = conversation_manager.get_input_for_agent()
        logger.info(f"Sending to agent ({current_model}): {type(agent_input)} - {conversation_manager.get_history_summary()}")
        
        # Add empty assistant message for streaming
        history.append({"role": "assistant", "content": ""})
        
        def _run_streaming():
            """Synchronous wrapper for streaming execution with Anthropic fallback"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    async def collect_streaming():
                        """Collect results from the streaming agent with fallback handling"""
                        content_chunks = []
                        final_result = None
                        streaming_worked = False
                        
                        try:
                            async for chunk in run_agent_with_streaming(agent, agent_input):
                                streaming_worked = True
                                if chunk['type'] == 'content_chunk':
                                    # Real-time content update
                                    content_chunks.append(chunk['accumulated'])
                                elif chunk['type'] == 'final_result':
                                    # Final result for conversation management
                                    final_result = chunk['result']
                                    # Ensure we have the final content
                                    if chunk['content'] and chunk['content'] not in content_chunks:
                                        content_chunks.append(chunk['content'])
                                elif chunk['type'] == 'error':
                                    # Error handling
                                    final_result = chunk['result']
                                    content_chunks.append(chunk['content'])
                                    
                        except Exception as stream_error:
                            logger.warning(f"Streaming failed completely: {stream_error}")
                            # Ultimate fallback - use the sync method
                            if not streaming_worked:
                                logger.info("Attempting sync fallback for Anthropic compatibility")
                                try:
                                    sync_result = await Runner.run(agent, agent_input)
                                    final_result = sync_result
                                    
                                    # Extract content
                                    if hasattr(sync_result, 'final_output'):
                                        content = str(sync_result.final_output)
                                    else:
                                        content = str(sync_result)
                                    
                                    content_chunks.append(content)
                                    
                                except Exception as sync_error:
                                    logger.error(f"Both streaming and sync execution failed: {sync_error}")
                                    content_chunks.append(f"Sorry, I encountered an error: {str(sync_error)}")
                        
                        # Update conversation manager with final result
                        if final_result:
                            conversation_manager.update_from_result(final_result)
                            logger.info(f"Updated conversation manager. {conversation_manager.get_history_summary()}")
                        
                        # Process content chunks through extract_response_content for proper formatting
                        processed_chunks = []
                        for content in content_chunks:
                            # Create a mock result object to use extract_response_content
                            class MockContentResult:
                                def __init__(self, content):
                                    self.final_output = content
                            
                            mock_result = MockContentResult(content)
                            formatted_content = extract_response_content(mock_result)
                            processed_chunks.append(formatted_content)
                        
                        return processed_chunks
                    
                    return loop.run_until_complete(collect_streaming())
                    
                finally:
                    loop.close()
            except Exception as e:
                logger.error(f"Streaming execution error: {str(e)}")
                return [f"Sorry, I encountered an error: {str(e)}"]
        
        # Execute streaming and yield updates
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_run_streaming)
                streaming_results = future.result(timeout=120)  # Increased timeout for fallback
                
                # Stream the content updates to the UI
                if streaming_results:
                    for i, content in enumerate(streaming_results):
                        history[-1]["content"] = content
                        yield history
                        # Add a small delay between updates for visual effect
                        if i < len(streaming_results) - 1:  # Don't delay on the last update
                            time.sleep(0.1)
                else:
                    # No content received
                    history[-1]["content"] = "I apologize, but I didn't receive a response. Please try again."
                    yield history
                    
        except Exception as e:
            logger.error(f"Error in streaming execution: {str(e)}")
            history[-1]["content"] = "Sorry, I had trouble processing your request."
            yield history
        
    except Exception as e:
        logger.error(f"Bot streaming function error: {str(e)}")
        if len(history) == 0 or history[-1].get("role") != "assistant":
            history.append({"role": "assistant", "content": ""})
        history[-1]["content"] = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
        yield history


def bot(history: List[Dict], model_name: str = None) -> Generator[List[Dict], None, None]:
    """
    Main bot function with comprehensive error handling and improved UX using manual conversation management
    
    Args:
        history: Current Gradio chat history (for display only)
        model_name: Model to use for the agent
        
    Yields:
        Updated history with bot response
    """
    try:
        # Get agent instance with specified model
        agent = get_or_create_agent(model_name)
        
        # Get input for agent from conversation manager
        agent_input = conversation_manager.get_input_for_agent()
        logger.info(f"Sending to agent ({current_model}): {type(agent_input)} - {conversation_manager.get_history_summary()}")
        
        # Run agent safely with sync wrapper
        result = run_agent_safely_sync(agent, agent_input)
        
        # Update conversation manager with the result
        conversation_manager.update_from_result(result)
        logger.info(f"Updated conversation manager. {conversation_manager.get_history_summary()}")
        
        # Extract and format response for display
        response = extract_response_content(result)
        
        # Stream the response
        yield from stream_response(response, history)
        
    except Exception as e:
        logger.error(f"Bot function error: {str(e)}")
        error_response = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
        yield from stream_response(error_response, history)


def dynamic_bot(history: List[Dict], use_real_streaming: bool = True, model_name: str = None) -> Generator[List[Dict], None, None]:
    """
    Dynamic bot function that can switch between streaming modes
    
    Args:
        history: Current Gradio chat history (for display only)
        use_real_streaming: Whether to use real-time streaming from agent
        model_name: Model to use for the agent
        
    Yields:
        Updated history with bot response
    """
    if use_real_streaming:
        logger.info("Using real-time streaming mode")
        yield from bot_with_real_streaming(history, model_name)
    else:
        logger.info("Using simulated streaming mode")
        yield from bot(history, model_name)


def clear_conversation() -> List[Dict]:
    """
    Clear the conversation history
    
    Returns:
        Empty chat history
    """
    global conversation_manager
    conversation_manager.clear_history()
    logger.info("Conversation history cleared")
    return []


# Gradio Interface
with gr.Blocks(
    theme=gr.themes.Soft(), 
    title="Fitness AI Assistant",
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    #chatbot {
        height: 600px;
    }
    .model-info {
        background: linear-gradient(135deg, rgba(55, 65, 81, 0.9), rgba(75, 85, 99, 0.7)) !important;
        color: #e5e7eb !important;
        padding: 16px !important;
        border-radius: 12px !important;
        border-left: 4px solid #10b981 !important;
        margin: 12px 0 !important;
        border: 1px solid rgba(75, 85, 99, 0.4) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(10px) !important;
    }
    .model-info p {
        color: #e5e7eb !important;
        margin: 8px 0 !important;
        line-height: 1.5 !important;
    }
    .model-info strong {
        color: #f9fafb !important;
        font-weight: 600 !important;
    }
    .model-info em {
        color: #d1d5db !important;
        font-style: italic;
    }
    .model-info code {
        background-color: rgba(31, 41, 55, 0.8) !important;
        color: #10b981 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
        font-size: 0.9em !important;
    }
    .model-dropdown {
        font-weight: bold;
    }
    /* Ensure all text in model-info respects dark theme */
    .model-info * {
        color: inherit !important;
    }
    /* Fix for any remaining white background issues */
    .model-info .prose {
        color: #e5e7eb !important;
    }
    """
) as demo:
    
    gr.Markdown("""
    # 🏋️‍♀️ Fitness AI Assistant
    Your personal fitness companion for workout plans, meal planning, and fitness guidance!
    
    💡 **Tips:**
    - Be specific about your fitness goals
    - Mention any physical limitations or preferences
    - Ask for modifications if needed
    - Choose your preferred AI model for different capabilities
    """)
    
    # Model selection section
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🤖 AI Model Selection")
            gr.Markdown("Browse and select your preferred AI model. Click on a row to select it.")
            
            # Create model table data
            table_data = FitnessAgent.get_models_table_data()
            
            model_table = gr.DataFrame(
                value=table_data,
                headers=["⭐", "Provider", "Model Name", "Capability", "Speed", "Cost", "Description"],
                datatype=["str", "str", "str", "str", "str", "str", "str"],
                interactive=False,
                wrap=True,
                elem_classes=["model-table"]
            )
            
            # Hidden components to manage selection
            selected_model = gr.Textbox(
                value="claude-3.5-haiku",
                visible=False,
                label="Selected Model"
            )
            
            # Model selection button
            with gr.Row():
                model_filter = gr.Dropdown(
                    choices=["All Models", "🔵 Anthropic Only", "🟢 OpenAI Only", "⭐ Recommended Only"],
                    value="All Models",
                    label="Filter Models",
                    scale=3
                )
    
    # Model information display
    model_info_display = gr.Markdown(
        value=f"""🔵 **Current Model:** `claude-3.5-haiku`

💡 **Description:** {FitnessAgent.get_model_info('claude-3.5-haiku')}

📊 **Status:** Ready to chat!""",
        visible=True,
        elem_classes=["model-info"]
    )
    
    chatbot = gr.Chatbot(
        elem_id="chatbot", 
        type="messages",
        show_copy_button=True,
        show_share_button=False,
        avatar_images=None,
        sanitize_html=True,
        render_markdown=True
    )

    chat_input = gr.MultimodalTextbox(
        interactive=True,
        file_count="multiple",
        placeholder="Ask me about fitness, request a workout plan, or get meal planning advice...",
        show_label=False,
        sources=["microphone", "upload"],
    )
    
    # Add clear conversation button and streaming toggle
    with gr.Row():
        clear_btn = gr.Button("🗑️ Clear Conversation", variant="secondary", size="sm")
        streaming_toggle = gr.Checkbox(
            label="🚀 Enable Real-time Streaming", 
            value=True, 
            info="Stream responses in real-time as the agent generates them"
        )
    
    # Add example buttons for common requests
    with gr.Row():
        gr.Examples(
            examples=[
                "Create a beginner workout plan for me",
                "I want to lose weight - help me with a fitness plan", 
                "Design a muscle building program for intermediate level",
                "I need a meal plan for gaining muscle mass",
                "What exercises should I do for better cardiovascular health?",
                "Help me with a home workout routine with no equipment"
            ],
            inputs=chat_input,
            label="💡 Try asking:"
        )
    
    # Add helpful information
    with gr.Accordion("ℹ️ How to use this assistant", open=False):
        gr.Markdown("""
        **What I can help you with:**
        - Create personalized workout plans
        - Design meal plans for your goals
        - Provide fitness guidance and tips
        - Suggest exercises for specific needs
        - Help modify existing plans
        
        **To get the best results:**
        - Tell me your fitness level (beginner, intermediate, advanced)
        - Mention your goals (weight loss, muscle gain, general fitness)
        - Include any equipment you have access to
        - Let me know about any injuries or limitations
        
        **AI Model Selection:**
        - **🔵 Anthropic Claude Models**: Excellent for detailed reasoning and analysis
          - Claude-4: Most capable (premium), Claude-3.7: Extended thinking
          - Claude-3.5: Balanced performance, Claude-3: Fast and cost-effective
        - **🟢 OpenAI GPT Models**: Great for general tasks and familiar interface
          - GPT-4o: Latest with vision, GPT-4 Turbo: Large context window
          - GPT-3.5: Fast and economical, o1/o3: Advanced reasoning
        - You can change models anytime - the conversation continues seamlessly
        - Mix and match providers based on your preferences
        
        **Conversation Management:**
        - The assistant remembers our entire conversation
        - You can refer back to previous plans or discussions
        - Use the "Clear Conversation" button to start fresh
        - Each conversation maintains context across multiple exchanges
        
        **Streaming Options:**
        - **Real-time Streaming**: Responses appear as the AI generates them using `Runner.run_streamed()` (most engaging)
        - **Simulated Streaming**: Responses are generated fully, then displayed with typing effect (more reliable)
        - Toggle the streaming mode using the checkbox above
        - Real-time streaming shows tool calls, outputs, and message generation in real-time
        - **Note**: Anthropic models automatically fall back to non-streaming if validation errors occur
        """)
    
    # Add model comparison section
    with gr.Accordion("🤖 Model Comparison Guide", open=False):
        gr.Markdown("""
        ## 🔵 Anthropic Claude Models
        
        | Model | Capability | Speed | Cost | Best For |
        |-------|------------|--------|------|----------|
        | claude-4-opus | ★★★★★ | ★★★☆☆ | ★★★★★ | Complex analysis, detailed plans |
        | claude-4-sonnet | ★★★★☆ | ★★★★☆ | ★★★★☆ | Balanced high performance |
        | claude-3.7-sonnet | ★★★★☆ | ★★★★☆ | ★★★☆☆ | Extended thinking, complex tasks |
        | claude-3.5-sonnet | ★★★★☆ | ★★★★☆ | ★★★☆☆ | General use, balanced |
        | claude-3.5-haiku | ★★★☆☆ | ★★★★★ | ★★☆☆☆ | **DEFAULT** - Fast responses |
        | claude-3-haiku | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | Most cost-effective |
        
        ## 🟢 OpenAI GPT Models
        
        | Model | Capability | Speed | Cost | Best For |
        |-------|------------|--------|------|----------|
        | gpt-4o | ★★★★★ | ★★★★☆ | ★★★★☆ | Latest features, vision support |
        | gpt-4o-mini | ★★★★☆ | ★★★★★ | ★★☆☆☆ | Balanced performance, affordable |
        | gpt-4-turbo | ★★★★☆ | ★★★★☆ | ★★★★☆ | Large context, reliable |
        | gpt-3.5-turbo | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | Fast and economical |
        | o1-preview | ★★★★★ | ★★☆☆☆ | ★★★★★ | Advanced reasoning |
        | o1-mini | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | Reasoning tasks |
        | o3-mini | ★★★★☆ | ★★★★☆ | ★★★☆☆ | Latest reasoning model |
        
        ### 💡 Provider Comparison
        - **🔵 Anthropic**: Excellent for detailed analysis, safety-focused, great for complex fitness planning
        - **🟢 OpenAI**: Familiar interface, good general performance, strong tool usage
        
        ### 🎯 Recommendations by Use Case
        - **Quick questions**: claude-3.5-haiku, gpt-4o-mini, gpt-3.5-turbo
        - **Comprehensive plans**: claude-3.5-sonnet, gpt-4o, claude-3.7-sonnet
        - **Complex analysis**: claude-4-opus, gpt-4o, o1-preview
        - **Budget-conscious**: claude-3-haiku, gpt-3.5-turbo, gpt-4o-mini
        """)

    # Event handlers
    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    bot_msg = chat_msg.then(
        dynamic_bot, 
        [chatbot, streaming_toggle, selected_model], 
        chatbot, 
        api_name="bot_response"
    )
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

    # Model table filtering
    model_filter.change(
        filter_model_table,
        inputs=[model_filter],
        outputs=[model_table]
    )
    
    # Model selection from table
    model_table.select(
        select_model_from_table,
        inputs=[model_table],
        outputs=[selected_model, model_info_display]
    )

    # Clear conversation handler
    clear_btn.click(clear_conversation, None, chatbot)

    chatbot.like(print_like_dislike, None, None, like_user_message=True)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        debug=False
    )
