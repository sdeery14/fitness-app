# AI Models Guide

## Recommended Models (Fast & Free)

### Groq Models
- **llama-3.3-70b-versatile**: Best for complex plans
- **llama-3.1-8b-instant**: Fastest responses
- **gemma2-9b-it**: Good balance

### Other Models
- **gpt-4o-mini**: OpenAI's efficient model
- **claude-3.5-haiku**: Anthropic's fast model

## Setup

Set your API key:
```bash
# For Groq (recommended)
$env:GROQ_API_KEY = "your_groq_key"

# For OpenAI
$env:OPENAI_API_KEY = "your_openai_key"

# For Anthropic
$env:ANTHROPIC_API_KEY = "your_anthropic_key"
```

## Voice Input

Voice input uses Groq's Whisper models for speech-to-text. Requires GROQ_API_KEY.
