"""
Event handlers for the fitness app UI.
"""
import gradio as gr
import logging
import os
from typing import List, Dict, Union, Generator, Any, Tuple, Optional

from fitness_core.agents import FitnessAgent
from fitness_core.services import ConversationManager, AgentRunner, ResponseFormatter
from fitness_core.utils import get_logger
from .audio_utils import AudioProcessor

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
    def select_model_from_dropdown(selected_model: str) -> str:
        """Handle model selection from dropdown"""
        try:
            # Ignore header selections (None values) and empty selections
            if not selected_model or selected_model is None:
                return ""
            
            # Return the selected model
            return selected_model
            
        except Exception as e:
            logger.error(f"Error selecting model from dropdown: {str(e)}")
            return selected_model or ""

    @staticmethod
    def print_like_dislike(x: gr.LikeData) -> None:
        """Log user feedback on messages"""
        logger.info(f"User feedback - Index: {x.index}, Value: {x.value}, Liked: {x.liked}")

    @staticmethod
    def add_voice_message(history: List[Dict], audio_data: Optional[Tuple]) -> Tuple[List[Dict], gr.Audio]:
        """
        Process voice input and add to chat history
        
        Args:
            history: Current Gradio chat history (for display)
            audio_data: Audio data from microphone (sample_rate, audio_array)
            
        Returns:
            Tuple of (updated_history, cleared_audio_input)
        """
        try:
            if audio_data is None:
                return history, gr.Audio(value=None)
            
            # Convert audio to text
            transcribed_text = AudioProcessor.convert_audio_to_text(audio_data)
            
            if transcribed_text and transcribed_text.strip():
                # Add voice message indicator to the text
                display_text = f"🎤 {transcribed_text}"
                
                # Add to Gradio history for display
                history.append({
                    "role": "user", 
                    "content": display_text
                })
                
                # Add to conversation manager (without the voice indicator)
                conversation_manager.add_user_message(transcribed_text)
                logger.info(f"Added voice message to conversation. {conversation_manager.get_history_summary()}")
            
            return history, gr.Audio(value=None)
            
        except Exception as e:
            logger.error(f"Error processing voice message: {str(e)}")
            # Add error message to history
            history.append({
                "role": "assistant", 
                "content": "Sorry, there was an error processing your voice message. Please try again."
            })
            return history, gr.Audio(value=None)

    @staticmethod
    def add_message_with_audio(history: List[Dict], message: Dict) -> Tuple[List[Dict], gr.MultimodalTextbox]:
        """
        Add user message to chat history with proper validation for text, files, and audio
        
        Args:
            history: Current Gradio chat history (for display)
            message: User message containing text, files, and/or audio
            
        Returns:
            Tuple of (updated_history, cleared_input)
        """
        try:
            # Debug: Log the message structure
            logger.info(f"Received message: {type(message)} - Keys: {list(message.keys()) if isinstance(message, dict) else 'Not a dict'}")
            if isinstance(message, dict):
                if message.get("files"):
                    logger.info(f"Files in message: {message['files']}")
                if message.get("text"):
                    logger.info(f"Text in message: {message['text']}")
            
            user_content_parts = []
            
            # Handle file uploads (including audio from microphone)
            if message.get("files"):
                for file_path in message["files"]:
                    if file_path:  # Validate file path exists
                        logger.info(f"Processing file: {file_path}")
                        
                        # Check if this is an audio file (from microphone recording)
                        if UIHandlers.is_audio_file(file_path):
                            logger.info(f"Detected audio file: {file_path}")
                            # Process audio file for transcription
                            transcribed_text = UIHandlers.process_audio_file(file_path)
                            
                            if transcribed_text and not transcribed_text.startswith("["):
                                # Add voice message indicator to the text
                                display_text = f"🎤 {transcribed_text}"
                                user_content_parts.append(transcribed_text)  # Add clean text to conversation
                                
                                # Add to Gradio history for display
                                history.append({
                                    "role": "user", 
                                    "content": display_text
                                })
                                logger.info(f"Successfully processed audio: {transcribed_text[:50]}...")
                            else:
                                # Show transcription error
                                history.append({
                                    "role": "user", 
                                    "content": f"🎤 {transcribed_text}"
                                })
                                logger.warning(f"Audio transcription failed: {transcribed_text}")
                        else:
                            # Handle non-audio file uploads
                            file_content = f"[File uploaded: {file_path}]"
                            user_content_parts.append(file_content)
                            # Add to Gradio history for display
                            history.append({
                                "role": "user", 
                                "content": {"path": file_path}
                            })
                            logger.info(f"Processed non-audio file: {file_path}")
            
            # Handle text input
            if message.get("text") and message["text"].strip():
                text_content = message["text"].strip()
                user_content_parts.append(text_content)
                # Add to Gradio history for display
                history.append({
                    "role": "user", 
                    "content": text_content
                })
                logger.info(f"Processed text input: {text_content[:50]}...")
            
            # Add to conversation manager (combine all content)
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
    def is_audio_file(file_path: str) -> bool:
        """
        Check if a file is an audio file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if it's an audio file, False otherwise
        """
        import os
        audio_extensions = {'.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm', '.mp4', '.mpeg', '.mpga'}
        file_ext = os.path.splitext(file_path.lower())[1]
        return file_ext in audio_extensions

    @staticmethod
    def process_audio_file(file_path: str) -> str:
        """
        Process an audio file for transcription.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            # Use Groq for transcription
            groq_api_key = os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                logger.warning("GROQ_API_KEY not found in environment variables")
                return "[Please set GROQ_API_KEY environment variable for voice transcription]"
            
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            
            with open(file_path, "rb") as audio_file:
                # Use whisper-large-v3-turbo for best price/performance ratio
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    language="en",  # You can make this configurable
                    temperature=0.0,
                    response_format="text"  # Simple text response for efficiency
                )
            
            # Groq returns the text directly when using "text" format
            result = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
            logger.info(f"Successfully transcribed audio file: {file_path} -> '{result[:50]}...'")
            return result
            
        except ImportError:
            logger.warning("Groq library not available")
            return "[Groq library not available for voice transcription]"
        except Exception as e:
            logger.error(f"Error processing audio file {file_path}: {str(e)}")
            return f"[Voice transcription error: {str(e)}]"

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
