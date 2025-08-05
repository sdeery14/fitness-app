"""
Voice conversation utilities for two-way voice chat with the fitness agent.
"""
import os
import tempfile
import logging
import soundfile as sf
import xxhash
import gradio as gr
from typing import Optional, Tuple, List, Dict, Generator, Any
from dataclasses import dataclass, field

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    Groq = None

from fitness_core.utils import get_logger
from fitness_core.agents import FitnessAgent
from fitness_core.agents.providers import ModelProvider
from fitness_core.services import FitnessAgentRunner, ConversationManager
from fitness_core.services.formatters import ResponseFormatter
from .tts_utils import generate_speech_for_session, clean_tts_markup

logger = get_logger(__name__)


@dataclass
class VoiceConversationState:
    """State management for voice conversation."""
    conversation_manager: ConversationManager = field(default_factory=ConversationManager)
    is_active: bool = False
    last_audio_response: Optional[str] = None
    
    @property
    def conversation(self) -> List[Dict]:
        """Get conversation history as list of dicts for compatibility."""
        # Ensure all content is strings, not complex objects
        cleaned_history = []
        for msg in self.conversation_manager.conversation_history:
            content = msg.get("content", "")
            
            # Extract text from complex objects including RunResult format
            if isinstance(content, list):
                # Handle list format like [{'annotations': [], 'text': '...', 'type': 'output_text'}]
                if content and isinstance(content[0], dict) and 'text' in content[0]:
                    content = content[0]['text']
                else:
                    # Fallback: join list items
                    content = " ".join(str(item) for item in content)
            elif isinstance(content, dict):
                # Handle dict format like {'annotations': [], 'text': '...', 'type': 'output_text'}
                if 'text' in content:
                    content = content['text']
                elif 'content' in content:
                    content = content['content']
                else:
                    content = str(content)
            elif not isinstance(content, str):
                content = str(content)
            
            cleaned_history.append({
                "role": msg.get("role", "assistant"),
                "content": content
            })
        
        return cleaned_history


class VoiceConversationManager:
    """Manages two-way voice conversations with the fitness agent."""
    
    def __init__(self):
        """Initialize the voice conversation manager."""
        if not HAS_GROQ:
            raise ValueError("Groq library is not available. Please install groq package.")
            
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.groq_client = Groq(api_key=self.groq_api_key)
    
    def _extract_text_from_response(self, response: Any) -> str:
        """
        Extract text content from various response formats including RunResult.
        
        Args:
            response: Response object (could be string, dict, list, or other)
            
        Returns:
            Clean text string
        """
        if isinstance(response, str):
            return response
        elif isinstance(response, list):
            # Handle list format like [{'annotations': [], 'text': '...', 'type': 'output_text'}]
            if response and isinstance(response[0], dict) and 'text' in response[0]:
                return response[0]['text']
            else:
                # Fallback: join list items
                return " ".join(str(item) for item in response)
        elif isinstance(response, dict):
            # Handle various dict formats including RunResult format
            if 'text' in response:
                return response['text']
            elif 'content' in response:
                return response['content']
            elif 'message' in response:
                return response['message']
            else:
                # Fallback to string representation
                return str(response)
        elif hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
    
    def transcribe_audio_with_vad(self, file_name: str) -> Optional[str]:
        """
        Transcribe audio file using Whisper with voice activity detection.
        
        Args:
            file_name: Path to the audio file
            
        Returns:
            Transcribed text if speech detected, None if no speech
        """
        if file_name is None:
            return None

        try:
            with open(file_name, "rb") as audio_file:
                response = self.groq_client.audio.transcriptions.with_raw_response.create(
                    model="whisper-large-v3-turbo",
                    file=("audio.wav", audio_file),
                    response_format="verbose_json",
                )
                completion = self._process_whisper_response(response.parse())
                logger.info(f"Audio transcription result: {completion}")
                return completion
                
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            return f"Error in transcription: {str(e)}"
    
    def _process_whisper_response(self, completion) -> Optional[str]:
        """
        Process Whisper transcription response and return text based on no_speech_prob.
        
        Args:
            completion: Whisper transcription response object
            
        Returns:
            Transcribed text if no_speech_prob <= 0.7, otherwise None
        """
        if completion.segments and len(completion.segments) > 0:
            no_speech_prob = completion.segments[0].get('no_speech_prob', 0)
            logger.info(f"No speech probability: {no_speech_prob}")

            if no_speech_prob > 0.7:
                return None
                
            return completion.text.strip()
        
        return None
    
    def generate_chat_response(self, conversation_manager: ConversationManager, model_name: str = None) -> str:
        """
        Generate a chat response using the fitness agent and conversation manager.
        
        Args:
            conversation_manager: Shared conversation manager instance
            model_name: Model to use for response generation
            
        Returns:
            Assistant response text
        """
        try:
            # Create a fitness agent for this conversation
            agent = FitnessAgent(model_name or ModelProvider.resolve_model_name())
            
            # Get input for agent from conversation manager (same as text chat)
            agent_input = conversation_manager.get_input_for_agent()
            
            if agent_input:
                # Generate response using the FitnessAgentRunner (same as text chat)
                result = FitnessAgentRunner.run_agent_safely_sync(agent, agent_input)
                logger.info(f"Agent result type: {type(result)}")
                logger.info(f"Agent result: {result}")
                
                # Update conversation manager with result (same as text chat)
                conversation_manager.update_from_result(result)
                logger.info(f"Conversation history after update: {conversation_manager.conversation_history}")
                
                # Check what's in the last assistant message
                if conversation_manager.conversation_history:
                    last_msg = conversation_manager.conversation_history[-1]
                    logger.info(f"Last message in conversation: {last_msg}")
                    logger.info(f"Last message content type: {type(last_msg.get('content', 'N/A'))}")
                
                # Use the same formatter as text messages
                formatted_response = ResponseFormatter.extract_response_content(result)
                logger.info(f"Formatted response type: {type(formatted_response)}")
                logger.info(f"Formatted response content: {formatted_response}")
                
                # Ensure we return a string - handle various response formats
                final_response = self._extract_text_from_response(formatted_response)
                logger.info(f"Final response type: {type(final_response)}")
                logger.info(f"Final response content: {final_response}")
                
                return final_response
            
            return "I'm here to help with your fitness goals. What would you like to know?"
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"I'm sorry, I encountered an error. Please try again."


