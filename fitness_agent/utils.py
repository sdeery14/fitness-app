"""
Utilities and configuration for the fitness agent.
"""
import os
import logging
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
    DEFAULT_MODEL: str = os.getenv("AI_MODEL", os.getenv("OPENAI_MODEL", "llama-3.3-70b-versatile"))
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
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
    def has_groq_key(cls) -> bool:
        """Check if Groq API key is configured."""
        return cls.GROQ_API_KEY is not None and len(cls.GROQ_API_KEY.strip()) > 0


def setup_logging():
    """Set up logging configuration."""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=Config.LOG_FILE if Config.LOG_FILE else None
    )
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def format_fitness_plan_for_display(fitness_plan) -> str:
    """Format a fitness plan for user-friendly display."""
    if not fitness_plan:
        return "No fitness plan available."
    
    try:
        output = []
        output.append(f"# {fitness_plan.name}")
        output.append(f"**Goal:** {fitness_plan.goal}")
        output.append(f"**Description:** {fitness_plan.description}")
        output.append(f"**Start Date:** {fitness_plan.start_date}")
        if fitness_plan.target_date:
            output.append(f"**Target Date:** {fitness_plan.target_date}")
        
        # Add training plan summary
        if hasattr(fitness_plan, 'training_plan') and fitness_plan.training_plan:
            output.append("\n## Training Plan")
            output.append(fitness_plan.training_plan.description)
        
        # Add meal plan summary
        if hasattr(fitness_plan, 'meal_plan') and fitness_plan.meal_plan:
            output.append("\n## Nutrition Plan")
            output.append(fitness_plan.meal_plan.description)
        
        return "\n".join(output)
    except Exception as e:
        return f"Error formatting fitness plan: {str(e)}"


__all__ = ['Config', 'setup_logging', 'format_fitness_plan_for_display']
