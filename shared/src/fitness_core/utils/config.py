"""
Configuration management for the fitness app.
"""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration management."""
    
    # Server configuration
    SERVER_NAME: str = os.getenv("SERVER_NAME", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "7860"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # AI Model configuration
    DEFAULT_MODEL: str = os.getenv("AI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o"))
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # UI configuration
    MAX_CHAT_HISTORY: int = int(os.getenv("MAX_CHAT_HISTORY", "50"))
    STREAMING_CHUNK_SIZE: int = int(os.getenv("STREAMING_CHUNK_SIZE", "3"))
    
    @classmethod
    def get_gradio_config(cls) -> Dict[str, Any]:
        """Get configuration for Gradio app launch."""
        return {
            "server_name": cls.SERVER_NAME,
            "server_port": cls.SERVER_PORT,
            "show_error": True,
            "debug": cls.DEBUG
        }
    
    @classmethod
    def has_anthropic_key(cls) -> bool:
        """Check if Anthropic API key is configured."""
        return cls.ANTHROPIC_API_KEY is not None and len(cls.ANTHROPIC_API_KEY.strip()) > 0
    
    @classmethod
    def has_openai_key(cls) -> bool:
        """Check if OpenAI API key is configured."""
        return cls.OPENAI_API_KEY is not None and len(cls.OPENAI_API_KEY.strip()) > 0
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status."""
        status = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check API keys
        if not cls.has_anthropic_key() and not cls.has_openai_key():
            status["errors"].append(
                "No API keys configured. Please set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable."
            )
            status["valid"] = False
        
        if not cls.has_anthropic_key():
            status["warnings"].append("ANTHROPIC_API_KEY not set - Claude models will not work")
        
        if not cls.has_openai_key():
            status["warnings"].append("OPENAI_API_KEY not set - OpenAI models will not work")
        
        # Check port availability (basic check)
        if not (1024 <= cls.SERVER_PORT <= 65535):
            status["warnings"].append(f"Server port {cls.SERVER_PORT} may not be valid")
        
        return status
