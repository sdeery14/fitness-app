# Development Guide

## Project Structure

```
fitness-app/
├── shared/src/fitness_core/   # Core AI agents and business logic
├── apps/gradio-app/          # Web interface with voice input
├── docs/                     # Documentation
└── app.py                    # Hugging Face entry point
```

## Quick Development

1. **Run the app**: `python start.py`
2. **Core logic**: Edit `shared/src/fitness_core/`
3. **UI**: Edit `apps/gradio-app/src/fitness_gradio/ui/`

## Adding Features

- **Agent tools**: Add to `agents/tools.py`
- **UI components**: Add to `ui/components.py` 
- **Models**: Add to `agents/structured_output_models.py`

## Code Style

- Use type hints
- Add docstrings for public functions
- Keep functions small and focused
