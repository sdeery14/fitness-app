"""
Pydantic models for the fitness agent.
"""
from pydantic import BaseModel
from typing import Optional, List


class FitnessPlan(BaseModel):
    """Structured fitness plan model."""
    name: str
    training_plan: str
    meal_plan: str


class AgentResponse(BaseModel):
    """Standard agent response format."""
    content: str
    plan: Optional[FitnessPlan] = None
    metadata: Optional[dict] = None


class ConversationMessage(BaseModel):
    """Individual conversation message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class AgentConfig(BaseModel):
    """Configuration for the fitness agent."""
    model_name: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    custom_instructions: Optional[str] = None
