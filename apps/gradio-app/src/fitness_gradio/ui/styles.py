"""
CSS styles and theming for the fitness app UI.
"""

# Main CSS for the Gradio interface
MAIN_CSS = """
.gradio-container {
    max-width: 1200px !important;
}

#chatbot {
    height: 600px;
}

/* Voice conversation specific styles */
#voice-status {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1)) !important;
    border: 2px solid rgba(16, 185, 129, 0.4) !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    text-align: center !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #065f46 !important;
    animation: pulse 2s infinite !important;
    backdrop-filter: blur(5px) !important;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

#voice-audio .record-button {
    background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3) !important;
    transition: all 0.3s ease !important;
}

#voice-audio .record-button:hover {
    background: linear-gradient(135deg, #b91c1c, #991b1b) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(220, 38, 38, 0.4) !important;
}

#voice-audio .stop-button {
    background: linear-gradient(135deg, #059669, #047857) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3) !important;
}

#voice-chatbot {
    height: 400px !important;
    border: 2px solid rgba(16, 185, 129, 0.3) !important;
    border-radius: 12px !important;
}

#voice-output {
    border: 2px solid rgba(79, 70, 229, 0.3) !important;
    border-radius: 12px !important;
}

.model-info {
    background: linear-gradient(135deg, rgba(55, 65, 81, 0.9), rgba(75, 85, 99, 0.7)) !important;
    color: #e5e7eb !important;
    padding: 16px !important;
    border-radius: 12px !important;
    border-left: 4px solid #10b981 !important;
    margin: 12px 0 !important;
    border: 1px solid rgba(75, 85, 99, 0.4) !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    backdrop-filter: blur(10px) !important;
}

.model-info p {
    color: #e5e7eb !important;
    margin: 8px 0 !important;
    line-height: 1.5 !important;
}

.model-info strong {
    color: #f9fafb !important;
    font-weight: 600 !important;
}

.model-info em {
    color: #d1d5db !important;
    font-style: italic;
}

.model-info code {
    background-color: rgba(31, 41, 55, 0.8) !important;
    color: #10b981 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
    font-size: 0.9em !important;
}

.model-dropdown {
    font-weight: bold;
}

/* TTS control styling */
.tts-checkbox {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1)) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 8px !important;
    padding: 8px !important;
    transition: all 0.3s ease !important;
}

.tts-checkbox:hover {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2)) !important;
    border-color: rgba(99, 102, 241, 0.5) !important;
}

.tts-active {
    animation: pulse-tts 2s infinite;
}

@keyframes pulse-tts {
    0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
    100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
}

/* Ensure all text in model-info respects dark theme */
.model-info * {
    color: inherit !important;
}

/* Fix for any remaining white background issues */
.model-info .prose {
    color: #e5e7eb !important;
}
"""

# Header markdown content
HEADER_MARKDOWN = """
# 🏋️‍♀️ Fitness AI Assistant
Your personal fitness companion for workout plans, meal planning, and fitness guidance!

💡 **Tips:**
- Be specific about your fitness goals
- Mention any physical limitations or preferences
- Ask for modifications if needed
- Choose your preferred AI model for different capabilities
"""

# Help content for the accordion
HELP_CONTENT = """
**What I can help you with:**
- Create personalized workout plans
- Design meal plans for your goals
- Provide fitness guidance and tips
- Suggest exercises for specific needs
- Help modify existing plans

**How to interact:**
- **💬 Type messages** in the text box
- **🎤 Record voice messages** using the circular microphone button (requires Groq API key)
- **� Enable Text-to-Speech** to hear AI responses spoken aloud (requires Groq API key)
- **🚀 Enable Real-time Streaming** for faster response display
- **�📎 Upload files** if needed for context

**To get the best results:**
- Tell me your fitness level (beginner, intermediate, advanced)
- Mention your goals (weight loss, muscle gain, general fitness)
- Include any equipment you have access to
- Let me know about any injuries or limitations

**Voice Input Setup:**
- Set your `GROQ_API_KEY` environment variable to enable voice transcription

**Text-to-Speech Setup:**
- Set your `GROQ_API_KEY` environment variable to enable audio generation
- Choose from 19 English voices or 4 Arabic voices
- Audio is automatically generated when TTS is enabled
- Responses are cleaned of markdown formatting for better speech quality
- Click the circular microphone icon in the input box and speak your message
- The system will convert your speech to text automatically using Groq's Whisper

**AI Model Selection:**
- **🔵 Anthropic Claude Models**: Excellent for detailed reasoning and analysis
  - Claude-4: Most capable (premium), Claude-3.7: Extended thinking
  - Claude-3.5: Balanced performance, Claude-3: Fast and cost-effective
- **🟢 OpenAI GPT Models**: Great for general tasks and familiar interface
  - GPT-4o: Latest with vision, GPT-4 Turbo: Large context window
  - GPT-3.5: Fast and economical, o1/o3: Advanced reasoning
- You can change models anytime - the conversation continues seamlessly
- Mix and match providers based on your preferences

**Conversation Management:**
- The assistant remembers our entire conversation
- You can refer back to previous plans or discussions
- Use the "Clear Conversation" button to start fresh
- Each conversation maintains context across multiple exchanges

**Streaming Options:**
- **Real-time Streaming**: Responses appear as the AI generates them using `Runner.run_streamed()` (most engaging)
- **Simulated Streaming**: Responses are generated fully, then displayed with typing effect (more reliable)
- Toggle the streaming mode using the checkbox above
- Real-time streaming shows tool calls, outputs, and message generation in real-time
- **Note**: Anthropic models automatically fall back to non-streaming if validation errors occur
"""

