"""
Agents module for the fitness core library.
"""
from .fitness_agent import FitnessAgent
from .models import AgentResponse, ConversationMessage, AgentConfig
from .structured_output_models import FitnessPlan
from .providers import ModelProvider

__all__ = [
    'FitnessAgent',
    'FitnessPlan', 
    'AgentResponse',
    'ConversationMessage',
    'AgentConfig',
    'ModelProvider'
]
