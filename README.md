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

Click the microphone button to speak your fitness questions. Requires GROQ_API_KEY.
## 🛠️ Development

Edit `shared/src/fitness_core/` for core logic, `apps/gradio-app/src/` for UI.

Run: `python start.py`

## 🎯 Usage

1. Run the app: `python start.py`
2. Open http://localhost:7860
3. Select an AI model
4. Chat: *"Create a beginner workout plan for weight loss"*

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

- 📖 [Development Guide](docs/DEVELOPMENT.md) - How to extend the app
- 🤖 [AI Models Guide](docs/MODELS.md) - Model setup and configuration

## 🎉 Acknowledgments

- Built with [OpenAI Agents](https://github.com/openai/openai-agents) library
- UI powered by [Gradio](https://gradio.app/)
- Model support via [LiteLLM](https://github.com/BerriAI/litellm)
