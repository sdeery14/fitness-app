"""
Audio utilities for voice input processing.
"""
import os
import tempfile
import numpy as np
from typing import Optional, Tuple
import logging
import io

logger = logging.getLogger(__name__)

try:
    from scipy.io.wavfile import write
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available - audio processing will be limited")

class AudioProcessor:
    """Handles audio processing for voice input."""
    
    @staticmethod
    def convert_audio_to_text(audio_data: Optional[Tuple]) -> str:
        """
        Convert audio data to text using speech recognition.
        
        Args:
            audio_data: Tuple of (sample_rate, audio_array) or None
            
        Returns:
            Transcribed text or empty string if no audio
        """
        if not audio_data or audio_data is None:
            return ""
        
        try:
            sample_rate, audio_array = audio_data
            
            if audio_array is None or len(audio_array) == 0:
                return ""
            
            logger.info(f"Received audio: sample_rate={sample_rate}, length={len(audio_array)}")
            
            # Try to use Groq Whisper API first (faster and more cost-effective)
            transcribed_text = AudioProcessor.process_groq_whisper_api(audio_data)
            
            if transcribed_text and not transcribed_text.startswith("["):
                return transcribed_text
            
            # Fallback for demonstration
            return "Voice message received - please set up GROQ_API_KEY for transcription"
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return f"Error processing voice input: {str(e)}"
    
    @staticmethod
    def process_whisper_api(audio_data: Tuple) -> str:
        """
        Process audio using OpenAI Whisper API.
        
        Args:
            audio_data: Tuple of (sample_rate, audio_array)
            
        Returns:
            Transcribed text
        """
        try:
            import openai
            from fitness_core.utils import Config
            
            sample_rate, audio_array = audio_data
            
            # Get OpenAI API key from config
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                logger.warning("OPENAI_API_KEY not found in environment variables")
                return "[Please set OPENAI_API_KEY environment variable for voice transcription]"
            
            # Convert numpy array to WAV file
            temp_filename = AudioProcessor.save_audio_to_temp_file(audio_data)
            if not temp_filename:
                return "[Error: Could not save audio file for processing]"
            
            try:
                # Use OpenAI Whisper API
                client = openai.OpenAI(api_key=openai_api_key)
                
                with open(temp_filename, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="en"  # You can make this configurable
                    )
                
                # Clean up temporary file
                os.unlink(temp_filename)
                
                return transcript.text.strip()
                
            except Exception as api_error:
                # Clean up temporary file on error
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                raise api_error
            
        except ImportError:
            logger.warning("OpenAI library not available")
            return "[OpenAI library not available for voice transcription]"
        except Exception as e:
            logger.error(f"Error with Whisper API: {str(e)}")
            return f"[Voice transcription error: {str(e)}]"
    
    @staticmethod
    def process_groq_whisper_api(audio_data: Tuple) -> str:
        """
        Process audio using Groq Whisper API.
        
        Args:
            audio_data: Tuple of (sample_rate, audio_array)
            
        Returns:
            Transcribed text
        """
        try:
            from groq import Groq
            
            sample_rate, audio_array = audio_data
            
            # Get Groq API key from config
            groq_api_key = os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                logger.warning("GROQ_API_KEY not found in environment variables")
                return "[Please set GROQ_API_KEY environment variable for voice transcription]"
            
            # Convert numpy array to WAV file
            temp_filename = AudioProcessor.save_audio_to_temp_file(audio_data)
            if not temp_filename:
                return "[Error: Could not save audio file for processing]"
            
            try:
                # Use Groq Whisper API
                client = Groq(api_key=groq_api_key)
                
                with open(temp_filename, "rb") as audio_file:
                    # Use whisper-large-v3-turbo for best price/performance ratio
                    transcription = client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-large-v3-turbo",
                        language="en",  # You can make this configurable
                        temperature=0.0,
                        response_format="text"  # Simple text response for efficiency
                    )
                
                # Clean up temporary file
                os.unlink(temp_filename)
                
                # Groq returns the text directly when using "text" format
                return transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
                
            except Exception as api_error:
                # Clean up temporary file on error
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
                raise api_error
            
        except ImportError:
            logger.warning("Groq library not available")
            return "[Groq library not available for voice transcription]"
        except Exception as e:
            logger.error(f"Error with Groq Whisper API: {str(e)}")
            return f"[Voice transcription error: {str(e)}]"
    
    @staticmethod
    def save_audio_to_temp_file(audio_data: Tuple) -> Optional[str]:
        """
        Save audio data to a temporary WAV file.
        
        Args:
            audio_data: Tuple of (sample_rate, audio_array)
            
        Returns:
            Path to temporary file or None if error
        """
        if not SCIPY_AVAILABLE:
            logger.error("scipy not available for audio file processing")
            return None
            
        try:
            sample_rate, audio_array = audio_data
            
            # Ensure audio_array is in the right format
            if audio_array.dtype != np.int16:
                # Convert to int16 if needed
                if audio_array.dtype == np.float32 or audio_array.dtype == np.float64:
                    # Convert float to int16
                    audio_array = (audio_array * 32767).astype(np.int16)
                else:
                    audio_array = audio_array.astype(np.int16)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                write(temp_file.name, sample_rate, audio_array)
                return temp_file.name
                
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            return None
