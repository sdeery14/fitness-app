"""
Text-to-Speech utilities using Groq's TTS models.
"""
import os
import tempfile
import logging
import requests
from typing import Optional, Union
from pathlib import Path

from fitness_core.utils import get_logger

logger = get_logger(__name__)


class GroqTTS:
    """Groq Text-to-Speech service wrapper."""
    
    # Available English voices for playai-tts
    ENGLISH_VOICES = [
        "Arista-PlayAI", "Atlas-PlayAI", "Basil-PlayAI", "Briggs-PlayAI",
        "Calum-PlayAI", "Celeste-PlayAI", "Cheyenne-PlayAI", "Chip-PlayAI",
        "Cillian-PlayAI", "Deedee-PlayAI", "Fritz-PlayAI", "Gail-PlayAI",
        "Indigo-PlayAI", "Mamaw-PlayAI", "Mason-PlayAI", "Mikail-PlayAI",
        "Mitch-PlayAI", "Quinn-PlayAI", "Thunder-PlayAI"
    ]
    
    # Available Arabic voices for playai-tts-arabic
    ARABIC_VOICES = [
        "Ahmad-PlayAI", "Amira-PlayAI", "Khalid-PlayAI", "Nasser-PlayAI"
    ]
    
    # Default voice selections
    DEFAULT_ENGLISH_VOICE = "Celeste-PlayAI"  # Pleasant female voice
    DEFAULT_ARABIC_VOICE = "Amira-PlayAI"    # Pleasant female voice
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the GroqTTS client.
        
        Args:
            api_key: Groq API key. If None, will try to get from GROQ_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        self.temp_dir = Path(tempfile.gettempdir()) / "fitness_app_tts"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Create a session-specific directory for persistent audio files
        self.session_dir = self.temp_dir / "session_audio"
        self.session_dir.mkdir(exist_ok=True)
    
    def text_to_speech(
        self, 
        text: str, 
        voice: Optional[str] = None,
        model: str = "playai-tts",
        response_format: str = "wav",
        output_file: Optional[Union[str, Path]] = None
    ) -> Optional[str]:
        """
        Convert text to speech using Groq's TTS API.
        
        Args:
            text: Text to convert to speech (max 10K characters)
            voice: Voice to use. If None, uses default voice based on model
            model: TTS model to use ("playai-tts" or "playai-tts-arabic")
            response_format: Audio format ("wav")
            output_file: Path to save audio file. If None, creates temp file
            
        Returns:
            Path to the generated audio file, or None if error
        """
        try:
            # Validate text length
            if len(text) > 10000:
                logger.warning(f"Text too long ({len(text)} chars), truncating to 10K characters")
                text = text[:10000]
            
            # Set default voice based on model
            if voice is None:
                if model == "playai-tts-arabic":
                    voice = self.DEFAULT_ARABIC_VOICE
                else:
                    voice = self.DEFAULT_ENGLISH_VOICE
            
            # Validate voice for model
            if model == "playai-tts" and voice not in self.ENGLISH_VOICES:
                logger.warning(f"Voice {voice} not valid for English model, using default")
                voice = self.DEFAULT_ENGLISH_VOICE
            elif model == "playai-tts-arabic" and voice not in self.ARABIC_VOICES:
                logger.warning(f"Voice {voice} not valid for Arabic model, using default")
                voice = self.DEFAULT_ARABIC_VOICE
            
            # Create output file path - use session directory for persistence
            if output_file is None:
                # Create a unique filename using a hash of the text and timestamp
                import time
                timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
                text_hash = hash(text) % 100000
                output_file = self.session_dir / f"tts_output_{text_hash}_{timestamp}.wav"
            else:
                output_file = Path(output_file)
            
            logger.info(f"Generating TTS for {len(text)} chars using {model} with {voice}")
            
            # Generate speech using the correct API structure
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "input": text,
                "voice": voice,
                "response_format": response_format
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/audio/speech",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                # Write audio content to file
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"TTS audio saved to: {output_file}")
                return str(output_file)
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"Error generating TTS: {str(e)}")
            return None
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> None:
        """
        Clean up old temporary audio files.
        
        Args:
            max_age_hours: Delete files older than this many hours
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.temp_dir.glob("*.wav"):
                if current_time - file_path.stat().st_mtime > max_age_seconds:
                    file_path.unlink()
                    logger.debug(f"Deleted old TTS file: {file_path}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
    
    @classmethod
    def get_available_voices(cls, model: str = "playai-tts") -> list[str]:
        """
        Get list of available voices for a model.
        
        Args:
            model: Model name ("playai-tts" or "playai-tts-arabic")
            
        Returns:
            List of available voice names
        """
        if model == "playai-tts-arabic":
            return cls.ARABIC_VOICES.copy()
        else:
            return cls.ENGLISH_VOICES.copy()


# Global TTS instance (lazy initialized)
_tts_instance: Optional[GroqTTS] = None


def get_tts_instance() -> Optional[GroqTTS]:
    """
    Get or create a global TTS instance.
    
    Returns:
        GroqTTS instance or None if API key not available
    """
    global _tts_instance
    
    if _tts_instance is None:
        try:
            _tts_instance = GroqTTS()
        except ValueError as e:
            logger.warning(f"TTS not available: {str(e)}")
            return None
    
    return _tts_instance


def generate_speech_for_text(text: str, voice: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to generate speech for text.
    
    Args:
        text: Text to convert to speech
        voice: Voice to use (optional)
        
    Returns:
        Path to generated audio file or None if error
    """
    tts = get_tts_instance()
    if tts is None:
        return None
    
    return tts.text_to_speech(text, voice=voice)


def generate_speech_for_session(text: str, voice: Optional[str] = None) -> Optional[str]:
    """
    Generate speech for text with session persistence for chat interface.
    
    Args:
        text: Text to convert to speech
        voice: Voice to use (optional)
        
    Returns:
        Path to generated audio file that persists for the session, or None if error
    """
    tts = get_tts_instance()
    if tts is None:
        return None
    
    # Generate audio in session directory for persistence
    audio_file = tts.text_to_speech(text, voice=voice)
    if audio_file:
        # Ensure the file is in the session directory
        audio_path = Path(audio_file)
        if audio_path.exists():
            logger.info(f"Session TTS audio available at: {audio_file}")
            return str(audio_file)
    
    return None


def clean_tts_markup(text: str) -> str:
    """
    Clean text for TTS by removing markdown and other markup.
    
    Args:
        text: Text that may contain markdown
        
    Returns:
        Clean text suitable for TTS
    """
    import re
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italics
    text = re.sub(r'`(.*?)`', r'\1', text)        # Inline code
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # Code blocks
    text = re.sub(r'#{1,6}\s*(.*)', r'\1', text)  # Headers
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)    # Images
    text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)  # Lists
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)  # Numbered lists
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)      # Quotes
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)       # Multiple newlines
    text = re.sub(r'[ \t]+', ' ', text)           # Multiple spaces
    text = text.strip()
    
    return text
