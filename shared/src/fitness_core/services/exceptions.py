"""
Custom exceptions for the fitness app.
"""


class FitnessAppError(Exception):
    """Base exception for fitness app errors."""
    pass


class FitnessUIError(FitnessAppError):
    """Custom exception for UI-related errors."""
    pass


class AgentExecutionError(FitnessAppError):
    """Exception for agent execution errors."""
    pass


class ModelProviderError(FitnessAppError):
    """Exception for model provider errors."""
    pass


class ConversationError(FitnessAppError):
    """Exception for conversation management errors."""
    pass