# Global voice conversation manager
_voice_manager: Optional[VoiceConversationManager] = None


def get_voice_manager() -> Optional[VoiceConversationManager]:
    """Get or create voice conversation manager."""
    global _voice_manager
    
    if _voice_manager is None:
        try:
            _voice_manager = VoiceConversationManager()
        except ValueError as e:
            logger.warning(f"Voice conversation not available: {e}")
            return None
    
    return _voice_manager


def reset_voice_audio_input() -> None:
    """
    Reset the voice audio input to prepare for next conversation turn.
    
    Returns:
        None (clears the audio input)
    """
    logger.debug("Resetting voice audio input for next turn")
    return None


def process_voice_audio(audio: Tuple, state: VoiceConversationState) -> Tuple:
    """
    Process incoming voice audio during conversation.
    
    Args:
        audio: Audio data tuple (sample_rate, audio_data)
        state: Current voice conversation state
        
    Returns:
        Updated audio and state
    """
    return audio, state


def handle_voice_response(
    state: VoiceConversationState, 
    audio: Tuple,
    model_name: str = None
) -> Generator[Tuple[VoiceConversationState, List[Dict], Optional[str]], None, None]:
    """
    Handle voice input and generate response with TTS.
    
    Args:
        state: Current voice conversation state
        audio: Audio data from microphone
        model_name: Model to use for response generation
        
    Yields:
        Tuple of (updated_state, conversation_history, audio_file)
    """
    voice_manager = get_voice_manager()
    if not voice_manager:
        yield state, state.conversation, None
        return
    
    if not audio:
        yield state, state.conversation, None
        return

    try:
        # Save audio to temporary file
        temp_dir = tempfile.gettempdir()
        file_name = os.path.join(temp_dir, f"{xxhash.xxh32(bytes(audio[1])).hexdigest()}.wav")
        sf.write(file_name, audio[1], audio[0], format="wav")

        # Transcribe the audio
        transcription = voice_manager.transcribe_audio_with_vad(file_name)
        
        if transcription and not transcription.startswith("Error"):
            # Add user message to conversation manager (same as text chat)
            # Remove the microphone emoji if present
            clean_transcription = transcription
            if transcription.startswith("🎤 "):
                clean_transcription = transcription[2:].strip()
            
            state.conversation_manager.add_user_message(clean_transcription)
            
            # Update the conversation display
            yield state, state.conversation, None
            
            # Generate assistant response using conversation manager
            assistant_message = voice_manager.generate_chat_response(
                state.conversation_manager, model_name
            )
            
            logger.info(f"Assistant message returned from generate_chat_response: type={type(assistant_message)}, content={assistant_message}")
            
            # The response is already added to conversation_manager by generate_chat_response
            # Update conversation display
            logger.info(f"About to yield conversation: {state.conversation}")
            for i, msg in enumerate(state.conversation):
                logger.info(f"Message {i}: role={msg.get('role')}, content_type={type(msg.get('content'))}, content={str(msg.get('content'))[:100]}...")
            yield state, state.conversation, None
            
            # Generate TTS for the response
            try:
                logger.info(f"Preparing TTS for assistant_message type: {type(assistant_message)}")
                logger.info(f"Assistant message content: {assistant_message}")
                
                # Extract text using the same method as in VoiceConversationManager
                voice_manager = get_voice_manager()
                if voice_manager:
                    tts_text = voice_manager._extract_text_from_response(assistant_message)
                else:
                    # Fallback if voice manager is not available
                    tts_text = str(assistant_message)
                
                logger.info(f"Extracted TTS text type: {type(tts_text)}")
                logger.info(f"Extracted TTS text content: {tts_text[:200]}...")
                
                clean_text = clean_tts_markup(tts_text)
                if len(clean_text) > 8000:
                    clean_text = clean_text[:8000] + "..."
                
                logger.info(f"Generating TTS for: {clean_text[:100]}...")
                audio_file = generate_speech_for_session(clean_text)
                state.last_audio_response = audio_file
                
                # Final update with audio
                yield state, state.conversation, audio_file
                
            except Exception as tts_error:
                logger.error(f"TTS error: {tts_error}")
                logger.error(f"Assistant message type: {type(assistant_message)}")
                logger.error(f"Assistant message content: {assistant_message}")
                yield state, state.conversation, None
        
        # Clean up temporary file
        try:
            os.remove(file_name)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error in voice response handling: {e}")
        # Add error message to conversation manager
        state.conversation_manager.add_assistant_message(
            "I'm sorry, I had trouble processing your voice input. Please try again."
        )
        yield state, state.conversation, None


