# 🏋️ Fitness AI Assistant

An AI-powered fitness companion that provides personalized workout plans, meal planning, and fitness guidance using state-of-the-art language models.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Poetry (for dependency management)
- OpenAI API Key and/or Anthropic API Key

### Setup

1. **Clone and setup the environment:**
   ```bash
   git clone <your-repo-url>
   cd fitness-app
   
   # Windows
   scripts\setup.bat
   
   # Linux/Mac  
   chmod +x scripts/setup.sh
   scripts/setup.sh
   ```

2. **Configure your API keys:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your API keys
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

3. **Run the Gradio web interface:**
   ```bash
   # Option 1: Using the run script
   python scripts/run_gradio.py
   
   # Option 2: Using Poetry directly
   cd apps/gradio-app
   poetry run fitness-gradio
   ```

4. **Open your browser to `http://localhost:7860`**

## 🏗️ Architecture

This project uses a **monorepo structure** that supports multiple frontend applications while sharing core business logic:

```
fitness-app/
├── shared/                    # 📦 Core business logic library
│   └── src/fitness_core/     # AI agents, models, services
├── apps/
│   └── gradio-app/           # 🎨 Web interface (Gradio)
├── scripts/                  # 🔧 Setup and run scripts
├── tests/                    # 🧪 Test files
└── docs/                     # 📚 Documentation
```

### Shared Core Library (`fitness_core`)
- **agents/**: AI agent implementations (OpenAI + Anthropic support)
- **services/**: Business logic (conversation management, streaming)
- **utils/**: Configuration, logging, utilities

### Apps
- **gradio-app/**: Interactive web interface with real-time chat

## 🤖 Supported AI Models

### OpenAI Models
- **GPT-4o**: Latest with vision and advanced capabilities
- **GPT-4o-mini**: Fast, capable, cost-effective ⭐ *Recommended*
- **GPT-4 Turbo**: Large context window
- **GPT-3.5 Turbo**: Cost-effective option
- **o1-preview/o1-mini**: Advanced reasoning models

### Anthropic Models  
- **Claude-3.5 Haiku**: Fast and responsive ⭐ *Recommended*
- **Claude-3.5 Sonnet**: Excellent balance of intelligence and speed
- **Claude-3 Haiku**: Most cost-effective
- **Claude-4 models**: Premium tier (when available)

## ✨ Features

- 🤖 **Multi-Provider AI Support**: OpenAI and Anthropic models
- 💬 **Real-time Streaming**: Live response streaming
- 🏋️ **Personalized Plans**: Custom workout and meal plans
- 📱 **Mobile-Friendly**: Responsive web interface
- 🎨 **Beautiful UI**: Modern Gradio interface
- ⚡ **Fast Setup**: One-command installation
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
