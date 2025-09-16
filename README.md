# 🏋️ Fitness AI Assistant

A personal AI-powered fitness and nutrition assistant that helps create personalized training plans and meal plans using state-of-the-art language models.

## ✨ Features

- **🤖 Multiple AI Models**: Choose from OpenAI (GPT-4), Anthropic (Claude), and Groq (Llama) models
- **💬 Conversational Interface**: Natural conversation with memory across sessions
- **📋 Personalized Plans**: Custom workout and meal plans based on your goals, fitness level, and equipment
- **👤 User Profiles**: The assistant remembers your preferences, goals, and limitations
- **🔄 Real-time Streaming**: See AI responses as they're generated
- **🎯 Smart Tools**: Built-in tools for creating fitness plans and managing user profiles
- **🌐 Web Interface**: Clean, easy-to-use Gradio web interface

## 🏗️ Project Structure

```
fitness-app/
├── fitness_agent/          # Core fitness agent logic
│   ├── __init__.py
│   ├── agents.py           # Main FitnessAgent class
│   ├── models.py           # Data models (FitnessPlan, TrainingPlan, etc.)
│   ├── services.py         # Agent runner and model providers
│   ├── memory.py           # User session and profile management
│   ├── tools.py            # Agent tools and functions
│   └── utils.py            # Configuration and utilities
├── gradio_app/             # Web interface
│   ├── __init__.py
│   └── app.py              # Gradio UI application
├── requirements.txt        # Python dependencies
├── app.py                  # Main entry point - run this!
└── README.md               # This file
```
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- API Keys: OpenAI, Anthropic, and/or Groq (at least one required)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd fitness-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Create a .env file with your API keys
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GROQ_API_KEY=your_groq_key_here
   ```

   Or set them directly:
   ```bash
   # Windows PowerShell
   $env:GROQ_API_KEY = "your_groq_key"
   $env:OPENAI_API_KEY = "your_openai_key"
   $env:ANTHROPIC_API_KEY = "your_anthropic_key"
   
   # Linux/Mac
   export GROQ_API_KEY="your_groq_key"
   export OPENAI_API_KEY="your_openai_key"
   export ANTHROPIC_API_KEY="your_anthropic_key"
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open in browser:**
   - Go to `http://localhost:7860`

## 🤖 AI Models

### Recommended Models (Fast & Free)

**Groq Models** (Recommended - Fast & Free):
- **llama-3.3-70b-versatile**: Best for complex fitness plans and detailed advice
- **llama-3.1-8b-instant**: Fastest responses for quick questions
- **mixtral-8x7b-32768**: Good balance of speed and capability

**OpenAI Models**:
- **gpt-4o-mini**: Efficient and capable, good balance of cost and performance
- **gpt-4o**: Most capable for complex reasoning and detailed plans

**Anthropic Models**:
- **claude-3.5-haiku**: Fast responses with good capability
- **claude-3.5-sonnet**: High-quality responses for detailed planning

### API Key Setup

Set your API key for your preferred provider:

```bash
# For Groq (recommended - fast & free)
GROQ_API_KEY=your_groq_key

# For OpenAI
OPENAI_API_KEY=your_openai_key

# For Anthropic
ANTHROPIC_API_KEY=your_anthropic_key
```

## 💬 Usage Guide

### Getting Started

1. **Tell the assistant about yourself:**
   - Your fitness goals (weight loss, muscle building, endurance, etc.)
   - Current fitness level (beginner, intermediate, advanced)
   - Available equipment (home gym, commercial gym, bodyweight only)
   - Any limitations, injuries, or preferences

2. **Ask for help:**
   - "Create a 12-week muscle building program"
   - "I'm a beginner, what should I start with?"
   - "Plan a nutrition strategy for weight loss"
   - "Design a home workout with no equipment"
   - "Update my fitness plan based on my progress"

### Example Conversations

```
You: I'm a beginner looking to lose weight. I have access to a gym.
GROQ_API_KEY=your_groq_key

# For OpenAI
OPENAI_API_KEY=your_openai_key

# For Anthropic
ANTHROPIC_API_KEY=your_anthropic_key
`

##  Usage Guide

### Getting Started

1. **Tell the assistant about yourself:**
   - Your fitness goals (weight loss, muscle building, endurance, etc.)
   - Current fitness level (beginner, intermediate, advanced)
   - Available equipment (home gym, commercial gym, bodyweight only)
   - Any limitations, injuries, or preferences

2. **Ask for help:**
   - Create a 12-week muscle building program
   - I'm a beginner, what should I start with?
   - Plan a nutrition strategy for weight loss
   - Design a home workout with no equipment
   - Update my fitness plan based on my progress

##  Configuration

Key configuration options in fitness_agent/utils.py:
- **SERVER_NAME**: Default 0.0.0.0 (all interfaces)
- **SERVER_PORT**: Default 7860
- **DEFAULT_MODEL**: Default llama-3.3-70b-versatile
- **DEBUG**: Set to true for development

##  Dependencies

Core dependencies:
- openai-agents[litellm]: AI agent framework
- gradio: Web interface
- pydantic: Data validation
- python-dotenv: Environment management

Optional:
- reportlab: PDF generation for fitness plans
- scipy: Scientific computing
- groq, openai, anthropic: Additional AI providers

##  Development

This simplified structure makes it easy to:
- **Understand the codebase**: Clear separation between agent logic and UI
- **Make changes**: Fewer files to navigate, simpler imports
- **Add features**: Extend the agent tools or UI components
- **Deploy**: Single requirements file, straightforward setup

### Adding Features

- **Agent tools**: Add to fitness_agent/tools.py
- **UI components**: Modify gradio_app/app.py
- **Models**: Add to fitness_agent/models.py
- **Core logic**: Edit fitness_agent/agents.py

### Code Style

- Use type hints
- Add docstrings for public functions
- Keep functions small and focused

##  Contributing

1. Fork the repository
2. Create a feature branch: git checkout -b feature/amazing-feature
3. Make your changes
4. Add tests for new functionality
5. Commit your changes: git commit -m 'Add amazing feature'
6. Push to the branch: git push origin feature/amazing-feature
7. Open a Pull Request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Support

- Always consult healthcare professionals before starting new exercise programs
- This AI assistant provides general guidance, not medical advice

##  Acknowledgments

- Built with OpenAI Agents library
- UI powered by Gradio
- Model support via LiteLLM

---

**Happy training! **
