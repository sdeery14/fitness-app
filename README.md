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

Your personal fitness companion for workout plans, meal planning, and fitness guidance powered by Anthropic's Claude models.

## ✨ Features

- **🏋️ Personalized Workout Plans**: Custom routines based on your fitness level and goals
- **🥗 Meal Planning**: Tailored nutrition plans for weight loss, muscle gain, or general health
- **💡 Fitness Guidance**: Expert advice on exercises, form, and best practices
- **🤖 Multiple AI Models**: Choose from Claude-3.5-Haiku to Claude-4-Opus based on your needs
- **💬 Interactive Chat**: Conversational interface with memory and context
- **⚡ Real-time Streaming**: See responses generated live

## 🚀 Quick Start

### Option 1: Run Locally
```bash
# Clone the repository
git clone <your-repo-url>
cd fitness-app

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Launch the app
python fitness_agent/app.py
```

### Option 2: Use the Interface
1. **Select your AI model** from the dropdown (default: claude-3.5-haiku)
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
