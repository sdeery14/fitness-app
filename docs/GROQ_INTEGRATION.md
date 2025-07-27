# Groq Models Integration

This document explains how to use Groq models in your fitness app through LiteLLM integration.

## Overview

Groq provides extremely fast inference speeds for open-source models at very competitive prices. The following Groq models have been integrated into your fitness app:

## Available Models

### Production Models (Recommended)
- **llama-3.3-70b-versatile** - Latest Llama 3.3 70B model, excellent for complex tasks
- **llama-3.1-8b-instant** - Fast Llama 3.1 8B model, great for quick responses  
- **gemma2-9b-it** - Google Gemma 2 9B instruction-tuned, efficient and smart
- **mixtral-8x7b-32768** - Mistral Mixtral 8x7B with 32K context, excellent reasoning

### Additional Models
- **llama-3.1-70b-versatile** - Llama 3.1 70B model, powerful and versatile
- **llama3-8b-8192** - Llama 3 8B with 8K context window
- **llama3-70b-8192** - Llama 3 70B with 8K context window  
- **llama2-70b-4096** - Llama 2 70B with 4K context window (legacy)
- **gemma-7b-it** - Google Gemma 7B instruction-tuned
- **qwen3-32b** - Alibaba Qwen 3 32B with multilingual capabilities
- **kimi-k2-instruct** - Moonshot Kimi K2 MoE with 1T parameters

### Speech Models
- **whisper-large-v3** - OpenAI Whisper Large v3 for speech-to-text
- **whisper-large-v3-turbo** - Faster version of Whisper Large v3

## Setup

### 1. API Key Configuration

Make sure you have your Groq API key set up:

```bash
# In your .env file
GROQ_API_KEY=your-groq-api-key-here

# Or as environment variable
export GROQ_API_KEY=your-groq-api-key-here
```

### 2. Model Selection

You can specify Groq models in several ways:

```bash
# Set as primary AI model
export AI_MODEL=llama-3.3-70b-versatile

# Set as Groq-specific model
export GROQ_MODEL=llama-3.1-8b-instant
```

## Usage in Code

### Basic Usage

```python
from fitness_core.agents.providers import ModelProvider

# Get the final model identifier for LiteLLM
model_name = "llama-3.3-70b-versatile"
final_model = ModelProvider.get_final_model_identifier(model_name)
# Returns: "litellm/groq/llama-3.3-70b-versatile"

# Get model information
info = ModelProvider.get_model_info(model_name)
print(info)  # "Latest Llama 3.3 70B model - excellent for complex tasks (Groq)"
```

### Provider Detection

```python
# Check which provider a model belongs to
provider = ModelProvider.get_provider("llama-3.3-70b-versatile", "litellm/groq/llama-3.3-70b-versatile")
print(provider)  # "groq"

# Get all models by provider
providers = ModelProvider.get_models_by_provider()
groq_models = providers["groq"]
```

### Model Validation

```python
# Validate a model name
is_valid, message = ModelProvider.validate_model_name("llama-3.3-70b-versatile")
print(f"Valid: {is_valid}, Message: {message}")
```

## Model Comparison

| Model | Capability | Speed | Cost | Best For |
|-------|------------|--------|------|----------|
| llama-3.3-70b-versatile | ★★★★☆ | ★★★★★ | ★☆☆☆☆ | Complex reasoning tasks |
| llama-3.1-8b-instant | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | Quick responses, chat |
| gemma2-9b-it | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | General purpose, efficient |
| mixtral-8x7b-32768 | ★★★★☆ | ★★★★★ | ★☆☆☆☆ | Large context reasoning |
| whisper-large-v3-turbo | ★★★★☆ | ★★★★★ | ★☆☆☆☆ | Speech transcription |

## Integration with Agents

The Groq models work seamlessly with your fitness app's agent system through LiteLLM:

```python
# The models are automatically configured to work with:
# - Agent initialization
# - LiteLLM model loading
# - Conversation handling
# - Error handling and fallbacks
```

## Benefits of Groq

1. **Speed**: Extremely fast inference, ideal for real-time applications
2. **Cost**: Very cost-effective compared to proprietary models
3. **Quality**: High-quality open-source models with excellent performance
4. **Reliability**: Stable API with good uptime
5. **Variety**: Multiple model sizes and types for different use cases

## Best Practices

### Model Selection
- **Quick interactions**: Use `llama-3.1-8b-instant`
- **Complex tasks**: Use `llama-3.3-70b-versatile`
- **Balanced performance**: Use `gemma2-9b-it`
- **Large context**: Use `mixtral-8x7b-32768`

### Error Handling
The system includes automatic fallbacks if a Groq model is unavailable:
1. Falls back to other recommended models
2. Provides clear error messages
3. Maintains conversation continuity

### Environment Variables Priority
1. `AI_MODEL` - Primary model selection
2. `GROQ_MODEL` - Groq-specific model
3. `ANTHROPIC_MODEL` - Anthropic fallback
4. `OPENAI_MODEL` - OpenAI fallback
5. Default: `gpt-4o-mini`

## Testing

Run the included test scripts to verify your setup:

```bash
# Test Groq model configuration
python test_groq_models.py

# See usage examples
python groq_example.py
```

## Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: GROQ_API_KEY not found
   Solution: Set GROQ_API_KEY in your .env file
   ```

2. **Model Not Found**
   ```
   Error: Model 'xyz' not found
   Solution: Use ModelProvider.get_recommended_models() to see available models
   ```

3. **LiteLLM Import Error**
   ```
   Error: No module named 'litellm'
   Solution: Install with `pip install litellm` or check dependencies
   ```

## Support

- Groq Documentation: https://console.groq.com/docs
- LiteLLM Groq Provider: https://docs.litellm.ai/docs/providers/groq
- Model List: Use `ModelProvider.get_models_by_provider()["groq"]`
