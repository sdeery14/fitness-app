"""
Hugging Face Spaces entry point for Fitness AI Assistant
"""
import sys
import os
from pathlib import Path

# Add the necessary paths
current_dir = Path(__file__).parent

# Add shared library to path
shared_path = current_dir / "shared" / "src"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Add gradio app to path  
gradio_app_path = current_dir / "apps" / "gradio-app" / "src"
if str(gradio_app_path) not in sys.path:
    sys.path.insert(0, str(gradio_app_path))

# Add fitness_agent to path
fitness_agent_path = current_dir / "fitness_agent"
if str(fitness_agent_path) not in sys.path:
    sys.path.insert(0, str(fitness_agent_path))

print("🚀 Starting Fitness AI Assistant...")
print(f"📂 Working directory: {current_dir}")
print(f"🔍 Python paths added:")
print(f"   - {shared_path}")
print(f"   - {gradio_app_path}")
print(f"   - {fitness_agent_path}")

try:
    print("📦 Testing core imports...")
    import gradio as gr
    print("✓ Gradio imported successfully")
    
    # Try to import our modules step by step
    print("📦 Testing fitness_core imports...")
    from fitness_core import setup_logging, Config, get_logger
    print("✓ fitness_core base imports successful")
    
    print("📦 Testing fitness_gradio imports...")
    try:
        import scipy
        print("✓ scipy imported successfully")
    except ImportError as e:
        print(f"⚠️ scipy not available - audio processing will be limited: {e}")
    
    try:
        import groq
        print("✓ groq imported successfully")
    except ImportError as e:
        print(f"⚠️ groq not available - voice transcription will be limited: {e}")
    
    from fitness_gradio.ui import create_fitness_app
    print("✓ fitness_gradio imports successful")
    
    # Configure logging
    setup_logging(level=Config.LOG_LEVEL, log_file=Config.LOG_FILE)
    logger = get_logger(__name__)
    
    print("🎨 Creating Gradio app...")
    app = create_fitness_app()
    print("✅ Successfully created full fitness app!")
    
except Exception as e:
    print(f"⚠️  Import error: {e}")
    print("🔄 Creating fallback Gradio interface...")
    
    import gradio as gr
    
    def respond(message, history):
        return (f"🏋️ Hello! I'm the Fitness AI Assistant. I'm currently in fallback mode due to missing dependencies.\n\n"
                f"You said: {message}\n\n"
                f"Please ensure all required dependencies are installed:\n"
                f"- openai-agents[litellm]\n"
                f"- python-dotenv\n"
                f"- pydantic\n\n"
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

if __name__ == "__main__":
    print("🚀 Launching Fitness AI Assistant...")
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
