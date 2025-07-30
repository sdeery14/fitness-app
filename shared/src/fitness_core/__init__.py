"""
Fitness Core - Shared business logic and AI agents.

This package contains the core functionality that can be shared across
different user interfaces (Gradio, FastAPI, CLI, etc.).
"""

__version__ = "0.1.0"

# Core exports
from .agents import FitnessAgent, FitnessPlanAgent, FitnessPlan, ModelProvider
from .services import ConversationManager, AgentRunner, ResponseFormatter
from .utils import Config, setup_logging, get_logger

__all__ = [
    # Agents
    'FitnessAgent',
    'FitnessPlanAgent',
    'FitnessPlan', 
    'ModelProvider',
    
    # Services
    'ConversationManager',
    'AgentRunner',
    'ResponseFormatter',
    
    # Utils
    'Config',
    'setup_logging',
    'get_logger'
]
