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

    # Available models via LiteLLM and native OpenAI
    # Updated to include both Anthropic and OpenAI models as of January 2025
    SUPPORTED_MODELS = {
        # === ANTHROPIC MODELS (via LiteLLM) ===
        # Claude-4 models (latest generation - may require special access)
        "claude-4-opus": "litellm/anthropic/claude-opus-4-20250514",
        "claude-4-sonnet": "litellm/anthropic/claude-sonnet-4-20250514",
        
        # Claude-3.7 models (newest stable)
        "claude-3.7-sonnet": "litellm/anthropic/claude-3-7-sonnet-20250219",
        
        # Claude-3.5 models (widely available)
        "claude-3.5-sonnet-latest": "litellm/anthropic/claude-3-5-sonnet-20241022",  # Latest version
        "claude-3.5-sonnet": "litellm/anthropic/claude-3-5-sonnet-20240620",        # Previous stable version
        "claude-3.5-haiku": "litellm/anthropic/claude-3-5-haiku-20241022",          # New Haiku 3.5 model
        
        # Claude-3 models (legacy but still available)
        "claude-3-haiku": "litellm/anthropic/claude-3-haiku-20240307",
        
        # === OPENAI MODELS (native) ===
        # GPT-4o models (latest generation with vision)
        "gpt-4o": "gpt-4o",                                     # Latest GPT-4o model
        "gpt-4o-mini": "gpt-4o-mini",                          # Compact version
        
        # GPT-4 models (previous generation)
        "gpt-4-turbo": "gpt-4-turbo",                          # Latest GPT-4 Turbo
        "gpt-4": "gpt-4",                                      # Original GPT-4
        
        # GPT-3.5 models (cost-effective)
        "gpt-3.5-turbo": "gpt-3.5-turbo",                     # Latest 3.5 turbo
        
        # Reasoning models (o-series)
        "o1-preview": "o1-preview",                            # Advanced reasoning
        "o1-mini": "o1-mini",                                  # Compact reasoning
        "o3-mini": "o3-mini",                                  # Latest reasoning model
    }

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the Fitness Agent with configurable AI model (Anthropic or OpenAI).
        
        Args:
            model_name: Name of the AI model to use. Can be a key from SUPPORTED_MODELS
                       or a full model identifier. Defaults to claude-3.5-haiku if not specified.
                       Can also be set via AI_MODEL, ANTHROPIC_MODEL, or OPENAI_MODEL environment variables.
        """
        # Determine which model to use
        if model_name is None:
            # Check environment variables in priority order
            model_name = (
                os.getenv("AI_MODEL") or 
                os.getenv("ANTHROPIC_MODEL") or 
                os.getenv("OPENAI_MODEL") or 
                "gpt-4o-mini"  # Default fallback - reliable OpenAI model
            )
        
        # Validate the model name
        is_valid, validation_message = self.validate_model_name(model_name)
        if not is_valid:
            print(f"Warning: {validation_message}")
            print(f"Falling back to default model: gpt-4o-mini")
            model_name = "gpt-4o-mini"
        
        # Resolve model name to full identifier
        if model_name in self.SUPPORTED_MODELS:
            full_model_name = self.SUPPORTED_MODELS[model_name]
        else:
            # Assume it's already a full model identifier
            full_model_name = model_name
        
        # Determine if this is an OpenAI model or needs LiteLLM prefix
        if self._is_openai_model(model_name, full_model_name):
            # Use native OpenAI model (no prefix needed)
            final_model = full_model_name
        else:
            # For Anthropic models, use the full model name as-is since it already has litellm/ prefix
            final_model = full_model_name

        # Store the model information for debugging
        self.model_name = model_name
        self.full_model_name = full_model_name
        self.final_model = final_model
        self.provider = self._get_provider(model_name, full_model_name)

        fitness_plan_agent = Agent(
            name="Fitness Plan Assistant",
            instructions="You are a helpful assistant for creating personalized fitness plans.",
            model=final_model,
            output_type=FitnessPlan
        )

        super().__init__(
            name="Fitness Assistant",
            model=final_model,
            instructions="""
            You are a helpful assistant for fitness-related queries.
            
            If the user wants to create a fitness plan, hand them off to the Fitness Plan Assistant.
            """,
            handoffs=[fitness_plan_agent]
        )

    def _is_openai_model(self, model_name: str, full_model_name: str) -> bool:
        """Check if this is an OpenAI model that should use native API."""
        # Check direct model name matches
        openai_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "o1-preview", "o1-mini", "o3-mini"]
        if model_name in openai_models:
            return True
        
        # Check for OpenAI indicators in model names
        openai_prefixes = ["gpt-", "o1-", "o3-", "openai/", "litellm/openai/"]
        for prefix in openai_prefixes:
            if prefix in model_name.lower() or prefix in full_model_name.lower():
                return True
        
        return False
    
    def _get_provider(self, model_name: str, full_model_name: str) -> str:
        """Determine the provider based on the model."""
        if self._is_openai_model(model_name, full_model_name):
            return "openai"
        elif "claude" in model_name.lower() or "anthropic" in full_model_name.lower():
            return "anthropic"
        else:
            return "unknown"

    @classmethod
    def list_supported_models(cls) -> dict:
        """Return a dictionary of supported model names and their full identifiers."""
        return cls.SUPPORTED_MODELS.copy()

    @classmethod
    def get_model_info(cls, model_name: str) -> str:
        """Get information about a specific model."""
        model_info = {
            # === ANTHROPIC MODELS ===
            "claude-4-opus": "Most capable and intelligent model. Superior reasoning, complex tasks (Premium tier)",
            "claude-4-sonnet": "High-performance model with exceptional reasoning and efficiency (Premium tier)", 
            "claude-3.7-sonnet": "Enhanced model with extended thinking capabilities (Recommended)",
            "claude-3.5-sonnet-latest": "Latest Claude 3.5 Sonnet with improved capabilities (Recommended)",
            "claude-3.5-sonnet": "Excellent balance of intelligence and speed (Stable version)",
            "claude-3.5-haiku": "Fast and compact model for near-instant responsiveness (New!)",
            "claude-3-haiku": "Fastest model, good for simple tasks and cost-effective (Legacy but reliable)",
            
            # === OPENAI MODELS ===
            "gpt-4o": "Latest GPT-4o with vision, web browsing, and advanced capabilities (Recommended)",
            "gpt-4o-mini": "Compact GPT-4o model - fast, capable, and cost-effective (Recommended)",
            "gpt-4-turbo": "GPT-4 Turbo with large context window and improved efficiency",
            "gpt-4": "Original GPT-4 model - highly capable but slower than turbo variants",
            "gpt-3.5-turbo": "Fast and cost-effective model, good for straightforward tasks",
            "o1-preview": "Advanced reasoning model with enhanced problem-solving (Preview)",
            "o1-mini": "Compact reasoning model for faster inference with good capabilities",
            "o3-mini": "Latest reasoning model with improved performance (New!)",
        }
        return model_info.get(model_name, "Model information not available")

    @classmethod
    def get_recommended_models(cls) -> list:
        """Get a list of recommended models that are most likely to be available."""
        return [
            # Anthropic recommendations (most reliable first)
            "claude-3.5-haiku",        # New fast model, default
            "claude-3-haiku",          # Most reliable, widely available, cost-effective
            "claude-3.5-sonnet",       # Stable version, widely available
            "claude-3.5-sonnet-latest", # Latest improvements
            "claude-3.7-sonnet",       # Newest stable with extended thinking
            
            # OpenAI recommendations  
            "gpt-4o-mini",             # Best balance of capability and cost
            "gpt-4o",                  # Latest flagship model
            "gpt-3.5-turbo",          # Most cost-effective OpenAI model
            "gpt-4-turbo",            # Solid previous generation
            "o1-mini",                # Good reasoning capabilities
        ]

    @classmethod 
    def get_models_by_provider(cls) -> dict:
        """Get models organized by provider."""
        models = cls.list_supported_models()
        providers = {
            "anthropic": {},
            "openai": {},
            "unknown": {}
        }
        
        for name, full_name in models.items():
            if "claude" in name.lower() or "anthropic" in full_name.lower():
                providers["anthropic"][name] = full_name
            elif any(indicator in name.lower() for indicator in ["gpt-", "o1-", "o3-", "openai/"]):
                providers["openai"][name] = full_name
            else:
                providers["unknown"][name] = full_name
                
        return providers

    @classmethod
    def get_models_table_data(cls) -> list:
        """Get model data formatted for table display."""
        models = cls.list_supported_models()
        table_data = []
        
        # Define capability ratings
        capability_ratings = {
            # Anthropic models
            "claude-4-opus": "★★★★★",
            "claude-4-sonnet": "★★★★☆", 
            "claude-3.7-sonnet": "★★★★☆",
            "claude-3.5-sonnet-latest": "★★★★☆",
            "claude-3.5-sonnet": "★★★★☆",
            "claude-3.5-haiku": "★★★☆☆",
            "claude-3-haiku": "★★★☆☆",
            # OpenAI models
            "gpt-4o": "★★★★★",
            "gpt-4o-mini": "★★★★☆",
            "gpt-4-turbo": "★★★★☆",
            "gpt-4": "★★★★☆",
            "gpt-3.5-turbo": "★★★☆☆",
            "o1-preview": "★★★★★",
            "o1-mini": "★★★★☆",
            "o3-mini": "★★★★☆",
        }
        
        # Define speed ratings
        speed_ratings = {
            # Anthropic models
            "claude-4-opus": "★★★☆☆",
            "claude-4-sonnet": "★★★★☆", 
            "claude-3.7-sonnet": "★★★★☆",
            "claude-3.5-sonnet-latest": "★★★★☆",
            "claude-3.5-sonnet": "★★★★☆",
            "claude-3.5-haiku": "★★★★★",
            "claude-3-haiku": "★★★★★",
            # OpenAI models
            "gpt-4o": "★★★★☆",
            "gpt-4o-mini": "★★★★★",
            "gpt-4-turbo": "★★★★☆",
            "gpt-4": "★★★☆☆",
            "gpt-3.5-turbo": "★★★★★",
            "o1-preview": "★★☆☆☆",
            "o1-mini": "★★★☆☆",
            "o3-mini": "★★★★☆",
        }
        
        # Define cost ratings (more stars = more expensive)
        cost_ratings = {
            # Anthropic models
            "claude-4-opus": "★★★★★",
            "claude-4-sonnet": "★★★★☆", 
            "claude-3.7-sonnet": "★★★☆☆",
            "claude-3.5-sonnet-latest": "★★★☆☆",
            "claude-3.5-sonnet": "★★★☆☆",
            "claude-3.5-haiku": "★★☆☆☆",
            "claude-3-haiku": "★☆☆☆☆",
            # OpenAI models
            "gpt-4o": "★★★★☆",
            "gpt-4o-mini": "★★☆☆☆",
            "gpt-4-turbo": "★★★★☆",
            "gpt-4": "★★★★☆",
            "gpt-3.5-turbo": "★☆☆☆☆",
            "o1-preview": "★★★★★",
            "o1-mini": "★★★☆☆",
            "o3-mini": "★★★☆☆",
        }
        
        recommended = cls.get_recommended_models()
        
        for model_name, full_path in models.items():
            provider = "🔵 Anthropic" if "claude" in model_name.lower() else "🟢 OpenAI"
            is_recommended = "⭐" if model_name in recommended else ""
            
            table_data.append([
                is_recommended,
                provider,
                model_name,
                capability_ratings.get(model_name, "★★★☆☆"),
                speed_ratings.get(model_name, "★★★☆☆"),
                cost_ratings.get(model_name, "★★★☆☆"),
                cls.get_model_info(model_name)
            ])
        
        return table_data

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
    print("🤖 Available AI Models (Anthropic + OpenAI):")
    print("=" * 60)
    
    # Show models by provider
    providers = FitnessAgent.get_models_by_provider()
    
    print("🔵 ANTHROPIC MODELS:")
    for name, full_id in providers["anthropic"].items():
        print(f"  • {name}: {full_id}")
        print(f"    {FitnessAgent.get_model_info(name)}")
        print()
    
    print("🟢 OPENAI MODELS:")
    for name, full_id in providers["openai"].items():
        print(f"  • {name}: {full_id}")
        print(f"    {FitnessAgent.get_model_info(name)}")
        print()
    
    print("🎯 RECOMMENDED MODELS (most likely to work):")
    recommended = FitnessAgent.get_recommended_models()
    for model in recommended:
        provider_icon = "🔵" if "claude" in model else "🟢" if any(x in model for x in ["gpt", "o1", "o3"]) else "⚪"
        print(f"  {provider_icon} {model}")
    
    print("\n" + "="*60 + "\n")
    
    # Create agent with default model
    print("Creating agent with default model (gpt-4o-mini)...")
    agent = FitnessAgent()
    print(f"✅ Created agent:")
    print(f"   Model name: {agent.model_name}")
    print(f"   Provider: {agent.provider}")
    print(f"   Final model: {agent.final_model}")
    
    print("\n" + "="*60 + "\n")
    
    # Example with OpenAI model
    print("Creating agent with OpenAI model (gpt-4o-mini)...")
    try:
        openai_agent = FitnessAgent("gpt-4o-mini")
        print(f"✅ Created OpenAI agent:")
        print(f"   Model name: {openai_agent.model_name}")
        print(f"   Provider: {openai_agent.provider}")
        print(f"   Final model: {openai_agent.final_model}")
    except Exception as e:
        print(f"⚠️ Could not create OpenAI agent: {e}")
        print("   (This is normal if you don't have OPENAI_API_KEY set)")
    
    print("\n💡 To actually run the agents:")
    print("   - Set ANTHROPIC_API_KEY for Claude models")
    print("   - Set OPENAI_API_KEY for GPT models")
    print("   - Use Runner.run_sync(agent, 'your message') to chat")
    
    # Uncomment this to test with actual API call:
    # result = Runner.run_sync(agent, "Hello. Please make me a fitness plan.")
    # print(result.final_output)