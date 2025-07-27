"""
Hugging Face Spaces entry point - redirects to fitness_agent/app.py
"""
import sys
from pathlib import Path

# Add the fitness_agent directory to the path
current_dir = Path(__file__).parent
fitness_agent_dir = current_dir / "fitness_agent"
sys.path.insert(0, str(fitness_agent_dir))

# Import and run the main app
from fitness_agent.app import app

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
