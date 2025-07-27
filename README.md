---
title: Fitness AI Assistant
emoji: 🏋️‍♀️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.38.1
app_file: fitness_agent/app.py
pinned: false
license: mit
---

# 🏋️‍♀️ Fitness AI Assistant

Your personal fitness companion for workout plans, meal planning, and fitness guidance powered by **multiple AI providers** - choose between Anthropic Claude and OpenAI GPT models!

## ✨ Features

- **🏋️ Personalized Workout Plans**: Custom routines based on your fitness level and goals
- **🥗 Meal Planning**: Tailored nutrition plans for weight loss, muscle gain, or general health  
- **💡 Fitness Guidance**: Expert advice on exercises, form, and best practices
- **🤖 Multiple AI Providers**: Choose from Anthropic Claude OR OpenAI GPT models
- **⚡ Model Flexibility**: Switch between models anytime for different capabilities
- **💬 Interactive Chat**: Conversational interface with memory and context
- **🔄 Real-time Streaming**: See responses generated live

## 🤖 Supported AI Models

### 🔵 Anthropic Claude Models
- **Claude-4**: claude-4-opus, claude-4-sonnet (Premium, most capable)
- **Claude-3.7**: claude-3.7-sonnet (Extended thinking)
- **Claude-3.5**: claude-3.5-sonnet, claude-3.5-haiku (Balanced, fast)
- **Claude-3**: claude-3-haiku (Cost-effective)

### 🟢 OpenAI GPT Models  
- **GPT-4o**: gpt-4o, gpt-4o-mini (Latest with vision)
- **GPT-4**: gpt-4-turbo (Large context window)
- **GPT-3.5**: gpt-3.5-turbo (Fast and economical)
- **Reasoning**: o1-preview, o1-mini, o3-mini (Advanced reasoning)

## 🚀 Quick Start

### Option 1: Run Locally
```bash
# Clone the repository
git clone <your-repo-url>
cd fitness-app

# Install dependencies
pip install -r requirements.txt

# Set up environment - choose your provider(s)
cp .env.example .env

# Edit .env and add your API key(s):
# For OpenAI models: OPENAI_API_KEY=your_openai_key_here
# For Anthropic models: ANTHROPIC_API_KEY=your_anthropic_key_here  
# For both providers: Set both keys!

# Launch the app
python fitness_agent/app.py
```

### Option 2: Use the Interface
1. **Select your AI provider and model** from the dropdown
   - 🔵 Anthropic models for detailed analysis and safety
   - 🟢 OpenAI models for familiar interface and vision capabilities
2. **Start chatting** about your fitness goals
3. **Be specific** about your level, equipment, and preferences
4. **Get personalized plans** and ask follow-up questions

## 🎯 Example Prompts

- "Create a beginner workout plan for me"
- "I want to lose weight - help me with a fitness plan"
- "Design a muscle building program for intermediate level"
- "I need a meal plan for gaining muscle mass"
- "Help me with a home workout routine with no equipment"

## 🤖 AI Model Options

| Model | Speed | Capability | Best For |
|-------|--------|------------|----------|
| claude-3.5-haiku | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Quick questions, cost-effective (default) |
| claude-3.5-sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Balanced performance, recommended |
| claude-3.7-sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Extended thinking, complex plans |
| claude-4-sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | High performance (premium) |
| claude-4-opus | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Maximum capability (premium) |

## 📚 Documentation

- **[Complete Model Guide](fitness_agent/COMPLETE_MODEL_GUIDE.md)** - Everything about AI models
- **[Examples](fitness_agent/examples.py)** - Code examples for different use cases
- **[Test Script](fitness_agent/test_updated_models.py)** - Test model availability

## 🛠️ Tech Stack

- **Backend**: Python, LiteLLM, Anthropic API
- **Frontend**: Gradio
- **AI Models**: Anthropic Claude (3.5-Haiku to 4-Opus)
- **Features**: Real-time streaming, conversation memory, model switching

---

*Built with ❤️ for fitness enthusiasts*

*Start your fitness journey today with personalized AI guidance!*
