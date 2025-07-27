# Fitness Agent - Complete Model Guide

This comprehensive guide covers everything you need to know about using different Anthropic models with the Fitness AI Assistant.

## 🤖 Currently Supported Models (January 2025)

Based on Anthropic's latest API, these models are currently available:

### Claude-4 (Latest Generation - Premium Tier)
- **claude-4-opus**: `claude-opus-4-20250514` - Most capable and intelligent model. Superior reasoning, complex tasks
- **claude-4-sonnet**: `claude-sonnet-4-20250514` - High-performance model with exceptional reasoning and efficiency

### Claude-3.7 (Extended Thinking)
- **claude-3.7-sonnet**: `claude-3-7-sonnet-20250219` - Enhanced model with extended thinking capabilities

### Claude-3.5 (Recommended for Most Users)
- **claude-3.5-sonnet-latest**: `claude-3-5-sonnet-20241022` - Latest Claude 3.5 Sonnet with improved capabilities
- **claude-3.5-sonnet**: `claude-3-5-sonnet-20240620` - Excellent balance of intelligence and speed (stable version)
- **claude-3.5-haiku**: `claude-3-5-haiku-20241022` - **NEW DEFAULT** - Fast and compact model for near-instant responsiveness

### Claude-3 (Legacy but Reliable)
- **claude-3-haiku**: `claude-3-haiku-20240307` - Cost-effective, good for simple tasks

### ❌ Deprecated Models (No Longer Available)
- claude-3-opus, claude-3-sonnet
- claude-2.1, claude-2
- claude-instant-1.2, claude-instant-1

## 🚀 Quick Start

### 1. Using the Gradio Interface

**Launch the app:**
```bash
python app.py
```

**Select a model:**
- Use the "🤖 AI Model" dropdown at the top
- Model changes automatically when selected (no button needed)
- Model information updates in real-time

### 2. Programmatic Usage

**Basic usage (uses default model):**
```python
from fitness_agent import FitnessAgent
from agents import Runner

agent = FitnessAgent()  # Uses claude-3.5-haiku by default
result = Runner.run_sync(agent, "Create a fitness plan for me.")
```

**Specify a specific model:**
```python
# Using friendly name
agent = FitnessAgent("claude-3.5-sonnet")

# Using full model identifier  
agent = FitnessAgent("claude-3-5-sonnet-20241022")
```

**Using environment variables:**
```env
# In your .env file
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_MODEL=claude-3.5-sonnet
```

## 📊 Model Comparison & Recommendations

| Model | Speed | Capability | Cost | Best For |
|-------|--------|------------|------|----------|
| claude-4-opus | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Complex analysis, detailed plans |
| claude-4-sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Balanced high performance |
| claude-3.7-sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Extended thinking, complex tasks |
| claude-3.5-sonnet-latest | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Latest improvements, recommended |
| claude-3.5-sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Stable, reliable choice |
| claude-3.5-haiku | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | **DEFAULT** - Fast responses |
| claude-3-haiku | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | Most cost-effective |

### 🎯 Use Case Recommendations

**For beginners/quick questions:**
- `claude-3.5-haiku` (default) - Fast and efficient
- `claude-3-haiku` - Most cost-effective

**For comprehensive fitness planning:**
- `claude-3.5-sonnet` - Great balance 
- `claude-3.5-sonnet-latest` - Latest improvements
- `claude-3.7-sonnet` - Extended thinking capabilities

**For complex analysis/detailed programs:**
- `claude-4-sonnet` - High performance
- `claude-4-opus` - Maximum capability (if available)

## 🔧 Configuration

### Environment Variables
```env
# Required
ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional - set default model
ANTHROPIC_MODEL=claude-3.5-haiku

# Optional - custom API base (for proxies)
ANTHROPIC_API_BASE=https://your-proxy-url.com
```

### Model Validation
The agent automatically validates model availability and falls back to the default if a model is not found.

## 🛠️ Features

### Seamless Model Switching
- Change models anytime in the UI
- Conversation history is preserved
- No need to restart the application

### Automatic Fallbacks
- Invalid models automatically fall back to default
- Streaming issues handled gracefully
- Clear error messages and suggestions

### Real-time Information
- Model capabilities and descriptions
- Performance and cost indicators
- Availability status

## 🔍 Testing & Debugging

**Test model availability:**
```bash
python test_updated_models.py
```

**List available models:**
```python
from fitness_agent import FitnessAgent

models = FitnessAgent.list_supported_models()
for name, full_id in models.items():
    print(f"{name}: {full_id}")
    print(f"  {FitnessAgent.get_model_info(name)}")
```

**Get recommended models:**
```python
recommended = FitnessAgent.get_recommended_models()
print("Recommended models:", recommended)
```

## 🚨 Troubleshooting

**"Model not found" errors:**
1. Check if the model is in the supported list
2. Verify your API key has access to the model
3. Claude-4 models may require special access
4. Try a recommended model from the list

**Streaming issues:**
- Some models automatically fall back to non-streaming mode
- This is normal behavior for certain Anthropic models
- Toggle streaming mode if you encounter issues

**Performance concerns:**
- Use `claude-3.5-haiku` for fastest responses
- Use `claude-3-haiku` for most cost-effective option
- Balance capability vs speed based on your needs

## 📚 Additional Resources

- [Anthropic Models Documentation](https://docs.anthropic.com/en/docs/about-claude/models/overview)
- [LiteLLM Anthropic Provider](https://docs.litellm.ai/docs/providers/anthropic)
- Test your setup with: `python test_updated_models.py`

---

*This guide is current as of January 2025. Model availability may change - always check the latest Anthropic documentation.*
