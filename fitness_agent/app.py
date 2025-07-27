"""
Main Gradio app entry point for Hugging Face Spaces
"""
import os
import sys
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

# Import required modules
import gradio as gr

try:
    # Try to import the main Gradio UI
    from fitness_gradio.ui import create_fitness_app
    from fitness_core import setup_logging, Config, get_logger
    
    # Configure logging
    setup_logging(level=Config.LOG_LEVEL, log_file=Config.LOG_FILE)
    logger = get_logger(__name__)
    
    # Create the main app
    app = create_fitness_app()
    
except ImportError as e:
    print(f"Warning: Could not import fitness modules: {e}")
    print("Creating fallback Gradio interface...")
    
    def respond(message, history):
        """Fallback response function."""
        return "I'm a fitness AI assistant. I'm currently loading my capabilities. Please try again in a moment, or ensure all dependencies are properly installed."
    
    # Create fallback interface
    app = gr.ChatInterface(
        respond,
        title="🏋️ Fitness AI Assistant",
        description="Your personal AI-powered fitness and nutrition coach. I can help with workout plans, nutrition advice, and health guidance.",
        examples=[
            "Create a beginner workout plan for me",
            "What should I eat for muscle gain?",
            "How can I lose weight safely?",
            "Design a 30-minute home workout"
        ],
        cache_examples=True,
        theme=gr.themes.Soft()
    )

# For Hugging Face Spaces
if __name__ == "__main__":
    # Launch the app
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
