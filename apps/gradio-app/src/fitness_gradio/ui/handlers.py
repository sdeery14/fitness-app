"""
Event handlers for the fitness app UI.
"""
import gradio as gr
import logging
from typing import List, Dict, Union, Generator, Any, Tuple

from fitness_core.agents import FitnessAgent
from fitness_core.services import ConversationManager, AgentRunner, ResponseFormatter
from fitness_core.utils import get_logger

logger = get_logger(__name__)

# Global state management
conversation_manager = ConversationManager()
current_agent = None
current_model = "gpt-4o-mini"


class UIHandlers:
    """Collection of event handlers for the UI."""
    
    @staticmethod
    def get_or_create_agent(model_name: str = None) -> FitnessAgent:
        """
        Get the current agent or create a new one with the specified model
        
        Args:
            model_name: Name of the AI model to use
            
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

    @staticmethod
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
            is_valid, validation_message = FitnessAgent.validate_model_name(new_model)
            
            if not is_valid:
                return f"""❌ **Invalid Model Selection**

{validation_message}

Please select a model from the supported list above."""
            
            # Test if we can create an agent with this model (basic validation)
            try:
                test_agent = FitnessAgent(new_model)
                logger.info(f"Successfully validated model: {new_model}")
            except Exception as model_error:
                logger.error(f"Failed to create agent with model {new_model}: {model_error}")
                return f"""❌ **Model Creation Failed**

Could not create agent with model `{new_model}`.

**Error:** {str(model_error)}

Please check your API keys and try a different model."""
            
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

    @staticmethod
    def filter_model_table(filter_choice: str) -> List[List[str]]:
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

    @staticmethod
    def select_model_from_table(table_data: Any, evt: gr.SelectData) -> Tuple[str, str]:
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
            change_result = UIHandlers.change_model(selected_model)
            
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

    @staticmethod
    def print_like_dislike(x: gr.LikeData) -> None:
        """Log user feedback on messages"""
        logger.info(f"User feedback - Index: {x.index}, Value: {x.value}, Liked: {x.liked}")

    @staticmethod
    def add_message(history: List[Dict], message: Dict) -> Tuple[List[Dict], gr.MultimodalTextbox]:
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

    @staticmethod
    def bot_with_real_streaming(
        history: List[Dict], 
        model_name: str = None
    ) -> Generator[List[Dict], None, None]:
        """
        Bot function with real-time streaming from the agent
        
        Args:
            history: Current Gradio chat history (for display only)
            model_name: Model to use for the agent
            
        Yields:
            Updated history with real-time streaming response
        """
        try:
            # Get agent instance with specified model
            agent = UIHandlers.get_or_create_agent(model_name)
            
            # Get input for agent from conversation manager
            agent_input = conversation_manager.get_input_for_agent()
            logger.info(f"Sending to agent ({current_model}): {type(agent_input)} - {conversation_manager.get_history_summary()}")
            
            # Add empty assistant message for streaming
            history.append({"role": "assistant", "content": ""})
            
            # Use the AgentRunner for streaming execution
            logger.info(f"Using real-time streaming mode")
            
            # Direct execution without ThreadPoolExecutor to avoid event loop issues
            try:
                content_chunks = []
                final_result = None
                
                for chunk in AgentRunner.run_agent_with_streaming_sync(agent, agent_input):
                    if chunk['type'] == 'final_result':
                        final_result = chunk['result']
                        if chunk['content']:
                            content_chunks.append(chunk['content'])
                    elif chunk['type'] == 'error':
                        final_result = chunk['result']
                        content_chunks.append(chunk['content'])
                
                # Update conversation manager
                if final_result:
                    conversation_manager.update_from_result(final_result)
                    logger.info(f"Updated conversation manager. {conversation_manager.get_history_summary()}")
                
                # Stream the content updates to the UI
                if content_chunks:
                    for content in content_chunks:
                        history[-1]["content"] = content
                        yield history
                else:
                    history[-1]["content"] = "I apologize, but I didn't receive a response. Please try again."
                    yield history
                    
            except Exception as e:
                logger.error(f"Error in streaming execution: {str(e)}")
                history[-1]["content"] = f"Sorry, I encountered an error while processing your request: {str(e)}"
                yield history
            
        except Exception as e:
            logger.error(f"Bot streaming function error: {str(e)}")
            if len(history) == 0 or history[-1].get("role") != "assistant":
                history.append({"role": "assistant", "content": ""})
            history[-1]["content"] = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
            yield history

    @staticmethod
    def bot(history: List[Dict], model_name: str = None) -> Generator[List[Dict], None, None]:
        """
        Main bot function with simulated streaming
        
        Args:
            history: Current Gradio chat history (for display only)
            model_name: Model to use for the agent
            
        Yields:
            Updated history with bot response
        """
        try:
            # Get agent instance with specified model
            agent = UIHandlers.get_or_create_agent(model_name)
            
            # Get input for agent from conversation manager
            agent_input = conversation_manager.get_input_for_agent()
            logger.info(f"Sending to agent ({current_model}): {type(agent_input)} - {conversation_manager.get_history_summary()}")
            
            # Run agent safely with sync wrapper
            result = AgentRunner.run_agent_safely_sync(agent, agent_input)
            
            # Update conversation manager with the result
            conversation_manager.update_from_result(result)
            logger.info(f"Updated conversation manager. {conversation_manager.get_history_summary()}")
            
            # Extract and format response for display
            response = ResponseFormatter.extract_response_content(result)
            
            # Stream the response with simulated typing
            yield from ResponseFormatter.stream_response(response, history)
            
        except Exception as e:
            logger.error(f"Bot function error: {str(e)}")
            error_response = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
            yield from ResponseFormatter.stream_response(error_response, history)

    @staticmethod
    def dynamic_bot(
        history: List[Dict], 
        use_real_streaming: bool = True, 
        model_name: str = None
    ) -> Generator[List[Dict], None, None]:
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
            yield from UIHandlers.bot_with_real_streaming(history, model_name)
        else:
            logger.info("Using simulated streaming mode")
            yield from UIHandlers.bot(history, model_name)

    @staticmethod
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