# Model comparison guide content
MODEL_COMPARISON_CONTENT = """
## 🔵 Anthropic Claude Models

| Model | Capability | Speed | Cost | Best For |
|-------|------------|--------|------|----------|
| claude-4-opus | ★★★★★ | ★★★☆☆ | ★★★★★ | Complex analysis, detailed plans |
| claude-4-sonnet | ★★★★☆ | ★★★★☆ | ★★★★☆ | Balanced high performance |
| claude-3.7-sonnet | ★★★★☆ | ★★★★☆ | ★★★☆☆ | Extended thinking, complex tasks |
| claude-3.5-sonnet | ★★★★☆ | ★★★★☆ | ★★★☆☆ | General use, balanced |
| claude-3.5-haiku | ★★★☆☆ | ★★★★★ | ★★☆☆☆ | Fast responses |
| claude-3-haiku | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | Most cost-effective |

## 🟢 OpenAI GPT Models

| Model | Capability | Speed | Cost | Best For |
|-------|------------|--------|------|----------|
| gpt-4o | ★★★★★ | ★★★★☆ | ★★★★☆ | Latest features, vision support |
| gpt-4o-mini | ★★★★☆ | ★★★★★ | ★★☆☆☆ | **DEFAULT** - Balanced performance, affordable |
| gpt-4-turbo | ★★★★☆ | ★★★★☆ | ★★★★☆ | Large context, reliable |
| gpt-3.5-turbo | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | Fast and economical |
| o1-preview | ★★★★★ | ★★☆☆☆ | ★★★★★ | Advanced reasoning |
| o1-mini | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | Reasoning tasks |
| o3-mini | ★★★★☆ | ★★★★☆ | ★★★☆☆ | Latest reasoning model |

## 🚀 Groq Models (Fast & Free)

| Model | Capability | Speed | Cost | Best For | Complex Tasks |
|-------|------------|--------|------|----------|---------------|
| llama-3.3-70b-versatile | ★★★★☆ | ★★★★★ | ★☆☆☆☆ | Balanced performance | ✅ Excellent |
| mixtral-8x7b-32768 | ★★★★☆ | ★★★★★ | ★☆☆☆☆ | Structured output | ✅ Excellent |
| llama3-70b-8192 | ★★★★☆ | ★★★★★ | ★☆☆☆☆ | General tasks | ✅ Good |
| qwen3-32b | ★★★★☆ | ★★★★★ | ★☆☆☆☆ | Code and analysis | ✅ Good |
| kimi-k2-instruct | ★★★★☆ | ★★★★★ | ★★☆☆☆ | Instruction following | ✅ Good |
| gemma2-9b-it | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | Light tasks | ⚠️ Limited |
| llama-3.1-8b-instant | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | Quick responses | ⚠️ Limited |
| llama3-8b-8192 | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | Basic tasks | ⚠️ Limited |
| gemma-7b-it | ★★☆☆☆ | ★★★★★ | ★☆☆☆☆ | Simple queries | ❌ Basic Only |
| llama2-70b-4096 | ★★★☆☆ | ★★★★☆ | ★☆☆☆☆ | Legacy support | ⚠️ Limited |

### 💡 Provider Comparison
- **🔵 Anthropic**: Excellent for detailed analysis, safety-focused, great for complex fitness planning
- **🟢 OpenAI**: Familiar interface, good general performance, strong tool usage
- **🚀 Groq**: Ultra-fast inference, free to use, varying complexity handling

### ⚠️ Model Capability Warnings for Fitness Plan Creation

**✅ EXCELLENT for Complex Fitness Plans:**
- claude-4-opus, claude-4-sonnet, claude-3.7-sonnet, claude-3.5-sonnet
- gpt-4o, gpt-4-turbo, o1-preview, o1-mini, o3-mini
- llama-3.3-70b-versatile, mixtral-8x7b-32768

**✅ GOOD for Fitness Plans (may need more specific prompting):**
- claude-3.5-haiku, gpt-4o-mini, gpt-3.5-turbo
- llama3-70b-8192, qwen3-32b, kimi-k2-instruct

**⚠️ LIMITED for Complex Plans (basic guidance only):**
- claude-3-haiku
- gemma2-9b-it, llama-3.1-8b-instant, llama3-8b-8192, llama2-70b-4096

**❌ NOT RECOMMENDED for Detailed Fitness Plans:**
- gemma-7b-it (may produce incomplete or empty plans)

### 🎯 Recommendations by Use Case
- **Quick questions**: claude-3.5-haiku, gpt-4o-mini, gpt-3.5-turbo, any Groq model
- **Comprehensive fitness plans**: claude-3.5-sonnet+, gpt-4o+, llama-3.3-70b-versatile, mixtral-8x7b-32768
- **Complex analysis**: claude-4-opus, gpt-4o, o1-preview
- **Budget-conscious**: claude-3-haiku, gpt-3.5-turbo, gpt-4o-mini
- **Speed priority**: Any Groq model, claude-3.5-haiku, gpt-4o-mini

### 🔧 Troubleshooting Complex Tasks
If you experience **empty or incomplete fitness plans** with smaller models:
1. Switch to a higher-capability model (marked as ✅ Excellent above)
2. Be more specific in your requests
3. Try models like `mixtral-8x7b-32768` which excel at structured output
4. For Groq models, `llama-3.3-70b-versatile` provides the best results
"""

# Example prompts for the Examples component
EXAMPLE_PROMPTS = [
    "Create a beginner workout plan for me",
    "I want to lose weight - help me with a fitness plan", 
    "Design a muscle building program for intermediate level",
    "I need a meal plan for gaining muscle mass",
    "What exercises should I do for better cardiovascular health?",
    "Help me with a home workout routine with no equipment"
]
