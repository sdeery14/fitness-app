"""
Main fitness agent implementation.
"""
from typing import Optional
from datetime import datetime
from agents import Agent
from dotenv import load_dotenv

from .models import AgentConfig
from .services import ModelProvider
from .tools import get_tool_functions, get_combined_instructions
from .memory import SessionManager, UserProfile

load_dotenv()


class FitnessAgent(Agent):
    """
    A helpful assistant for general fitness guidance and handoffs to a plan-building agent.
    """

    def __init__(self, model_name: Optional[str] = None, config: Optional[AgentConfig] = None):
        """
        Initialize the Fitness Agent with configurable AI model (Anthropic or OpenAI).
        
        Args:
            model_name: Name of the AI model to use. Can be a key from SUPPORTED_MODELS
                       or a full model identifier. Defaults to llama-3.3-70b-versatile if not specified.
                       Can also be set via AI_MODEL, ANTHROPIC_MODEL, or OPENAI_MODEL environment variables.
            config: Optional AgentConfig for additional configuration
        """
        # Resolve model name
        resolved_model_name = ModelProvider.resolve_model_name(model_name)
        final_model = ModelProvider.get_final_model_identifier(resolved_model_name)

        # Store the model information for debugging
        self.model_name = resolved_model_name
        self.full_model_name = ModelProvider.SUPPORTED_MODELS.get(resolved_model_name, resolved_model_name)
        self.final_model = final_model
        self.provider = ModelProvider.get_provider(resolved_model_name, self.full_model_name)
        self.config = config

        # Load user profile for context
        self._load_user_profile()

        # Get tools and instructions dynamically
        tools = get_tool_functions()
        tool_instructions = get_combined_instructions()

        # Build system prompt with user context
        system_prompt = self._build_system_prompt(tool_instructions)

        # Initialize parent Agent
        super().__init__(
            name="Fitness Assistant",
            model=final_model,
            instructions=system_prompt,
            tools=tools
        )

    def _load_user_profile(self) -> None:
        """Load current user profile into agent context."""
        try:
            session = SessionManager.get_current_session()
            self.user_profile = session.profile if session else None
            self._profile_loaded_at = datetime.now()
        except Exception:
            self.user_profile = None
            self._profile_loaded_at = datetime.now()

    def refresh_user_profile(self) -> None:
        """Refresh user profile - useful for long conversations."""
        self._load_user_profile()

    def _format_profile_context(self) -> str:
        """Format user profile for system prompt context."""
        if not self.user_profile:
            return ""
        
        profile = self.user_profile
        
        # Check if the user profile has meaningful data
        if not any([
            profile.name,
            profile.age,
            profile.fitness_level,
            profile.goals,
            profile.equipment_available
        ]):
            return ""
        context_parts = []
        
        if profile.name:
            context_parts.append(f"User's name: {profile.name}")
        if profile.age:
            context_parts.append(f"Age: {profile.age}")
        if profile.fitness_level:
            context_parts.append(f"Fitness level: {profile.fitness_level}")
        if profile.goals:
            context_parts.append(f"Goals: {', '.join(profile.goals)}")
        if profile.equipment_available:
            context_parts.append(f"Available equipment: {', '.join(profile.equipment_available)}")
        if profile.medical_conditions:
            context_parts.append(f"Medical considerations: {', '.join(profile.medical_conditions)}")
            
        return "\n".join(context_parts)

    def _build_system_prompt(self, tool_instructions: str) -> str:
        """Build the system prompt including user profile context."""
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        base_prompt = f"""You are a professional fitness and nutrition assistant with expertise in working with users to create a personalized fitness plan.

Current date and time: {current_datetime}

You create personalized plans by iteratively creating plans and asking the user for feedback.

Create the first plan as soon as the user asks for a fitness plan, and then iterate on it based on their feedback.

Never ask for feedback before creating a new plan based on what you already know.

You provide short, concise responses in conversation, generally no longer than one or two sentences.

Unless specified otherwise, do not respond with any lists or bullet points. Talk like a normal person.

{tool_instructions}

Do not talk about anything outside of fitness and nutrition, and do not provide any medical advice. Always recommend that the user consults with a healthcare provider before starting any new fitness program."""

        # Add user profile context if available
        profile_context = self._format_profile_context()
        if profile_context:
            return f"""{base_prompt}

USER PROFILE:
{profile_context}

Remember this information about the user when providing recommendations and creating fitness plans."""
        
        return base_prompt
