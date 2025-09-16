"""
Fitness Agent - Core AI agent for fitness planning and training.
"""

try:
    from .agents import FitnessAgent
    from .services import FitnessAgentRunner
    from .models import FitnessPlan, TrainingPlan, MealPlan, AgentConfig
    from .memory import UserSession, SessionManager
    from .utils import Config

    __all__ = [
        'FitnessAgent',
        'FitnessAgentRunner', 
        'FitnessPlan',
        'TrainingPlan',
        'MealPlan',
        'AgentConfig',
        'UserSession',
        'SessionManager',
        'Config'
    ]
except ImportError as e:
    # Graceful degradation if imports fail
    print(f"Warning: Some fitness_agent imports failed: {e}")
    __all__ = []
