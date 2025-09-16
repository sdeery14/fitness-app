"""
Fitness AI Assistant - Main Entry Point
"""
import sys
import os
from pathlib import Path

# Add the current directory to Python path (for local imports)
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

print("🚀 Starting Fitness AI Assistant...")
print(f"📂 Working directory: {current_dir}")

try:
    # Import and run the Gradio app
    from gradio_app import create_app
    from fitness_agent.utils import Config, setup_logging
    
    # Set up logging
    setup_logging()
    
    # Create and launch the app
    app = create_app()
    
    print("✅ Fitness AI Assistant ready!")
    print(f"🌐 Server will start on: http://{Config.SERVER_NAME}:{Config.SERVER_PORT}")
    
    # Launch with configuration
    app.launch(**Config.get_gradio_config())
    
except Exception as e:
    print(f"❌ Error starting Fitness AI Assistant: {str(e)}")
    print("📋 Make sure you have installed the required dependencies:")
    print("   pip install -r requirements.txt")
    
    # Fallback simple interface
    print("🔄 Creating fallback interface...")
    import gradio as gr
    
    def respond(message, history):
        return (f"🏋️ Hello! I'm the Fitness AI Assistant. I'm currently in fallback mode due to missing dependencies.\n\n"
                f"You said: {message}\n\n"
                f"Please ensure all required dependencies are installed:\n"
                f"- openai-agents[litellm]\n"
                f"- python-dotenv\n"
                f"- pydantic\n"
                f"- gradio\n\n"
                f"Once properly configured, I can help with:\n"
                f"- Fitness program design\n"
                f"- Nutrition advice\n"
                f"- Workout planning\n"
                f"- Health and wellness guidance")
    
    app = gr.ChatInterface(
        respond,
        title="🏋️ Fitness AI Assistant",
        description="Your personal AI-powered fitness and nutrition coach (Fallback Mode)",
        examples=[
            "Create a beginner workout plan",
            "What should I eat after a workout?", 
            "How many calories should I eat per day?",
            "Design a 30-day fitness challenge"
        ]
    )
    
    print("✅ Created fallback interface")
    app.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    pass  # Main logic is already executed above
