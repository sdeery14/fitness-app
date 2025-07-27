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

**To get the best results:**
- Tell me your fitness level (beginner, intermediate, advanced)
- Mention your goals (weight loss, muscle gain, general fitness)
- Include any equipment you have access to
- Let me know about any injuries or limitations

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

### 💡 Provider Comparison
- **🔵 Anthropic**: Excellent for detailed analysis, safety-focused, great for complex fitness planning
- **🟢 OpenAI**: Familiar interface, good general performance, strong tool usage

### 🎯 Recommendations by Use Case
- **Quick questions**: claude-3.5-haiku, gpt-4o-mini, gpt-3.5-turbo
- **Comprehensive plans**: claude-3.5-sonnet, gpt-4o, claude-3.7-sonnet
- **Complex analysis**: claude-4-opus, gpt-4o, o1-preview
- **Budget-conscious**: claude-3-haiku, gpt-3.5-turbo, gpt-4o-mini
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
