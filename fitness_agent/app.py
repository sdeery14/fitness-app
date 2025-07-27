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


def print_like_dislike(x: gr.LikeData) -> None:
    """Log user feedback on messages"""
    logger.info(f"User feedback - Index: {x.index}, Value: {x.value}, Liked: {x.liked}")


# Global conversation manager instance
conversation_manager = ConversationManager()


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


def bot_with_real_streaming(history: List[Dict]) -> Generator[List[Dict], None, None]:
    """
    Bot function with real-time streaming from the agent using Runner.run_streamed
    
    Args:
        history: Current Gradio chat history (for display only)
        
    Yields:
        Updated history with real-time streaming response
    """
    try:
        # Create agent instance
        agent = FitnessAgent()
        
        # Get input for agent from conversation manager
        agent_input = conversation_manager.get_input_for_agent()
        logger.info(f"Sending to agent: {type(agent_input)} - {conversation_manager.get_history_summary()}")
        
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


def bot(history: List[Dict]) -> Generator[List[Dict], None, None]:
    """
    Main bot function with comprehensive error handling and improved UX using manual conversation management
    
    Args:
        history: Current Gradio chat history (for display only)
        
    Yields:
        Updated history with bot response
    """
    try:
        # Create agent instance
        agent = FitnessAgent()
        
        # Get input for agent from conversation manager
        agent_input = conversation_manager.get_input_for_agent()
        logger.info(f"Sending to agent: {type(agent_input)} - {conversation_manager.get_history_summary()}")
        
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


def dynamic_bot(history: List[Dict], use_real_streaming: bool = True) -> Generator[List[Dict], None, None]:
    """
    Dynamic bot function that can switch between streaming modes
    
    Args:
        history: Current Gradio chat history (for display only)
        use_real_streaming: Whether to use real-time streaming from agent
        
    Yields:
        Updated history with bot response
    """
    if use_real_streaming:
        logger.info("Using real-time streaming mode")
        yield from bot_with_real_streaming(history)
    else:
        logger.info("Using simulated streaming mode")
        yield from bot(history)


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
    """
) as demo:
    
    gr.Markdown("""
    # 🏋️‍♀️ Fitness AI Assistant
    Your personal fitness companion for workout plans, meal planning, and fitness guidance!
    
    💡 **Tips:**
    - Be specific about your fitness goals
    - Mention any physical limitations or preferences
    - Ask for modifications if needed
    """)
    
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

    # Event handlers
    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    bot_msg = chat_msg.then(dynamic_bot, [chatbot, streaming_toggle], chatbot, api_name="bot_response")
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

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
