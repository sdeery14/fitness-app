# Fitness Gradio App

Web interface for the Fitness AI Assistant using Gradio with voice input and text-to-speech support.

## Features

- Interactive chat interface with multimodal input
- **Voice input** via microphone button (powered by Groq Whisper)
- **Text-to-Speech output** with 19 English and 4 Arabic voices (powered by Groq PlayAI TTS)
- Multi-provider model support (Groq, Anthropic, OpenAI)
- Real-time streaming responses
- Fitness plan generation
- Mobile-friendly design

## Quick Start

```bash
# Set your API key for voice functionality and TTS
$env:GROQ_API_KEY = "your-groq-api-key"

# Install and run
poetry install
poetry run python -m fitness_gradio.main
```

## Voice & TTS Setup

1. Get a [Groq API key](https://console.groq.com/keys)
2. Set `GROQ_API_KEY` environment variable
3. **Voice Input**: Click the microphone button in the chat interface
4. **Text-to-Speech**: Enable the "🔊 Enable Text-to-Speech" checkbox
5. Allow browser microphone access when prompted (for voice input)

### Available TTS Voices

**English (playai-tts)**: 19 voices including Celeste-PlayAI (default), Fritz-PlayAI, Arista-PlayAI, Atlas-PlayAI, Basil-PlayAI, Briggs-PlayAI, Calum-PlayAI, Cheyenne-PlayAI, and more.

**Arabic (playai-tts-arabic)**: 4 voices including Amira-PlayAI (default), Ahmad-PlayAI, Khalid-PlayAI, Nasser-PlayAI.

See [VOICE_SETUP.md](VOICE_SETUP.md) for detailed setup instructions.

## Configuration

Optional environment variables:
```bash
GROQ_API_KEY=your-groq-key          # Required for voice input
AI_MODEL=llama-3.3-70b-versatile    # Optional model selection
ANTHROPIC_API_KEY=your-anthropic-key # For Claude models
OPENAI_API_KEY=your-openai-key       # For GPT models
```
