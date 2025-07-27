"""
Agents module for the fitness core library.
"""
from .base import FitnessAgent
from .models import FitnessPlan, AgentResponse, ConversationMessage, AgentConfig
from .providers import ModelProvider

__all__ = [
    'FitnessAgent',
    'FitnessPlan', 
    'AgentResponse',
    'ConversationMessage',
    'AgentConfig',
    'ModelProvider'
]
