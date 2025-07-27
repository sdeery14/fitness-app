"""
AI model provider management and configuration.
"""
import os
from typing import Dict, List, Tuple, Optional
from .models import AgentConfig


class ModelProvider:
    """Manages AI model configurations and provider-specific logic."""

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
        
        # === GROQ MODELS (via LiteLLM) ===
        # Llama models (Meta)
        "llama-3.3-70b-versatile": "litellm/groq/llama-3.3-70b-versatile",     # Latest Llama 3.3
        "llama-3.1-8b-instant": "litellm/groq/llama-3.1-8b-instant",           # Fast Llama 3.1 8B
        "llama3-8b-8192": "litellm/groq/llama3-8b-8192",                       # Llama 3 8B with 8K context
        "llama3-70b-8192": "litellm/groq/llama3-70b-8192",                     # Llama 3 70B with 8K context
        
        # Gemma models (Google)
        "gemma2-9b-it": "litellm/groq/gemma2-9b-it",                           # Gemma 2 9B instruction-tuned
        
        # Mixtral models (Mistral)
        "mixtral-8x7b-32768": "litellm/groq/mixtral-8x7b-32768",               # Mixtral 8x7B with 32K context
        
        # Other featured models
        "qwen3-32b": "litellm/groq/qwen/qwen3-32b",                            # Qwen 3 32B
        "kimi-k2-instruct": "litellm/groq/moonshotai/kimi-k2-instruct",        # Kimi K2 MoE model
        
        # Whisper models (Speech-to-Text)
        "whisper-large-v3": "litellm/groq/whisper-large-v3",                   # Whisper Large v3
        "whisper-large-v3-turbo": "litellm/groq/whisper-large-v3-turbo",       # Whisper Large v3 Turbo
        "o3-mini": "o3-mini",                                  # Latest reasoning model
    }

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
            
            # === GROQ MODELS ===
            "llama-3.3-70b-versatile": "Latest Llama 3.3 70B model - excellent for complex tasks (Meta via Groq)",
            "llama-3.1-8b-instant": "Fast Llama 3.1 8B model - great for quick responses (Meta via Groq)",
            "llama3-8b-8192": "Llama 3 8B with 8K context window - efficient and capable (Meta via Groq)",
            "llama3-70b-8192": "Llama 3 70B with 8K context window - high performance (Meta via Groq)",
            "gemma2-9b-it": "Google Gemma 2 9B instruction-tuned - efficient and smart (Google via Groq)",
            "mixtral-8x7b-32768": "Mistral Mixtral 8x7B with 32K context - excellent reasoning (Mistral via Groq)",
            "qwen3-32b": "Alibaba Qwen 3 32B - advanced multilingual capabilities (Alibaba via Groq)",
            "kimi-k2-instruct": "Moonshot Kimi K2 MoE - 1T parameters with tool use (Moonshot via Groq)",
            "whisper-large-v3": "OpenAI Whisper Large v3 - best speech-to-text (OpenAI via Groq)",
            "whisper-large-v3-turbo": "OpenAI Whisper Large v3 Turbo - faster speech-to-text (OpenAI via Groq)",
        }
        return model_info.get(model_name, "Model information not available")

    @classmethod
    def get_recommended_models(cls) -> List[str]:
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
            
            # Groq recommendations (fast and cost-effective)
            "llama-3.3-70b-versatile", # Latest and most capable Llama model
            "llama-3.1-8b-instant",   # Fastest for simple tasks
            "gemma2-9b-it",           # Efficient Google model
            "mixtral-8x7b-32768",     # Excellent reasoning with large context
        ]

    @classmethod 
    def get_models_by_provider(cls) -> Dict[str, Dict[str, str]]:
        """Get models organized by provider."""
        models = cls.SUPPORTED_MODELS
        providers = {
            "anthropic": {},
            "openai": {},
            "groq": {},
            "unknown": {}
        }
        
        for name, full_name in models.items():
            if "claude" in name.lower() or "anthropic" in full_name.lower():
                providers["anthropic"][name] = full_name
            elif any(indicator in name.lower() for indicator in ["gpt-", "o1-", "o3-", "openai/"]):
                providers["openai"][name] = full_name
            elif "groq" in full_name.lower() or name in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-8b-8192", "llama3-70b-8192", "gemma2-9b-it", "mixtral-8x7b-32768", "qwen3-32b", "kimi-k2-instruct", "whisper-large-v3", "whisper-large-v3-turbo"]:
                providers["groq"][name] = full_name
            else:
                providers["unknown"][name] = full_name
                
        return providers

    @classmethod
    def get_models_table_data(cls) -> List[List[str]]:
        """Get model data formatted for table display."""
        models = cls.SUPPORTED_MODELS
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
            # Groq models
            "llama-3.3-70b-versatile": "★★★★☆",
            "llama-3.1-8b-instant": "★★★☆☆",
            "llama3-8b-8192": "★★★☆☆",
            "llama3-70b-8192": "★★★★☆",
            "gemma2-9b-it": "★★★☆☆",
            "mixtral-8x7b-32768": "★★★★☆",
            "qwen3-32b": "★★★★☆",
            "kimi-k2-instruct": "★★★★★",
            "whisper-large-v3": "★★★★★",
            "whisper-large-v3-turbo": "★★★★☆",
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
            # Groq models (Groq is known for speed!)
            "llama-3.3-70b-versatile": "★★★★★",
            "llama-3.1-8b-instant": "★★★★★",
            "llama3-8b-8192": "★★★★★",
            "llama3-70b-8192": "★★★★★",
            "gemma2-9b-it": "★★★★★",
            "mixtral-8x7b-32768": "★★★★★",
            "qwen3-32b": "★★★★★",
            "kimi-k2-instruct": "★★★★☆",
            "whisper-large-v3": "★★★★☆",
            "whisper-large-v3-turbo": "★★★★★",
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
            # Groq models (very cost-effective)
            "llama-3.3-70b-versatile": "★☆☆☆☆",
            "llama-3.1-8b-instant": "★☆☆☆☆",
            "llama3-8b-8192": "★☆☆☆☆",
            "llama3-70b-8192": "★☆☆☆☆",
            "gemma2-9b-it": "★☆☆☆☆",
            "mixtral-8x7b-32768": "★☆☆☆☆",
            "qwen3-32b": "★☆☆☆☆",
            "kimi-k2-instruct": "★★☆☆☆",
            "whisper-large-v3": "★☆☆☆☆",
            "whisper-large-v3-turbo": "★☆☆☆☆",
        }
        
        recommended = cls.get_recommended_models()
        
        for model_name, full_path in models.items():
            if "claude" in model_name.lower():
                provider = "🔵 Anthropic"
            elif "groq" in full_path.lower() or model_name in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-8b-8192", "llama3-70b-8192", "gemma2-9b-it", "mixtral-8x7b-32768", "qwen3-32b", "kimi-k2-instruct", "whisper-large-v3", "whisper-large-v3-turbo"]:
                # Show actual model provider with Groq hosting indication
                if model_name.startswith("llama"):
                    provider = "🚀 Meta (via Groq)"
                elif model_name.startswith("gemma"):
                    provider = "🚀 Google (via Groq)"
                elif model_name.startswith("mixtral"):
                    provider = "🚀 Mistral (via Groq)"
                elif model_name.startswith("qwen"):
                    provider = "🚀 Alibaba (via Groq)"
                elif model_name.startswith("kimi"):
                    provider = "� Moonshot (via Groq)"
                elif model_name.startswith("whisper"):
                    provider = "🚀 OpenAI (via Groq)"
                else:
                    provider = "🚀 Groq"
            elif any(indicator in model_name.lower() for indicator in ["gpt-", "o1-", "o3-"]):
                provider = "�🟢 OpenAI"
            else:
                provider = "❓ Unknown"
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
    def validate_model_name(cls, model_name: str) -> Tuple[bool, str]:
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

    @classmethod
    def is_openai_model(cls, model_name: str, full_model_name: str) -> bool:
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
    
    @classmethod
    def get_provider(cls, model_name: str, full_model_name: str) -> str:
        """Determine the provider based on the model."""
        if cls.is_openai_model(model_name, full_model_name):
            return "openai"
        elif "claude" in model_name.lower() or "anthropic" in full_model_name.lower():
            return "anthropic"
        elif "groq" in full_model_name.lower() or model_name in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-8b-8192", "llama3-70b-8192", "gemma2-9b-it", "mixtral-8x7b-32768", "qwen3-32b", "kimi-k2-instruct", "whisper-large-v3", "whisper-large-v3-turbo"]:
            return "groq"
        else:
            return "unknown"

    @classmethod
    def resolve_model_name(cls, model_name: Optional[str] = None) -> str:
        """
        Resolve model name from various sources (env vars, default, etc.).
        
        Args:
            model_name: Explicit model name, if provided
            
        Returns:
            Resolved model name
        """
        if model_name is None:
            # Check environment variables in priority order
            model_name = (
                os.getenv("AI_MODEL") or 
                os.getenv("ANTHROPIC_MODEL") or 
                os.getenv("OPENAI_MODEL") or 
                os.getenv("GROQ_MODEL") or
                "gpt-4o-mini"  # Default fallback - reliable OpenAI model
            )
        
        # Validate the model name
        is_valid, validation_message = cls.validate_model_name(model_name)
        if not is_valid:
            print(f"Warning: {validation_message}")
            print(f"Falling back to default model: gpt-4o-mini")
            model_name = "gpt-4o-mini"
        
        return model_name

    @classmethod
    def get_final_model_identifier(cls, model_name: str) -> str:
        """
        Get the final model identifier to use with the agents library.
        
        Args:
            model_name: Model name (key or full identifier)
            
        Returns:
            Final model identifier for the agents library
        """
        # Resolve model name to full identifier
        if model_name in cls.SUPPORTED_MODELS:
            full_model_name = cls.SUPPORTED_MODELS[model_name]
        else:
            # Assume it's already a full model identifier
            full_model_name = model_name
        
        # Determine if this is an OpenAI model or needs LiteLLM prefix
        if cls.is_openai_model(model_name, full_model_name):
            # Use native OpenAI model (no prefix needed)
            final_model = full_model_name
        else:
            # For Anthropic and Groq models, use the full model name as-is since it already has litellm/ prefix
            final_model = full_model_name
        
        return final_model
