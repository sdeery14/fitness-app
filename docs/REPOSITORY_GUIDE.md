# Fitness App - Repository Structure

## 📁 Core Architecture

### Monorepo Structure
- **`shared/`** - Core fitness logic and utilities
- **`apps/gradio-app/`** - Gradio web interface with voice input
- **`docs/`** - Documentation and guides
- **`tests/`** - Test files organized by component

### Main Components
- **`apps/gradio-app/src/fitness_gradio/main.py`** - Gradio application entry point
- **`apps/gradio-app/src/fitness_gradio/ui/`** - UI components and handlers
- **`shared/src/fitness_core/`** - Shared business logic and agents

### Documentation
- **`GROQ_INTEGRATION.md`** - Groq models setup and usage (including Whisper for voice)
- **`DEVELOPER_GUIDE.md`** - Architecture guide for adding new applications
- **`VOICE_SETUP.md`** - Voice input setup and troubleshooting

### Configuration
- **`shared/pyproject.toml`** - Core dependencies and utilities
- **`apps/gradio-app/pyproject.toml`** - Gradio-specific dependencies

## 🚀 Quick Start

1. **Install dependencies**: `cd apps/gradio-app && poetry install`
2. **Set up environment**: Set `GROQ_API_KEY` environment variable
3. **Run the app**: `poetry run python -m fitness_gradio.main`
4. **Use voice input**: Click the microphone button in the chat interface

## 📚 Need Help?

- **Model questions**: See `COMPLETE_MODEL_GUIDE.md`
- **Usage examples**: Run `examples.py`

---

*Clean, focused, and ready to use! 🎯*
