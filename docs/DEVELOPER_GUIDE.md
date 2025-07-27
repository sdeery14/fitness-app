# Fitness App - Developer Guide

## Project Structure

This project uses a monorepo structure to support multiple frontend applications while sharing core business logic.

```
fitness-app/
├── shared/                    # Shared core library
│   ├── src/fitness_core/     # Core business logic
│   └── pyproject.toml        # Core dependencies
├── apps/
│   └── gradio-app/           # Gradio web interface
│       ├── src/fitness_gradio/
│       └── pyproject.toml    # Gradio-specific deps
├── scripts/                  # Setup and run scripts
├── tests/                    # Test files organized by component
└── docs/                     # Documentation
```

## Adding a New Application

To add a new interface (e.g., FastAPI backend, CLI tool, mobile app), follow these steps:

### 1. Create App Directory Structure

```bash
mkdir -p apps/your-app-name/src/your_app_name
cd apps/your-app-name
```

### 2. Create pyproject.toml

```toml
[tool.poetry]
name = "your-app-name"
version = "0.1.0"
description = "Description of your app"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
packages = [{include = "your_app_name", from = "src"}]

[tool.poetry.dependencies]
python = "^3.12"
fitness-core = {path = "../../shared", develop = true}
# Add your app-specific dependencies here
fastapi = "^0.104.0"  # Example for FastAPI
uvicorn = "^0.24.0"   # Example for FastAPI

[tool.poetry.scripts]
your-app = "your_app_name.main:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 3. Create App Structure

```bash
# Create main package
touch src/your_app_name/__init__.py
touch src/your_app_name/main.py

# Add app-specific modules
mkdir src/your_app_name/routers    # For FastAPI
mkdir src/your_app_name/middleware # For FastAPI
mkdir src/your_app_name/schemas    # For FastAPI
# OR
mkdir src/your_app_name/commands   # For CLI
mkdir src/your_app_name/interface  # For CLI
```

### 4. Example FastAPI App

**`src/your_app_name/main.py`:**
```python
"""
FastAPI backend for fitness assistant.
"""
import sys
from pathlib import Path

# Add shared library to path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "src"
sys.path.insert(0, str(shared_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fitness_core import FitnessAgent, ConversationManager, Config, setup_logging

# Configure logging
setup_logging(level=Config.LOG_LEVEL)

app = FastAPI(
    title="Fitness AI API",
    description="FastAPI backend for fitness assistant",
    version="0.1.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Fitness AI API"}

@app.post("/api/v1/chat")
async def chat(message: str):
    agent = FitnessAgent()
    conversation = ConversationManager()
    conversation.add_user_message(message)
    
    # Process with agent...
    return {"response": "AI response here"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
```

### 5. Example CLI App

**`src/your_app_name/main.py`:**
```python
"""
CLI interface for fitness assistant.
"""
import sys
from pathlib import Path
import click

# Add shared library to path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared" / "src"
sys.path.insert(0, str(shared_path))

from fitness_core import FitnessAgent, setup_logging

@click.group()
def cli():
    """Fitness AI Assistant CLI"""
    setup_logging(level="INFO")

@cli.command()
@click.option("--message", "-m", help="Message to send to the AI")
@click.option("--model", "-M", help="AI model to use")
def chat(message, model):
    """Chat with the fitness AI assistant"""
    agent = FitnessAgent(model_name=model)
    response = agent.run(message)
    click.echo(response)

@cli.command()
def models():
    """List available AI models"""
    models = FitnessAgent.list_supported_models()
    for name, identifier in models.items():
        click.echo(f"{name}: {identifier}")

def main():
    cli()

if __name__ == "__main__":
    main()
```

### 6. Install and Test

```bash
# Install dependencies
poetry install

# Test your app
poetry run your-app

# Or if it's a server
poetry run uvicorn your_app_name.main:app --reload
```

### 7. Update Setup Scripts

Add your app to the setup scripts:

**`scripts/setup.bat`:**
```batch
REM Add after Gradio app setup
echo 🚀 Setting up Your App...
cd apps\your-app-name
poetry install
cd ..\..
```

### 8. Create App-Specific Run Script

**`scripts/run_your_app.py`:**
```python
import subprocess
import sys
from pathlib import Path

def run_your_app():
    app_dir = Path(__file__).parent.parent / "apps" / "your-app-name"
    
    print("🚀 Starting Your App...")
    
    try:
        subprocess.run([
            "poetry", "run", "your-app"
        ], cwd=app_dir, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_your_app()
```

## Key Benefits

1. **Shared Logic**: All apps use the same AI agents and business logic
2. **Independent Deployment**: Each app can be deployed separately  
3. **Technology Flexibility**: Use any framework (FastAPI, Flask, Django, etc.)
4. **Isolated Dependencies**: Each app only includes what it needs
5. **Easy Testing**: Test shared logic once, test UI separately

## Common Patterns

### Accessing Shared Components

```python
from fitness_core import FitnessAgent, ConversationManager
from fitness_core.services import AgentRunner, ResponseFormatter
from fitness_core.utils import Config, get_logger
```

### Error Handling

```python
from fitness_core.services.exceptions import AgentExecutionError

try:
    agent = FitnessAgent()
    result = agent.run(message)
except AgentExecutionError as e:
    logger.error(f"Agent failed: {e}")
```

### Configuration

All apps inherit from the shared `Config` class:

```python
from fitness_core.utils import Config

# Access configuration
api_key = Config.OPENAI_API_KEY
port = Config.SERVER_PORT
debug_mode = Config.DEBUG
```
