#!/usr/bin/env python3
"""
Debug script to test audio transcription functionality
"""
import os
import sys
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fitness_gradio.ui.handlers import UIHandlers

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_audio_message_processing():
    """Test the add_message_with_audio function"""
    
    # Mock message with audio file (you'd need to provide a real audio file path to test)
    test_audio_file = "test_audio.wav"  # Replace with actual audio file path
    
    # Test case 1: Audio only message
    mock_audio_message = {
        "files": [test_audio_file],
        "text": ""
    }
    
    # Test case 2: Text only message
    mock_text_message = {
        "files": [],
        "text": "Hello, this is a test message"
    }
    
    # Test case 3: Combined audio and text
    mock_combined_message = {
        "files": [test_audio_file],
        "text": "Additional text content"
    }
    
    initial_history = []
    
    print("Testing audio message processing...")
    
    # Test text message
    print("\n=== Testing text-only message ===")
    try:
        history, input_state = UIHandlers.add_message_with_audio(initial_history.copy(), mock_text_message)
        print(f"History after text message: {history}")
        print(f"Input state: {input_state}")
    except Exception as e:
        print(f"Error with text message: {e}")
    
    # Test audio message (only if audio file exists)
    if os.path.exists(test_audio_file):
        print("\n=== Testing audio-only message ===")
        try:
            history, input_state = UIHandlers.add_message_with_audio(initial_history.copy(), mock_audio_message)
            print(f"History after audio message: {history}")
            print(f"Input state: {input_state}")
        except Exception as e:
            print(f"Error with audio message: {e}")
    else:
        print(f"\n=== Skipping audio test (file {test_audio_file} not found) ===")
    
    # Test is_audio_file function
    print("\n=== Testing audio file detection ===")
    test_files = [
        "test.wav",
        "test.mp3", 
        "test.m4a",
        "test.txt",
        "test.jpg",
        "test.webm"
    ]
    
    for test_file in test_files:
        is_audio = UIHandlers.is_audio_file(test_file)
        print(f"{test_file}: {'Audio' if is_audio else 'Not audio'}")

if __name__ == "__main__":
    test_audio_message_processing()
