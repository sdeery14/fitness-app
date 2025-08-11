"""
Event handlers for the fitness app UI.
"""
import gradio as gr
import logging
import os
from typing import List, Dict, Union, Generator, Any, Tuple, Optional

from fitness_core.agents import FitnessAgent
from fitness_core.agents.providers import ModelProvider
from fitness_core.agents.user_session import SessionManager
from fitness_core.services import ConversationManager, FitnessAgentRunner, ResponseFormatter
from fitness_core.utils import get_logger
from .tts_utils import generate_speech_for_text, generate_speech_for_session, clean_tts_markup
from .voice_conversation import (
    VoiceConversationState, 
    start_voice_conversation, 
    end_voice_conversation,
    process_voice_audio,
    handle_voice_response,
    merge_voice_with_main_conversation
)

logger = get_logger(__name__)

# Global state management
conversation_manager = ConversationManager()
current_agent = None
current_model = ModelProvider.resolve_model_name()  # Use configured default model


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
    def refresh_agent_profile() -> None:
        """
        Refresh the current agent's user profile context.
        Call this when user profile is updated to ensure agent has latest context.
        """
        global current_agent
        if current_agent and hasattr(current_agent, 'refresh_user_profile'):
            current_agent.refresh_user_profile()
            logger.info("Refreshed agent's user profile context")

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
            logger.info(f"Processing message: {message}")
            user_content_parts = []
            has_audio_content = False
            audio_transcription = None
            
            # Handle file uploads (including audio from microphone)
            if message.get("files"):
                logger.info(f"Found {len(message['files'])} files in message")
                for file_path in message["files"]:
                    if file_path:  # Validate file path exists
                        logger.info(f"Processing file: {file_path}")
                        # Check if this is an audio file (from microphone recording)
                        if UIHandlers.is_audio_file(file_path):
                            logger.info(f"Detected audio file: {file_path}")
                            # Process audio file for transcription
                            transcribed_text = UIHandlers.process_audio_file(file_path)
                            
                            if transcribed_text and not transcribed_text.startswith("["):
                                audio_transcription = transcribed_text
                                user_content_parts.append(transcribed_text)  # Add clean text to conversation
                                has_audio_content = True
                                logger.info(f"Successfully transcribed audio: '{transcribed_text[:50]}...'")
                            else:
                                # Handle transcription error
                                audio_transcription = transcribed_text
                                has_audio_content = True  # Still mark as audio content even if failed
                                logger.warning(f"Audio transcription failed: {transcribed_text}")
                        else:
                            # Handle non-audio file uploads
                            file_content = f"[File uploaded: {file_path}]"
                            user_content_parts.append(file_content)
                            logger.info(f"Added file upload to content: {file_path}")
            else:
                logger.info("No files found in message")
            
            # Handle text input
            text_content = None
            if message.get("text") and message["text"].strip():
                text_content = message["text"].strip()
                user_content_parts.append(text_content)
                logger.info(f"Found text content: '{text_content[:50]}...'")
            else:
                logger.info("No text content found in message")
            
            # Add appropriate message to chat history
            if has_audio_content and audio_transcription:
                if audio_transcription.startswith("["):
                    # Transcription error - show error message
                    display_text = f"🎤 {audio_transcription}"
                else:
                    # Successful transcription - show with microphone icon
                    display_text = f"🎤 {audio_transcription}"
                
                history.append({
                    "role": "user",
                    "content": display_text
                })
                logger.info(f"Added audio message to chat history: '{display_text}'")
                
                # If there's also text content, add it separately
                if text_content:
                    history.append({
                        "role": "user",
                        "content": text_content
                    })
                    logger.info(f"Added additional text content to history: '{text_content[:50]}...'")
                    
            elif text_content:
                # Only text content, no audio
                history.append({
                    "role": "user",
                    "content": text_content
                })
                logger.info(f"Added text-only message to chat history: '{text_content[:50]}...'")
                
            elif message.get("files") and not has_audio_content:
                # File uploads that aren't audio
                for file_path in message["files"]:
                    if file_path and not UIHandlers.is_audio_file(file_path):
                        history.append({
                            "role": "user",
                            "content": {"path": file_path}
                        })
                        logger.info(f"Added file upload to history: {file_path}")
            
            # Add to conversation manager (combine all content)
            if user_content_parts:
                combined_content = "\n".join(user_content_parts)
                conversation_manager.add_user_message(combined_content)
                logger.info(f"Added user message to conversation manager. Content parts: {len(user_content_parts)}, Combined: '{combined_content[:100]}...', {conversation_manager.get_history_summary()}")
            else:
                logger.warning("No user content parts found in message - this may indicate an issue")
                
            logger.info(f"Final history length: {len(history)}")
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
    def bot_with_real_streaming(
        history: List[Dict], 
        model_name: str = None,
        use_tts: bool = False
    ) -> Generator[Tuple[List[Dict], Optional[str]], None, None]:
        """
        Bot function with real-time streaming from the agent
        
        Args:
            history: Current Gradio chat history (for display only)
            model_name: Model to use for the agent
            use_tts: Whether to generate text-to-speech for the response
            
        Yields:
            Tuple of (Updated history, audio_file_path or None)
        """
        try:
            # Get agent instance with specified model
            agent = UIHandlers.get_or_create_agent(model_name)
            
            # Get input for agent from conversation manager
            agent_input = conversation_manager.get_input_for_agent()
            logger.info(f"Sending to agent ({current_model}): {type(agent_input)} - {conversation_manager.get_history_summary()}")
            
            # Add empty assistant message for streaming
            history.append({"role": "assistant", "content": ""})
            
            # Use the FitnessAgentRunner for streaming execution
            logger.info(f"Using real-time streaming mode")
            
            # Direct execution without ThreadPoolExecutor to avoid event loop issues
            try:
                content_chunks = []
                final_result = None
                final_content = ""
                
                for chunk in FitnessAgentRunner.run_agent_with_streaming_sync(agent, agent_input):
                    if chunk['type'] == 'final_result':
                        final_result = chunk['result']
                        if chunk['content']:
                            content_chunks.append(chunk['content'])
                            final_content = chunk['content']
                    elif chunk['type'] == 'error':
                        final_result = chunk['result']
                        content_chunks.append(chunk['content'])
                        final_content = chunk['content']
                
                # Update conversation manager
                if final_result:
                    conversation_manager.update_from_result(final_result)
                    logger.info(f"Updated conversation manager. {conversation_manager.get_history_summary()}")
                    
                    # Check if the result contains a FitnessPlan and save it
                    UIHandlers._check_and_save_fitness_plan(final_result)
                
                # Stream the content updates to the UI
                if content_chunks:
                    for content in content_chunks:
                        history[-1]["content"] = content
                        yield history, None  # No audio during streaming
                        final_content = content
                    
                    # Generate TTS for the final response if enabled
                    if use_tts and final_content:
                        audio_file = UIHandlers._generate_tts_for_response_sync(final_content)
                        if audio_file:
                            # Return the final history with the audio file
                            yield history, audio_file
                        else:
                            yield history, None
                    else:
                        yield history, None
                        
                else:
                    error_msg = "I apologize, but I didn't receive a response. Please try again."
                    history[-1]["content"] = error_msg
                    yield history, None
                    
            except Exception as e:
                logger.error(f"Error in streaming execution: {str(e)}")
                error_msg = f"Sorry, I encountered an error while processing your request: {str(e)}"
                history[-1]["content"] = error_msg
                yield history, None
            
        except Exception as e:
            logger.error(f"Bot streaming function error: {str(e)}")
            if len(history) == 0 or history[-1].get("role") != "assistant":
                history.append({"role": "assistant", "content": ""})
            history[-1]["content"] = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
            yield history, None

    @staticmethod
    def bot(history: List[Dict], model_name: str = None, use_tts: bool = False) -> Generator[Tuple[List[Dict], Optional[str]], None, None]:
        """
        Main bot function with simulated streaming
        
        Args:
            history: Current Gradio chat history (for display only)
            model_name: Model to use for the agent
            use_tts: Whether to generate text-to-speech for the response
            
        Yields:
            Tuple of (Updated history, audio_file_path or None)
        """
        try:
            # Get agent instance with specified model
            agent = UIHandlers.get_or_create_agent(model_name)
            
            # Get input for agent from conversation manager
            agent_input = conversation_manager.get_input_for_agent()
            logger.info(f"Sending to agent ({current_model}): {type(agent_input)} - {conversation_manager.get_history_summary()}")
            
            # Run agent safely with sync wrapper
            result = FitnessAgentRunner.run_agent_safely_sync(agent, agent_input)
            
            # Update conversation manager with the result
            conversation_manager.update_from_result(result)
            logger.info(f"Updated conversation manager. {conversation_manager.get_history_summary()}")
            
            # Check if the result contains a FitnessPlan and save it
            UIHandlers._check_and_save_fitness_plan(result)
            
            # Extract and format response for display
            response = ResponseFormatter.extract_response_content(result)
            
            # Stream the response with simulated typing
            for updated_history in ResponseFormatter.stream_response(response, history):
                yield updated_history, None  # No audio during streaming
            
            # Generate TTS for the final response if enabled
            if use_tts and response:
                audio_file = UIHandlers._generate_tts_for_response_sync(response)
                if audio_file:
                    yield history, audio_file
                else:
                    yield history, None
            else:
                yield history, None
            
        except Exception as e:
            logger.error(f"Bot function error: {str(e)}")
            error_response = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
            for updated_history in ResponseFormatter.stream_response(error_response, history):
                yield updated_history, None

    @staticmethod
    def dynamic_bot(
        history: List[Dict], 
        use_real_streaming: bool = True,
        use_tts: bool = False,
        model_name: str = None
    ) -> Generator[Tuple[List[Dict], Optional[str]], None, None]:
        """
        Dynamic bot function that can switch between streaming modes and TTS
        
        Args:
            history: Current Gradio chat history (for display only)
            use_real_streaming: Whether to use real-time streaming from agent
            use_tts: Whether to generate text-to-speech for the response
            model_name: Model to use for the agent
            
        Yields:
            Tuple of (Updated history, audio_file_path or None)
        """
        if use_real_streaming:
            logger.info("Using real-time streaming mode")
            yield from UIHandlers.bot_with_real_streaming(history, model_name, use_tts)
        else:
            logger.info("Using simulated streaming mode")
            yield from UIHandlers.bot(history, model_name, use_tts)

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

    @staticmethod
    def get_latest_fitness_plan() -> str:
        """
        Get the latest fitness plan generated by the agent.
        
        Returns:
            Formatted fitness plan or message if no plan exists
        """
        try:
            session = SessionManager.get_current_session()
            
            if not session:
                return "**No Fitness Plan Available**\n\nNo fitness plan has been generated yet. Ask me to create a personalized fitness plan for you!"
            
            latest_plan = session.get_fitness_plan()
            
            if latest_plan is None:
                return "**No Fitness Plan Available**\n\nNo fitness plan has been generated yet. Ask me to create a personalized fitness plan for you!"
            
            # Format the plan using the ResponseFormatter
            from fitness_core.services import ResponseFormatter
            formatted_plan = ResponseFormatter.format_fitness_plan(latest_plan, style="detailed")
            
            return formatted_plan
            
        except Exception as e:
            logger.error(f"Error retrieving latest fitness plan: {str(e)}")
            return f"**Error Retrieving Plan**\n\nSorry, there was an error retrieving your fitness plan: {str(e)}"

    @staticmethod
    def has_fitness_plan() -> bool:
        """
        Check if a fitness plan is available.
        
        Returns:
            True if a fitness plan exists, False otherwise
        """
        session = SessionManager.get_current_session()
        return session and session.has_fitness_plan()

    @staticmethod 
    def clear_fitness_plan() -> str:
        """
        Clear the stored fitness plan.
        
        Returns:
            Confirmation message
        """
        try:
            session = SessionManager.get_current_session()
            if session:
                session.clear_fitness_plan()
            logger.info("Fitness plan cleared")
            return "**Fitness Plan Cleared**\n\nYour stored fitness plan has been cleared. Ask me to create a new one when you're ready!"
        except Exception as e:
            logger.error(f"Error clearing fitness plan: {str(e)}")
            return f"**Error Clearing Plan**\n\nThere was an error clearing your fitness plan: {str(e)}"

    @staticmethod
    def refresh_plan_display() -> str:
        """
        Refresh the fitness plan display. This is called after bot responses to update the UI.
        
        Returns:
            Current fitness plan content for display
        """
        return UIHandlers.get_latest_fitness_plan()

    @staticmethod
    def _check_and_save_fitness_plan(result: Any) -> None:
        """
        Check if the agent result contains a FitnessPlan and save it if found.
        
        Args:
            result: The agent execution result to check
        """
        try:
            # Check if the result has tool calls that might contain fitness plans
            if hasattr(result, 'messages') and result.messages:
                for message in result.messages:
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        for tool_call in message.tool_calls:
                            # Check if this is a create_fitness_plan tool call
                            if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'name'):
                                if tool_call.function.name == 'create_fitness_plan':
                                    logger.info("Found create_fitness_plan tool call")
                                    # Look for the tool result in the subsequent messages
                                    UIHandlers._extract_fitness_plan_from_tool_result(result)
                                    return
            
            # Also check the final_output directly for FitnessPlan objects
            if hasattr(result, 'final_output'):
                output = result.final_output
                if hasattr(output, 'name') and hasattr(output, 'training_plan') and hasattr(output, 'meal_plan'):
                    logger.info("Found FitnessPlan in final_output")
                    session = SessionManager.get_or_create_session()
                    session.set_fitness_plan(output)
                    
        except Exception as e:
            logger.error(f"Error checking for fitness plan in result: {str(e)}")

    @staticmethod
    def _extract_fitness_plan_from_tool_result(result: Any) -> None:
        """
        Extract FitnessPlan from tool execution results.
        
        Args:
            result: The agent execution result containing tool calls
        """
        try:
            # Look through messages for tool results
            if hasattr(result, 'messages') and result.messages:
                for message in result.messages:
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        for tool_call in message.tool_calls:
                            if (hasattr(tool_call, 'function') and 
                                hasattr(tool_call.function, 'name') and 
                                tool_call.function.name == 'create_fitness_plan'):
                                
                                # The tool should have returned a structured FitnessPlan
                                # We need to find the corresponding tool result
                                tool_call_id = getattr(tool_call, 'id', None)
                                if tool_call_id:
                                    # Look for the tool result message
                                    for msg in result.messages:
                                        if (hasattr(msg, 'role') and msg.role == 'tool' and
                                            hasattr(msg, 'tool_call_id') and msg.tool_call_id == tool_call_id):
                                            
                                            # Try to extract FitnessPlan from the tool result
                                            tool_content = getattr(msg, 'content', '')
                                            UIHandlers._parse_and_save_fitness_plan_from_content(tool_content)
                                            return
                                            
        except Exception as e:
            logger.error(f"Error extracting fitness plan from tool result: {str(e)}")

    @staticmethod
    def _parse_and_save_fitness_plan_from_content(content: str) -> None:
        """
        Parse fitness plan content and save it if it's a valid plan.
        
        Args:
            content: Content that might contain fitness plan data
        """
        try:
            # This is a simplified parser - we might need to enhance this based on actual tool output format
            # For now, we'll check if the content looks like a fitness plan and create a simple FitnessPlan object
            
            if "training_plan" in content.lower() and "meal_plan" in content.lower():
                # Import here to avoid circular imports
                from fitness_core.agents.agent_models import FitnessPlan
                
                # Simple parsing - this can be enhanced based on actual output format
                lines = content.split('\n')
                name = "Generated Fitness Plan"
                training_plan = "Training plan details from tool"
                meal_plan = "Meal plan details from tool"
                
                # Try to extract actual content if possible
                for line in lines:
                    if line.startswith("**") and "Plan" in line:
                        name = line.strip("*").strip()
                        break
                
                # Create and save the fitness plan
                fitness_plan = FitnessPlan(
                    name=name,
                    training_plan=training_plan,
                    meal_plan=meal_plan
                )
                
                session = SessionManager.get_or_create_session()
                session.set_fitness_plan(fitness_plan)
                logger.info(f"Successfully parsed and saved fitness plan: {name}")
                
        except Exception as e:
            logger.error(f"Error parsing fitness plan from content: {str(e)}")

    @staticmethod
    def toggle_audio_visibility(tts_enabled: bool) -> gr.Audio:
        """
        Toggle the visibility of the audio component based on TTS setting.
        
        Args:
            tts_enabled: Whether TTS is enabled
            
        Returns:
            Updated audio component with appropriate visibility
        """
        return gr.Audio(visible=tts_enabled)

    @staticmethod
    def _generate_tts_for_response_sync(text: str) -> Optional[str]:
        """
        Generate TTS audio for a response text synchronously.
        
        Args:
            text: The text to convert to speech
            
        Returns:
            Path to generated audio file or None if error
        """
        try:
            if not text or not text.strip():
                return None
            
            # Clean the text for TTS
            clean_text = clean_tts_markup(text)
            
            # Limit text length for TTS (Groq has 10K char limit)
            if len(clean_text) > 8000:  # Leave some buffer
                clean_text = clean_text[:8000] + "..."
                logger.info(f"Truncated TTS text to 8000 characters")
            
            logger.info(f"Generating TTS for response ({len(clean_text)} chars)")
            
            # Generate TTS using session persistence
            audio_file = generate_speech_for_session(clean_text)
            if audio_file:
                logger.info(f"TTS audio generated: {audio_file}")
                return audio_file
            else:
                logger.warning("Failed to generate TTS audio")
                return None
                
        except Exception as e:
            logger.error(f"TTS generation error: {str(e)}")
            return None

    @staticmethod
    def start_voice_conversation() -> tuple:
        """
        Start a voice conversation with shared conversation manager.
        
        Returns:
            Tuple of components to update
        """
        print("=== START VOICE CONVERSATION HANDLER CALLED ===")
        logger.info("=== START VOICE CONVERSATION HANDLER CALLED ===")
        
        try:
            logger.info("=== START VOICE CONVERSATION BUTTON CLICKED ===")
            global conversation_manager
            
            # Start voice conversation with the main conversation manager for context continuity
            state, status_visible, status_text = start_voice_conversation(conversation_manager)
            logger.info(f"Voice conversation started with shared context - Status: {status_text}")
            logger.info(f"Main conversation has {len(conversation_manager.conversation_history)} messages")
            
            return (
                state,                    # voice_state
                status_text              # voice_status markdown
            )
        except Exception as e:
            logger.error(f"Error starting voice conversation: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return (
                VoiceConversationState(),
                "❌ Error starting voice conversation"
            )

    @staticmethod
    def end_voice_conversation(voice_state: VoiceConversationState) -> tuple:
        """
        End voice conversation - simplified since using shared chatbot.
        
        Args:
            voice_state: Current voice conversation state
            
        Returns:
            Tuple of (voice_state, voice_status)
        """
        try:
            logger.info("Ending voice conversation")
            
            # Reset voice state 
            updated_state, status_visible, status_text, voice_history = end_voice_conversation(voice_state)
            
            return (
                updated_state,           # voice_state
                status_text             # voice_status markdown
            )
            
        except Exception as e:
            logger.error(f"Error ending voice conversation: {e}")
            return voice_state, "❌ Error ending voice conversation"

    @staticmethod
    def handle_voice_input(
        voice_state: VoiceConversationState, 
        audio: tuple, 
        model_name: str = None,
        main_chatbot: List[Dict] = None
    ) -> Generator[tuple, None, None]:
        """
        Handle voice input during conversation using shared chatbot.
        
        Args:
            voice_state: Current voice conversation state
            audio: Audio data from microphone
            model_name: Model to use for response  
            main_chatbot: Main chatbot history to update directly
            
        Yields:
            Tuple of (voice_state, main_chatbot, voice_output)
        """
        try:
            for updated_state, conversation, audio_file in handle_voice_response(
                voice_state, audio, model_name
            ):
                # Convert conversation to Gradio-compatible format
                gradio_conversation = []
                for msg in conversation:
                    if isinstance(msg, dict) and msg.get('role') and msg.get('content'):
                        # Extract content if it's a complex structure
                        content = msg['content']
                        if isinstance(content, list) and content:
                            # Extract text from complex content structure
                            text_content = ""
                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'output_text':
                                    text_content += item.get('text', '')
                            content = text_content if text_content else str(content)
                        elif not isinstance(content, str):
                            content = str(content)
                            
                        gradio_conversation.append({
                            'role': msg['role'],
                            'content': content
                        })
                
                yield updated_state, gradio_conversation, audio_file
                
        except Exception as e:
            logger.error(f"Error handling voice input: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            yield voice_state, main_chatbot or [], None
