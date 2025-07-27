# Fitness Gradio App

Web interface for the Fitness AI Assistant using Gradio with voice input support.

## Features

- Interactive chat interface with multimodal input
- **Voice input** via microphone button (powered by Groq Whisper)
- Multi-provider model support (Groq, Anthropic, OpenAI)
- Real-time streaming responses
- Fitness plan generation
- Mobile-friendly design

## Quick Start

```bash
# Set your API key for voice functionality
$env:GROQ_API_KEY = "your-groq-api-key"

# Install and run
poetry install
poetry run python -m fitness_gradio.main
```

## Voice Setup

1. Get a [Groq API key](https://console.groq.com/keys)
2. Set `GROQ_API_KEY` environment variable
3. Click the microphone button in the chat interface
4. Allow browser microphone access when prompted

See [VOICE_SETUP.md](VOICE_SETUP.md) for detailed setup instructions.

## Configuration

Optional environment variables:
```bash
GROQ_API_KEY=your-groq-key          # Required for voice input
AI_MODEL=llama-3.3-70b-versatile    # Optional model selection
ANTHROPIC_API_KEY=your-anthropic-key # For Claude models
OPENAI_API_KEY=your-openai-key       # For GPT models
```
