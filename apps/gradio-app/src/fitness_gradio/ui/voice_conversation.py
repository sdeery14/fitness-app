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
from fitness_core.services import AgentRunner
from fitness_core.services.formatters import ResponseFormatter
from .tts_utils import generate_speech_for_session, clean_tts_markup

logger = get_logger(__name__)


@dataclass
class VoiceConversationState:
    """State management for voice conversation."""
    conversation: List[Dict] = field(default_factory=list)
    is_active: bool = False
    last_audio_response: Optional[str] = None


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
    
    def generate_chat_response(self, conversation_history: List[Dict], model_name: str = None) -> str:
        """
        Generate a chat response using the fitness agent.
        
        Args:
            conversation_history: List of conversation messages
            model_name: Model to use for response generation
            
        Returns:
            Assistant response text
        """
        try:
            # Create a fitness agent for this conversation
            agent = FitnessAgent(model_name or "gpt-4o-mini")
            
            # Convert conversation history to agent format and get last user message
            last_user_message = None
            for msg in reversed(conversation_history):
                if msg["role"] == "user":
                    # Remove the microphone emoji if present
                    content = msg["content"]
                    if content.startswith("🎤 "):
                        content = content[2:].strip()
                    last_user_message = content
                    break
            
            if last_user_message:
                # Generate response using the AgentRunner
                result = AgentRunner.run_agent_safely_sync(agent, last_user_message)
                
                # Use the same formatter as text messages
                return ResponseFormatter.extract_response_content(result)
            
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
            # Add user message to conversation
            state.conversation.append({"role": "user", "content": f"🎤 {transcription}"})
            
            # Update the conversation display
            yield state, state.conversation, None
            
            # Generate assistant response
            assistant_message = voice_manager.generate_chat_response(
                state.conversation, model_name
            )
            
            # Add assistant message to conversation
            state.conversation.append({"role": "assistant", "content": assistant_message})
            
            # Update conversation display
            yield state, state.conversation, None
            
            # Generate TTS for the response
            try:
                clean_text = clean_tts_markup(assistant_message)
                if len(clean_text) > 8000:
                    clean_text = clean_text[:8000] + "..."
                
                audio_file = generate_speech_for_session(clean_text)
                state.last_audio_response = audio_file
                
                # Final update with audio
                yield state, state.conversation, audio_file
                
            except Exception as tts_error:
                logger.error(f"TTS error: {tts_error}")
                yield state, state.conversation, None
        
        # Clean up temporary file
        try:
            os.remove(file_name)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error in voice response handling: {e}")
        state.conversation.append({
            "role": "assistant", 
            "content": "I'm sorry, I had trouble processing your voice input. Please try again."
        })
        yield state, state.conversation, None


def start_voice_conversation() -> Tuple[VoiceConversationState, bool, str]:
    """
    Start a new voice conversation.
    
    Returns:
        Tuple of (new_state, status_visible, status_text)
    """
    logger.info("=== STARTING VOICE CONVERSATION ===")
    state = VoiceConversationState(is_active=True)
    status_text = "🎙️ Voice conversation active - Just start talking!"
    logger.info(f"Voice conversation state created: active={state.is_active}")
    logger.info(f"Status text: {status_text}")
    return state, True, status_text


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
    
    # Reset state
    state.is_active = False
    state.conversation = []
    state.last_audio_response = None
    
    return state, False, "", conversation_history


def get_voice_conversation_js() -> str:
    """
    Get the JavaScript code for Voice Activity Detection (VAD).
    Based on the exact GitHub example: https://github.com/bklieger-groq/gradio-groq-basics/tree/main/calorie-tracker
    
    Returns:
        JavaScript code for VAD integration
    """
    return """
async function main(){
    const script1 = document.createElement("script");
    script1.src = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/ort.js";
    document.head.appendChild(script1)
    const script2 = document.createElement("script");
    script2.onload = async () =>  {
    console.log("vad loaded") ;
    var record = document.querySelector('.record-button');
    if (record) {
        record.textContent = "Just Start Talking!"
        record.style = "width: fit-content; padding-right: 0.5vw;"
    }
    const myvad = await vad.MicVAD.new({
        onSpeechStart: () => {
        var record = document.querySelector('.record-button');
        var player = document.querySelector('#streaming-out')
        if (record != null && (player == null || player.paused)) {
            console.log(record);
            record.click();
        }
        },
        onSpeechEnd: (audio) => {
        var stop = document.querySelector('.stop-button');
        if (stop != null) {
            console.log(stop);
            stop.click();
        }
        }
    })
    myvad.start()
    }
    script2.src = "https://cdn.jsdelivr.net/npm/@ricky0123/vad-web@0.0.7/dist/bundle.min.js";
    script1.onload = () =>  {
    console.log("onnx loaded") 
    document.head.appendChild(script2)
    };
}
"""


def reset_voice_conversation_js() -> str:
    """
    Get JavaScript to reset voice conversation button state.
    
    Returns:
        JavaScript code to reset button
    """
    return """
() => {
  var record = document.querySelector('.record-button');
  record.textContent = "Just Start Talking!"
  record.style = "width: fit-content; padding-right: 0.5vw;"
}
"""
