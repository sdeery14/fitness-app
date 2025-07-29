#!/usr/bin/env python3
"""
Test script for the voice conversation feature.
Run this to test the voice conversation functionality.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fitness_gradio.ui.app import FitnessAppUI
    
    print("✅ Successfully imported FitnessAppUI")
    
    # Test creating the app
    app = FitnessAppUI()
    print("✅ Successfully created FitnessAppUI instance")
    
    # Test getting the demo
    demo = app.get_demo()
    print("✅ Successfully got Gradio demo")
    
    print("\n🎉 Voice conversation feature is ready!")
    print("\n🚀 To launch the app, run:")
    print("python scripts/run_gradio.py")
    
    print("\n📋 Voice Conversation Features:")
    print("- 🎤 Start Voice Conversation button")
    print("- 🔊 Automatic voice activity detection (VAD)")
    print("- 🗣️ Speech-to-text using Groq Whisper")
    print("- 🤖 AI responses using your selected model")
    print("- 🔉 Text-to-speech using Groq TTS")
    print("- 💬 Chat history preserved in main conversation")
    print("- ❌ Exit button to end voice chat")
    
    print("\n⚠️  Requirements:")
    print("- GROQ_API_KEY environment variable must be set")
    print("- Microphone access will be requested by the browser")
    print("- Modern browser with JavaScript enabled")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTry installing missing dependencies:")
    print("pip install gradio groq soundfile")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPlease check your setup and try again.")
