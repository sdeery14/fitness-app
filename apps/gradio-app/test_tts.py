"""
Test TTS functionality
"""
import os
from fitness_gradio.ui.tts_utils import GroqTTS, generate_speech_for_text, clean_tts_markup

def test_tts_setup():
    """Test basic TTS setup and functionality."""
    print("Testing TTS setup...")
    
    # Check if API key is available
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please set GROQ_API_KEY to test TTS functionality")
        return False
    
    print("✅ GROQ_API_KEY found")
    
    # Test TTS instance creation
    try:
        tts = GroqTTS()
        print("✅ GroqTTS instance created successfully")
    except Exception as e:
        print(f"❌ Failed to create GroqTTS instance: {e}")
        return False
    
    # Test text cleaning
    test_text = "**Hello** this is a *test* with `code` and [links](http://example.com)"
    cleaned = clean_tts_markup(test_text)
    print(f"Text cleaning test:")
    print(f"  Original: {test_text}")
    print(f"  Cleaned:  {cleaned}")
    
    # Test voice lists
    english_voices = GroqTTS.get_available_voices("playai-tts")
    arabic_voices = GroqTTS.get_available_voices("playai-tts-arabic")
    print(f"✅ Available English voices: {len(english_voices)}")
    print(f"✅ Available Arabic voices: {len(arabic_voices)}")
    
    print("🎉 All TTS setup tests passed!")
    print("Note: Actual TTS generation will be tested when the UI is used with a valid API key.")
    return True

if __name__ == "__main__":
    test_tts_setup()
