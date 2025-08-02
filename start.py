"""
Quick start script for the Fitness AI Assistant.
Run this from the project root to start the application.
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Start the fitness app using the run_gradio script."""
    script_path = Path(__file__).parent / "scripts" / "run_gradio.py"
    
    print("🏋️ Starting Fitness AI Assistant...")
    print("📍 Use this script to quickly start the app from the project root")
    print()
    
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
