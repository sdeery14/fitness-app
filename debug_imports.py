#!/usr/bin/env python3
"""
Simple test script to debug imports
"""
import sys
from pathlib import Path

# Add paths
current_dir = Path(__file__).parent
shared_path = current_dir / "shared" / "src"
gradio_app_path = current_dir / "apps" / "gradio-app" / "src"

sys.path.insert(0, str(shared_path))
sys.path.insert(0, str(gradio_app_path))

print(f"Python path includes:")
for p in sys.path[:5]:  # Show first 5 paths
    print(f"  - {p}")

try:
    print("Testing basic imports...")
    import gradio as gr
    print("✓ Gradio import successful")
except Exception as e:
    print(f"❌ Gradio import failed: {e}")

try:
    print("Testing agents import...")
    from agents import Agent
    print("✓ agents.Agent import successful")
except Exception as e:
    print(f"❌ agents.Agent import failed: {e}")

try:
    print("Testing fitness_core imports...")
    from fitness_core.agents.base import FitnessAgent
    print("✓ fitness_core.agents.base.FitnessAgent import successful")
except Exception as e:
    print(f"❌ fitness_core.agents.base.FitnessAgent import failed: {e}")

try:
    print("Testing fitness_gradio imports...")
    from fitness_gradio.ui import create_fitness_app
    print("✓ fitness_gradio.ui.create_fitness_app import successful")
except Exception as e:
    print(f"❌ fitness_gradio.ui.create_fitness_app import failed: {e}")

print("Import test completed.")
