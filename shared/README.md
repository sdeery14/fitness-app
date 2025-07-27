# Fitness Core Library

Shared business logic, AI agents, and utilities for the Fitness App ecosystem.

## Components

- **agents/**: AI agent implementations and model management
- **models/**: Pydantic data models 
- **services/**: Core business logic and conversation management
- **utils/**: Configuration, logging, and utility functions

## Usage

This library is designed to be imported by various frontend applications (Gradio, FastAPI, CLI, etc.)

```python
from fitness_core.agents import FitnessAgent
from fitness_core.models import FitnessPlan
from fitness_core.services import ConversationManager
```
