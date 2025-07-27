# Voice Input Setup Guide

## Overview
The fitness app now supports voice input through the microphone feature. This allows you to speak your fitness questions and get responses without typing.

## Prerequisites
- Groq API key (for Whisper speech-to-text - faster and more cost-effective than OpenAI)
- Microphone access in your browser
- Modern web browser with microphone support

## Setup Instructions

### 1. Set up Groq API Key
You need to set your Groq API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY = "your-groq-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GROQ_API_KEY=your-groq-api-key-here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

### 2. Get a Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to [API Keys](https://console.groq.com/keys)
4. Create a new API key
5. Copy the key and set it as an environment variable

### 3. Start the Application
Run the fitness app as usual:
```bash
poetry run python -m fitness_gradio.main
```

### 4. Using Voice Input

1. **Click the circular microphone button** inside the chat input box
2. **Allow microphone access** when prompted by your browser
3. **Speak clearly** into your microphone
4. **Click stop recording** when finished
5. The app will automatically transcribe your speech and send it as a message

## Features

- **Automatic speech-to-text** conversion using Groq Whisper models
- **Ultra-fast transcription** with Groq's optimized infrastructure
- **Cost-effective** pricing (much cheaper than OpenAI)
- **High accuracy** with `whisper-large-v3-turbo` model
- **Voice message indicators** in the chat (🎤 prefix)
- **Error handling** for network issues or API problems

## Models Used

- **whisper-large-v3-turbo**: Best price/performance ratio at $0.04 per minute
- **Multilingual support**: Works with multiple languages (configured for English by default)
- **Fast processing**: Optimized for speed with minimal latency

## Troubleshooting

### "No microphone" Error
- **Check browser permissions**: Make sure your browser has microphone access
- **Check system settings**: Ensure your microphone is working and not muted
- **Try a different browser**: Some browsers have better microphone support

### "Please set GROQ_API_KEY" Message
- Make sure you've set the environment variable correctly
- Restart the application after setting the API key
- Check that your API key is valid and active
- Verify you have credits in your Groq account

### Transcription Errors
- **Speak clearly** and at a normal pace
- **Reduce background noise** for better accuracy
- **Try shorter messages** if having issues with longer recordings

### Audio Processing Errors
- Make sure you have a working internet connection
- Check that the scipy library is installed (`poetry install`)
- Restart the application if audio processing stops working

## Technical Details

The voice input system uses:
- **Gradio Audio component** for recording
- **Groq Whisper API** for speech-to-text
- **scipy** for audio file processing
- **Custom audio handlers** for seamless integration

## Cost Considerations

Groq Whisper API pricing:
- **whisper-large-v3-turbo**: $0.04 per minute (very affordable!)
- **whisper-large-v3**: $0.111 per minute (higher accuracy)
- Much more cost-effective than OpenAI's Whisper API
- Monitor your Groq usage dashboard if concerned about costs

## Privacy

- Audio is sent to Groq for transcription
- No audio data is stored locally after transcription
- Follow your organization's data privacy guidelines
- Consider using local Whisper models for sensitive environments

## Why Groq?

- **🚀 Faster**: Groq's inference speed is significantly faster than OpenAI
- **💰 Cheaper**: More cost-effective pricing
- **🔧 Reliable**: High uptime and consistent performance
- **🌐 Compatible**: OpenAI-compatible API for easy integration
