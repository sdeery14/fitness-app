"""
UI components and handlers for the Gradio fitness app.
"""
from .app import FitnessAppUI, create_fitness_app
from .components import UIComponents
from .handlers import UIHandlers

__all__ = [
    'FitnessAppUI',
    'create_fitness_app', 
    'UIComponents',
    'UIHandlers'
]