def start_voice_conversation(existing_conversation_manager: ConversationManager = None) -> Tuple[VoiceConversationState, bool, str]:
    """
    Start a new voice conversation, optionally with an existing conversation manager.
    
    Args:
        existing_conversation_manager: Optional existing conversation manager to continue from
    
    Returns:
        Tuple of (new_state, status_visible, status_text)
    """
    logger.info("=== STARTING VOICE CONVERSATION ===")
    
    # Create state with existing conversation manager or new one
    if existing_conversation_manager:
        state = VoiceConversationState(
            conversation_manager=existing_conversation_manager,
            is_active=True
        )
        logger.info(f"Starting voice conversation with existing history ({len(existing_conversation_manager.conversation_history)} messages)")
    else:
        state = VoiceConversationState(is_active=True)
        logger.info("Starting fresh voice conversation")
    
    status_text = "🎙️ Voice conversation active - Just start talking!"
    logger.info(f"Voice conversation state created: active={state.is_active}")
    logger.info(f"Status text: {status_text}")
    return state, True, status_text


def merge_voice_with_main_conversation(
    voice_state: VoiceConversationState, 
    main_conversation_manager: ConversationManager
) -> None:
    """
    Merge voice conversation history with the main conversation manager.
    
    Args:
        voice_state: Voice conversation state containing the conversation
        main_conversation_manager: Main conversation manager to merge into
    """
    logger.info("Merging voice conversation with main chat")
    
    # Add all voice conversation messages to main conversation
    for message in voice_state.conversation:
        content = message["content"]
        
        # Handle different content types
        if isinstance(content, list):
            # If content is a list, join it or take the first item
            content = " ".join(str(item) for item in content) if content else ""
        elif not isinstance(content, str):
            # Convert to string if it's not already
            content = str(content)
        
        # Remove microphone emoji if present
        if content.startswith("🎤 "):
            content = content[2:].strip()
        
        if message["role"] == "user":
            main_conversation_manager.add_user_message(content)
        else:  # assistant
            main_conversation_manager.add_assistant_message(content)
    
    logger.info(f"Merged {len(voice_state.conversation)} voice messages to main conversation")


def end_voice_conversation(state: VoiceConversationState) -> Tuple[VoiceConversationState, bool, str, List[Dict]]:
    """
    End the voice conversation and return the conversation history.
    
    Args:
        state: Current voice conversation state
        
    Returns:
        Tuple of (updated_state, status_visible, status_text, conversation_history)
    """
    logger.info("Ending voice conversation")
    
    # Copy conversation to return
    conversation_history = state.conversation.copy()
    
    # Reset state (but keep the same conversation manager instance)
    state.is_active = False
    state.conversation_manager.clear_history()
    state.last_audio_response = None
    
    return state, False, "", conversation_history


