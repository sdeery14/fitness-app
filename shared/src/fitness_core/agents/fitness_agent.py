"""
Main fitness agent implementation.
"""
from typing import Optional
from agents import Agent
from dotenv import load_dotenv

from .models import FitnessPlan, AgentConfig
from .providers import ModelProvider
from .fitness_plan_agent import FitnessPlanAgent

load_dotenv()


class FitnessAgent(Agent):
    """
    A helpful assistant for general fitness guidance and handoffs to a plan-building agent.
    
    Supports multiple AI providers via LiteLLM (as of January 2025):
    
    Anthropic models:
    - Claude-4: claude-opus-4-20250514, claude-sonnet-4-20250514 (Premium)
    - Claude-3.7: claude-3-7-sonnet-20250219 (Extended thinking)
    - Claude-3.5: claude-3-5-sonnet-20241022 (latest), claude-3-5-sonnet-20240620 (stable), claude-3-5-haiku-20241022 (fast)
    - Claude-3: claude-3-haiku-20240307 (legacy but reliable)
    
    OpenAI models:
    - GPT-4o: gpt-4o, gpt-4o-mini (Vision + latest capabilities)
    - GPT-4: gpt-4-turbo (Legacy but stable)
    - GPT-3.5: gpt-3.5-turbo (Cost-effective)
    - Reasoning: o1-preview, o1-mini, o3-mini (Advanced reasoning)
    
    Note: Some older models may be deprecated. Always check provider documentation.
    """

    def __init__(self, model_name: Optional[str] = None, config: Optional[AgentConfig] = None):
        """
        Initialize the Fitness Agent with configurable AI model (Anthropic or OpenAI).
        
        Args:
            model_name: Name of the AI model to use. Can be a key from SUPPORTED_MODELS
                       or a full model identifier. Defaults to gpt-4o-mini if not specified.
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

        # Create fitness plan agent with model-specific configuration
        fitness_plan_agent = FitnessPlanAgent.create_for_model(final_model, config)

        # Initialize parent Agent with improved instructions
        super().__init__(
            name="Fitness Assistant",
            model=final_model,
            instructions="""You are a professional fitness and nutrition assistant with expertise in creating personalized fitness programs.

CORE CAPABILITIES:
- Fitness program design and workout planning
- Nutrition guidance and meal planning  
- Exercise technique and form advice
- Goal setting and progress tracking
- Injury prevention and modification strategies

WHEN TO TRANSFER TO FITNESS PLAN ASSISTANT:
Transfer immediately when users request:
- "Create a workout plan" or "design a program"
- "I need a fitness plan" or "help me with a routine"
- "Build a meal plan" or nutrition planning
- Any structured fitness or nutrition program creation

CONVERSATION GUIDELINES:
- Be encouraging and supportive
- Ask clarifying questions about fitness level, goals, and preferences
- Provide evidence-based advice
- Consider individual limitations and equipment availability
- Always prioritize safety and proper form

For detailed fitness plan creation, immediately transfer to the Fitness Plan Assistant who will create comprehensive, structured programs.""",
            handoffs=[fitness_plan_agent]
        )

    @classmethod
    def list_supported_models(cls) -> dict:
        """Return a dictionary of supported model names and their full identifiers."""
        return ModelProvider.SUPPORTED_MODELS.copy()

    @classmethod
    def get_model_info(cls, model_name: str) -> str:
        """Get information about a specific model."""
        return ModelProvider.get_model_info(model_name)

    @classmethod
    def get_recommended_models(cls) -> list:
        """Get a list of recommended models that are most likely to be available."""
        return ModelProvider.get_recommended_models()

    @classmethod 
    def get_models_by_provider(cls) -> dict:
        """Get models organized by provider."""
        return ModelProvider.get_models_by_provider()

    @classmethod
    def get_models_table_data(cls) -> list:
        """Get model data formatted for table display."""
        return ModelProvider.get_models_table_data()

    @classmethod
    def validate_model_name(cls, model_name: str) -> tuple[bool, str]:
        """
        Validate if a model name is in our supported list and provide helpful feedback.
        
        Returns:
            tuple: (is_valid, message)
        """
        return ModelProvider.validate_model_name(model_name)
