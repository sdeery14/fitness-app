from pydantic import BaseModel
from agents import Agent, Runner
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()


class FitnessPlan(BaseModel):
    name: str
    training_plan: str
    meal_plan: str


class FitnessAgent(Agent):
    """
    A helpful assistant for general fitness guidance and handoffs to a plan-building agent.
    
    Supports current LiteLLM Anthropic models (as of January 2025):
    - Claude-4: claude-opus-4-20250514, claude-sonnet-4-20250514 (Premium)
    - Claude-3.7: claude-3-7-sonnet-20250219 (Extended thinking)
    - Claude-3.5: claude-3-5-sonnet-20241022 (latest), claude-3-5-sonnet-20240620 (stable), claude-3-5-haiku-20241022 (fast)
    - Claude-3: claude-3-haiku-20240307 (legacy but reliable)
    
    Note: Some older models (claude-3-opus, claude-3-sonnet, claude-2.x, claude-instant) 
    have been deprecated and removed from the API.
    """

    # Available Anthropic models via LiteLLM
    # Updated to match current Anthropic API as of January 2025
    SUPPORTED_MODELS = {
        # Claude-4 models (latest generation - may require special access)
        "claude-4-opus": "claude-opus-4-20250514",
        "claude-4-sonnet": "claude-sonnet-4-20250514",
        
        # Claude-3.7 models (newest stable)
        "claude-3.7-sonnet": "claude-3-7-sonnet-20250219",
        
        # Claude-3.5 models (widely available)
        "claude-3.5-sonnet-latest": "claude-3-5-sonnet-20241022",  # Latest version
        "claude-3.5-sonnet": "claude-3-5-sonnet-20240620",        # Previous stable version
        "claude-3.5-haiku": "claude-3-5-haiku-20241022",          # New Haiku 3.5 model
        
        # Claude-3 models (legacy but still available)
        "claude-3-haiku": "claude-3-haiku-20240307",
        # Note: claude-3-opus and claude-3-sonnet have been deprecated/removed
    }

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Fitness Agent with configurable Anthropic model.
        
        Args:
            model_name: Name of the Anthropic model to use. Can be a key from SUPPORTED_MODELS
                       or a full model identifier. Defaults to claude-3-haiku if not specified.
                       Can also be set via ANTHROPIC_MODEL environment variable.
        """
        # Determine which model to use
        if model_name is None:
            # Check environment variable first, default to the newest fast model
            model_name = os.getenv("ANTHROPIC_MODEL", "claude-3.5-haiku")
        
        # Validate the model name
        is_valid, validation_message = self.validate_model_name(model_name)
        if not is_valid:
            print(f"Warning: {validation_message}")
            print(f"Falling back to default model: claude-3.5-haiku")
            model_name = "claude-3.5-haiku"
        
        # Resolve model name to full identifier
        if model_name in self.SUPPORTED_MODELS:
            full_model_name = self.SUPPORTED_MODELS[model_name]
        else:
            # Assume it's already a full model identifier
            full_model_name = model_name
        
        # Add litellm/anthropic/ prefix if not already present
        if not full_model_name.startswith("litellm/anthropic/"):
            litellm_model = f"litellm/anthropic/{full_model_name}"
        else:
            litellm_model = full_model_name

        # Store the model information for debugging
        self.model_name = model_name
        self.full_model_name = full_model_name
        self.litellm_model = litellm_model

        fitness_plan_agent = Agent(
            name="Fitness Plan Assistant",
            instructions="You are a helpful assistant for creating personalized fitness plans.",
            model=litellm_model,
            output_type=FitnessPlan
        )

        super().__init__(
            name="Fitness Assistant",
            model=litellm_model,
            instructions="""
            You are a helpful assistant for fitness-related queries.
            
            If the user wants to create a fitness plan, hand them off to the Fitness Plan Assistant.
            """,
            handoffs=[fitness_plan_agent]
        )

    @classmethod
    def list_supported_models(cls) -> dict:
        """Return a dictionary of supported model names and their full identifiers."""
        return cls.SUPPORTED_MODELS.copy()

    @classmethod
    def get_model_info(cls, model_name: str) -> str:
        """Get information about a specific model."""
        model_info = {
            "claude-4-opus": "Most capable and intelligent model. Superior reasoning, complex tasks (Premium tier)",
            "claude-4-sonnet": "High-performance model with exceptional reasoning and efficiency (Premium tier)",
            "claude-3.7-sonnet": "Enhanced model with extended thinking capabilities (Recommended)",
            "claude-3.5-sonnet-latest": "Latest Claude 3.5 Sonnet with improved capabilities (Recommended)",
            "claude-3.5-sonnet": "Excellent balance of intelligence and speed (Stable version)",
            "claude-3.5-haiku": "Fast and compact model for near-instant responsiveness (New!)",
            "claude-3-haiku": "Fastest model, good for simple tasks and cost-effective (Legacy but reliable)",
        }
        return model_info.get(model_name, "Model information not available")

    @classmethod
    def get_recommended_models(cls) -> list:
        """Get a list of recommended models that are most likely to be available."""
        return [
            "claude-3-haiku",           # Most reliable, widely available, cost-effective
            "claude-3.5-haiku",        # New fast model
            "claude-3.5-sonnet",       # Stable version, widely available
            "claude-3.5-sonnet-latest", # Latest improvements
            "claude-3.7-sonnet",       # Newest stable with extended thinking
        ]

    @classmethod
    def validate_model_name(cls, model_name: str) -> tuple[bool, str]:
        """
        Validate if a model name is in our supported list and provide helpful feedback.
        
        Returns:
            tuple: (is_valid, message)
        """
        if model_name in cls.SUPPORTED_MODELS:
            full_name = cls.SUPPORTED_MODELS[model_name]
            return True, f"Valid model: {model_name} -> {full_name}"
        elif model_name in cls.SUPPORTED_MODELS.values():
            return True, f"Valid full model identifier: {model_name}"
        else:
            recommended = ", ".join(cls.get_recommended_models())
            return False, f"Model '{model_name}' not found. Recommended models: {recommended}"


if __name__ == "__main__":
    # Example usage with different models
    print("Available Anthropic models:")
    for name, full_id in FitnessAgent.list_supported_models().items():
        print(f"  {name}: {full_id}")
        print(f"    {FitnessAgent.get_model_info(name)}")
    
    print("\n" + "="*50 + "\n")
    
    # Create agent with new default model (claude-3.5-haiku)
    print("Creating agent with new default model (claude-3.5-haiku)...")
    agent = FitnessAgent()
    
    # You can also specify a different model:
    # agent = FitnessAgent("claude-3.5-sonnet")  # Using friendly name
    # agent = FitnessAgent("claude-3-5-sonnet-20241022")  # Using full identifier
    
    result = Runner.run_sync(agent, "Hello. Please make me a fitness plan.")
    print(result.final_output)