def get_voice_conversation_js() -> str:
    """
    Get the JavaScript code for Voice Activity Detection (VAD).
    This will be loaded on-demand when voice conversation starts.
    
    Returns:
        JavaScript code for VAD integration
    """
    return """
() => {
    // Check if VAD is already initialized to avoid duplicate initialization
    if (window.vadInitialized) {
        console.log("VAD already initialized");
        return;
    }

    console.log("Initializing VAD...");

    // Request microphone permission explicitly
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            console.log("Microphone permission granted");
            // Stop the test stream
            stream.getTracks().forEach(track => track.stop());
            
            // Now initialize VAD
            initializeVAD();
        })
        .catch(error => {
            console.error("Microphone permission denied:", error);
            alert("Microphone access is required for voice conversation. Please allow microphone access and try again.");
        });

    function initializeVAD() {
        const script1 = document.createElement("script");
        script1.src = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/ort.js";
        document.head.appendChild(script1);

        const script2 = document.createElement("script");
        script2.onload = async () => {
            console.log("vad loaded");
            var record = document.querySelector('.record-button');
            if (record) {
                record.textContent = "Just Start Talking!";
                record.style = "width: fit-content; padding-right: 0.5vw;";
            }
            
            try {
                const myvad = await vad.MicVAD.new({
                    onSpeechStart: () => {
                        console.log("Speech detected - starting recording");
                        var record = document.querySelector('.record-button');
                        var player = document.querySelector('#voice-output audio');
                        
                        // Only start recording if not already recording and no audio is playing
                        if (record != null && (player == null || player.paused)) {
                            console.log("Clicking record button");
                            record.click();
                        }
                    },
                    onSpeechEnd: (audio) => {
                        console.log("Speech ended - stopping recording");
                        var stop = document.querySelector('.stop-button');
                        if (stop != null) {
                            console.log("Clicking stop button");
                            stop.click();
                        }
                    }
                });
                
                // Store VAD instance globally for cleanup
                window.currentVAD = myvad;
                
                // Start VAD
                myvad.start();
                console.log("VAD started successfully");
                window.vadInitialized = true;
                
                // Set up audio playback handlers
                function setupAudioPlaybackHandlers() {
                    const voiceOutput = document.querySelector('#voice-output audio');
                    if (voiceOutput) {
                        voiceOutput.addEventListener('ended', function() {
                            console.log("Audio playback ended - ready for next input");
                            // Reset record button text
                            var record = document.querySelector('.record-button');
                            if (record) {
                                record.textContent = "Just Start Talking!";
                                record.style = "width: fit-content; padding-right: 0.5vw;";
                            }
                        });
                        
                        voiceOutput.addEventListener('pause', function() {
                            console.log("Audio playback paused - ready for next input");
                        });
                    }
                }
                
                // Set up audio playback handlers after DOM is ready
                setTimeout(setupAudioPlaybackHandlers, 1000);
                
            } catch (error) {
                console.error("Error initializing VAD:", error);
                alert("Error initializing voice detection. Please check your microphone and try again.");
            }
        };

        script2.src = "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.7/dist/bundle.min.js";
        script1.onload = () => {
            console.log("onnx loaded");
            document.head.appendChild(script2);
        };
    }
}
"""


def get_vad_cleanup_js() -> str:
    """
    Get JavaScript code to clean up VAD when voice conversation ends.
    
    Returns:
        JavaScript code to stop and cleanup VAD
    """
    return """
() => {
    console.log("Cleaning up VAD...");

    // Stop and cleanup VAD if it exists
    if (window.currentVAD) {
        try {
            window.currentVAD.pause();
            console.log("VAD stopped");
        } catch (error) {
            console.log("Error stopping VAD:", error);
        }
        window.currentVAD = null;
    }

    // Reset initialization flag
    window.vadInitialized = false;

    // Reset button state
    var record = document.querySelector('.record-button');
    if (record) {
        record.textContent = "Record";
        record.style = "";
    }

    console.log("VAD cleanup completed");
}
"""


def reset_voice_conversation_js() -> str:
    """
    Get JavaScript to reset voice conversation button state and prepare for next input.
    
    Returns:
        JavaScript code to reset button and prepare for continuous conversation
    """
    return """
() => {
    console.log("Resetting voice conversation state");

    // Reset record button text and style
    var record = document.querySelector('.record-button');
    if (record) {
        record.textContent = "Just Start Talking!";
        record.style = "width: fit-content; padding-right: 0.5vw;";
    }

    // Ensure VAD is ready for next input
    setTimeout(() => {
        console.log("Voice conversation ready for next input");
    }, 500);
}
"""
