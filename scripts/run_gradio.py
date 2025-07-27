"""
Run the Gradio app from the project root.
"""
import subprocess
import sys
from pathlib import Path

def run_gradio():
    """Run the Gradio application"""
    gradio_dir = Path(__file__).parent.parent / "apps" / "gradio-app"
    
    print("🎨 Starting Fitness Gradio app...")
    print(f"📂 Working directory: {gradio_dir}")
    
    try:
        # Change to gradio app directory and run with poetry
        result = subprocess.run([
            "poetry", "run", "fitness-gradio"
        ], cwd=gradio_dir, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Gradio app: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Poetry not found. Make sure Poetry is installed and in PATH.")
        print("   Run 'scripts/setup.bat' first to set up the environment.")
        sys.exit(1)

if __name__ == "__main__":
    run_gradio()
