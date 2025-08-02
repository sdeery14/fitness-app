# Development Guidelines

## Code Organization

### Structure
```
fitness-app/
├── apps/gradio-app/          # Gradio UI application
├── shared/                   # Shared core fitness logic
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
├── app.py                    # Hugging Face entry point
└── start.py                  # Quick start script
```

### Key Principles

1. **Unified Chat System**: Both voice and text use the same FitnessAgent and chatbot component
2. **Shared State**: Conversation history and fitness plans are shared between voice and text modes
3. **Modular UI**: Components are separated for maintainability
4. **Clean Separation**: Core logic (shared/) is separate from UI (apps/)

## Development Workflow

### Making Changes

1. **Core Logic**: Edit files in `shared/src/fitness_core/`
2. **UI Components**: Edit files in `apps/gradio-app/src/fitness_gradio/ui/`
3. **Test Changes**: Run `python start.py` from project root

### Adding Features

1. **Agent Tools**: Add to `shared/src/fitness_core/agents/tools.py`
2. **UI Components**: Add to `apps/gradio-app/src/fitness_gradio/ui/components.py`
3. **Event Handlers**: Add to `apps/gradio-app/src/fitness_gradio/ui/handlers.py`

### Code Style

- Use type hints for all functions
- Add docstrings for public methods
- Follow PEP 8 naming conventions
- Keep functions focused and small

## Testing

- Test both voice and text input modes
- Verify fitness plans appear in both modes
- Check that conversation history transfers between modes
- Test different AI models

## Deployment

- Use `app.py` for Hugging Face Spaces
- Use `start.py` for local development
- Ensure environment variables are set correctly
