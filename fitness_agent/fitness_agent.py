"""
Fitness Agent - Main application entry point for Hugging Face Spaces
"""
import sys
import os
from pathlib import Path

# Add the necessary paths
current_dir = Path(__file__).parent
root_dir = current_dir.parent

# Add shared library to path
shared_path = root_dir / "shared" / "src"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Add gradio app to path
gradio_app_path = root_dir / "apps" / "gradio-app" / "src"
if str(gradio_app_path) not in sys.path:
    sys.path.insert(0, str(gradio_app_path))

try:
    from fitness_core import setup_logging, Config, get_logger
    from fitness_core.agents.base import BaseAgent
    from fitness_core.agents.models import AgentConfig
    from fitness_core.services.agent_runner import AgentRunner
    
    # Configure logging
    setup_logging(level=Config.LOG_LEVEL, log_file=Config.LOG_FILE)
    logger = get_logger(__name__)
    
    class FitnessAgent(BaseAgent):
        """Main Fitness Agent class for backwards compatibility."""
        
        def __init__(self, config: AgentConfig = None):
            """Initialize the fitness agent."""
            if config is None:
                # Create default config
                config = AgentConfig(
                    name="fitness_agent",
                    description="AI-powered fitness and nutrition assistant",
                    model_provider="openai",
                    model_name="gpt-4",
                    temperature=0.7
                )
            super().__init__(config)
            self.runner = AgentRunner()
        
        async def process_message(self, message: str, context: dict = None) -> str:
            """Process a user message and return response."""
            try:
                response = await self.runner.run_agent(
                    message=message,
                    context=context or {}
                )
                return response
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                return f"I apologize, but I encountered an error: {str(e)}"
        
        def get_capabilities(self) -> list:
            """Get agent capabilities."""
            return [
                "Fitness program design",
                "Nutrition advice", 
                "Workout planning",
                "Health and wellness guidance"
            ]

except ImportError as e:
    logger = None
    print(f"Warning: Could not import fitness_core modules: {e}")
    
    # Fallback FitnessAgent for basic functionality
    class FitnessAgent:
        """Fallback Fitness Agent when core modules aren't available."""
        
        def __init__(self, config=None):
            self.config = config
        
        async def process_message(self, message: str, context: dict = None) -> str:
            """Basic message processing fallback."""
            return "I'm a fitness AI assistant. Please ensure all dependencies are properly installed."
        
        def get_capabilities(self) -> list:
            """Get basic capabilities."""
            return ["Basic fitness assistance"]
