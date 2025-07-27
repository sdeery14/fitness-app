# 🏋️ Fitness AI Assistant

An AI-powered fitness companion that provides personalized workout plans, meal planning, and fitness guidance using state-of-the-art language models.

## ✨ Features

- **🎤 Voice Input**: Record voice messages using Groq's Whisper for speech-to-text
- **🤖 Multiple AI Models**: Choose from OpenAI, Anthropic, and Groq models
- **� Conversational Interface**: Natural conversation with memory across sessions
- **📋 Personalized Plans**: Custom workout and meal plans based on your goals
- **🔄 Real-time Streaming**: See AI responses as they're generated
- **📁 File Support**: Upload documents for context

## �🚀 Quick Start

### Prerequisites
- Python 3.12+
- Poetry (for dependency management)
- API Keys: OpenAI, Anthropic, and/or Groq

### Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd fitness-app
   ```

2. **Install dependencies:**
   ```bash
   cd apps/gradio-app
   poetry install
   ```

3. **Configure your API keys:**
   ```bash
   # Set environment variables (Windows PowerShell)
   $env:OPENAI_API_KEY = "your_openai_key_here"
   $env:ANTHROPIC_API_KEY = "your_anthropic_key_here"
   $env:GROQ_API_KEY = "your_groq_key_here"
   
   # Or create a .env file in the project root
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Run the application:**
   ```bash
   cd apps/gradio-app
   poetry run fitness-gradio
   ```

5. **Open your browser to `http://localhost:7860`**

## 🏗️ Project Structure

This project uses a **monorepo structure** with a clean separation of concerns:

```
fitness-app/
├── shared/                    # 📦 Core business logic library
│   └── src/fitness_core/     # AI agents, models, services
├── apps/
│   └── gradio-app/           # 🎨 Web interface with voice support
├── tests/                    # 🧪 Test files
├── docs/                     # 📚 Documentation
├── app.py                    # � Hugging Face Spaces entry point
└── .github/workflows/        # 🔄 CI/CD pipelines
```

### Core Library (`fitness_core`)
- **agents/**: AI agent implementations with multi-provider support
- **services/**: Business logic (conversation management, streaming)
- **utils/**: Configuration, logging, and utilities

### Gradio App
- **ui/**: User interface components and handlers
- **Voice Support**: Groq Whisper integration for speech-to-text
- **Real-time Streaming**: Live AI response generation

## 🤖 Supported AI Models

### 🟢 OpenAI Models
- **GPT-4o**: Latest with vision capabilities
- **GPT-4o-mini**: Fast, capable, cost-effective ⭐ *Default*
- **GPT-4 Turbo**: Large context window
- **GPT-3.5 Turbo**: Most economical
- **o1/o3 models**: Advanced reasoning

### 🔵 Anthropic Models  
- **Claude-3.5 Sonnet**: Excellent reasoning and analysis
- **Claude-3.5 Haiku**: Fast and responsive
- **Claude-3 Haiku**: Most cost-effective
- **Claude-4 models**: Premium capabilities

### 🚀 Groq Models (Ultra-Fast)
- **Llama-3.3-70b**: Excellent for complex fitness plans
- **Mixtral-8x7b**: Great for structured output
- **Whisper models**: Speech-to-text transcription

## 🎤 Voice Input

The app supports voice input using Groq's Whisper API:
- Click the microphone button in the chat input
- Speak your fitness questions naturally
- Automatic transcription with high accuracy
- See [VOICE_SETUP.md](apps/gradio-app/VOICE_SETUP.md) for setup details
- 🔧 **Extensible**: Easy to add new interfaces

## 🛠️ Development

### Project Structure Benefits
- **Shared Logic**: AI agents and business logic in one place
- **Independent Apps**: Each interface can be developed separately
- **Easy Testing**: Test core logic once, UI components separately
- **Technology Flexibility**: Add FastAPI, React, CLI, mobile apps easily

### Adding New Applications

Want to add a FastAPI backend or React frontend? See the [Developer Guide](docs/DEVELOPER_GUIDE.md) for detailed instructions.

Example for FastAPI:
```bash
mkdir -p apps/api/src/fitness_api
cd apps/api
# Create pyproject.toml with fitness-core dependency
poetry install
# Build your FastAPI app using shared fitness_core library
```

### Running Tests
```bash
# Test shared core
cd shared && poetry run pytest

# Test Gradio app  
cd apps/gradio-app && poetry run pytest
```

## 🎯 Usage Examples

### Web Interface
1. Open http://localhost:7860
2. Select your preferred AI model
3. Chat naturally: *"Create a beginner workout plan for weight loss"*
4. Get personalized fitness plans with structured workout and meal plans

### Programmatic Usage
```python
from fitness_core import FitnessAgent

# Create agent with your preferred model
agent = FitnessAgent("gpt-4o-mini")

# Get fitness advice
response = agent.run("I want to build muscle, I'm a beginner")
print(response)
```

## 🔧 Configuration

All configuration is handled through environment variables:

```bash
# API Keys (at least one required)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Model Selection
AI_MODEL=gpt-4o-mini  # Default model to use

# Server Configuration  
SERVER_PORT=7860      # Gradio server port
DEBUG=false           # Debug mode

# Logging
LOG_LEVEL=INFO        # DEBUG, INFO, WARNING, ERROR
LOG_FILE=app.log      # Optional log file
```

## 🚀 Deployment

### Docker (Coming Soon)
```bash
docker-compose up
```

### Manual Deployment
Each app can be deployed independently:

```bash
# Deploy Gradio app
cd apps/gradio-app
poetry build
# Deploy the built package
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes in the appropriate app or shared library
4. Add tests for new functionality
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Developer Guide](docs/DEVELOPER_GUIDE.md) - How to extend the app
- 🤖 [Model Guide](docs/COMPLETE_MODEL_GUIDE.md) - AI model information
- 🏗️ [Architecture Guide](docs/REPOSITORY_GUIDE.md) - Project structure details

## 🎉 Acknowledgments

- Built with [OpenAI Agents](https://github.com/openai/openai-agents) library
- UI powered by [Gradio](https://gradio.app/)
- Model support via [LiteLLM](https://github.com/BerriAI/litellm)
