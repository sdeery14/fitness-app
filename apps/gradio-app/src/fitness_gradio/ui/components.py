"""
UI components for the fitness app.
"""
import gradio as gr
from typing import List

from fitness_core.agents import FitnessAgent
from .styles import (
    HEADER_MARKDOWN, 
    HELP_CONTENT, 
    MODEL_COMPARISON_CONTENT, 
    EXAMPLE_PROMPTS
)


class UIComponents:
    """Factory class for creating UI components."""
    
    @staticmethod
    def create_header() -> gr.Markdown:
        """Create the app header."""
        return gr.Markdown(HEADER_MARKDOWN)
    
    @staticmethod
    def create_model_selection_section() -> tuple:
        """
        Create the model selection section with dropdown.
        
        Returns:
            Tuple of (model_dropdown, selected_model)
        """
        with gr.Column():
            gr.Markdown("### 🤖 AI Model Selection")
            
            # Get model data and organize by provider
            table_data = FitnessAgent.get_models_table_data()
            
            # Organize models by provider
            anthropic_models = []
            openai_models = []
            groq_models = []
            
            for row in table_data:
                star, provider, model_name, capability, speed, cost, description = row
                
                # Extract provider information and create display text
                if "Anthropic" in provider:
                    display_text = f"{model_name} (Anthropic)"
                    anthropic_models.append((display_text, model_name))
                elif "OpenAI" in provider and "via Groq" not in provider:
                    display_text = f"{model_name} (OpenAI)"
                    openai_models.append((display_text, model_name))
                elif "via Groq" in provider:
                    # Only include text generation models from Groq (exclude Whisper speech-to-text models)
                    if model_name.startswith("whisper"):
                        continue  # Skip Whisper models as they are speech-to-text, not text generation
                    
                    # Extract the actual provider (Meta, Google, etc.) from the provider string
                    if "Meta" in provider:
                        display_text = f"{model_name} (Meta via Groq)"
                    elif "Google" in provider:
                        display_text = f"{model_name} (Google via Groq)"
                    elif "Mistral" in provider:
                        display_text = f"{model_name} (Mistral via Groq)"
                    elif "Alibaba" in provider:
                        display_text = f"{model_name} (Alibaba via Groq)"
                    elif "Moonshot" in provider:
                        display_text = f"{model_name} (Moonshot via Groq)"
                    elif "OpenAI" in provider:
                        display_text = f"{model_name} (OpenAI via Groq)"
                    else:
                        display_text = f"{model_name} (Groq)"
                    groq_models.append((display_text, model_name))
                else:
                    # Fallback for unknown providers
                    display_text = f"{model_name} (Unknown)"
                    openai_models.append((display_text, model_name))
            
            # Sort within each provider by model size (largest to smallest)
            # Define model hierarchy for sorting
            model_order = {
                # Anthropic models (largest to smallest)
                "claude-4-opus": 0,
                "claude-4-sonnet": 1,
                "claude-3.7-sonnet": 2,
                "claude-3.5-sonnet-latest": 3,
                "claude-3.5-sonnet": 4,
                "claude-3.5-haiku": 5,
                "claude-3-haiku": 6,
                
                # OpenAI models (largest to smallest)
                "gpt-4o": 0,
                "gpt-4-turbo": 1,
                "gpt-4": 2,
                "gpt-4o-mini": 3,
                "gpt-3.5-turbo": 4,
                "o1-preview": 5,
                "o1-mini": 6,
                "o3-mini": 7,
                
                # Groq models (by capability and size - text generation only)
                "llama-3.3-70b-versatile": 0,
                "llama3-70b-8192": 1,
                "mixtral-8x7b-32768": 2,
                "qwen3-32b": 3,
                "kimi-k2-instruct": 4,
                "gemma2-9b-it": 5,
                "llama-3.1-8b-instant": 6,
                "llama3-8b-8192": 7,
                "gemma-7b-it": 8,
                "llama2-70b-4096": 9,
            }
            
            anthropic_models.sort(key=lambda x: model_order.get(x[1], 999))
            openai_models.sort(key=lambda x: model_order.get(x[1], 999))
            groq_models.sort(key=lambda x: model_order.get(x[1], 999))
            
            # Create final dropdown choices organized by provider
            dropdown_choices = []
            
            # Add Anthropic models first (alphabetically first)
            dropdown_choices.extend(anthropic_models)
            
            # Add Groq models (fast and cost-effective)
            dropdown_choices.extend(groq_models)
            
            # Add OpenAI models last
            dropdown_choices.extend(openai_models)
            
            # Main model selection dropdown (full width)
            model_dropdown = gr.Dropdown(
                choices=dropdown_choices,
                value="claude-3.5-haiku",
                label="Select AI Model",
                info="Choose your preferred AI model for fitness guidance",
                elem_classes=["model-dropdown"]
            )
            
            # Hidden component to manage selection (for compatibility)
            selected_model = gr.Textbox(
                value="claude-3.5-haiku",
                visible=False,
                label="Selected Model"
            )
        
        return model_dropdown, selected_model
    
    @staticmethod
    def create_chatbot() -> gr.Chatbot:
        """Create the main chatbot component."""
        return gr.Chatbot(
            elem_id="chatbot", 
            type="messages",
            show_copy_button=True,
            show_share_button=False,
            avatar_images=None,
            sanitize_html=True,
            render_markdown=True
        )
    
    @staticmethod
    def create_output_audio() -> gr.Audio:
        """Create the output audio component for TTS responses."""
        return gr.Audio(
            label="🔊 Audio Response", 
            streaming=False,  # Disable streaming to avoid ffmpeg issues
            autoplay=True,
            show_download_button=True,
            show_share_button=False,
            format="wav",  # Explicitly set format to WAV
            visible=False  # Initially hidden, will show when TTS is enabled
        )
    
    @staticmethod
    def create_chat_input() -> gr.MultimodalTextbox:
        """Create the chat input component."""
        return gr.MultimodalTextbox(
            interactive=True,
            file_count="multiple",
            placeholder="Ask me about fitness, request a workout plan, or get meal planning advice...",
            show_label=False,
            sources=["microphone", "upload"],  # Enable microphone and file uploads
            submit_btn=True,  # Ensure submit button is available
        )
    
    @staticmethod
    def create_control_buttons() -> tuple:
        """
        Create the control buttons (clear, streaming toggle, TTS toggle).
        
        Returns:
            Tuple of (clear_btn, streaming_toggle, tts_toggle)
        """
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Conversation", variant="secondary", size="sm")
            streaming_toggle = gr.Checkbox(
                label="🚀 Enable Real-time Streaming", 
                value=True, 
                info="Stream responses in real-time as the agent generates them"
            )
            tts_toggle = gr.Checkbox(
                label="🔊 Enable Text-to-Speech", 
                value=False, 
                info="Convert AI responses to speech using Groq's TTS models"
            )
        
        return clear_btn, streaming_toggle, tts_toggle
    
    @staticmethod
    def create_examples_section(chat_input: gr.MultimodalTextbox) -> gr.Examples:
        """Create the examples section."""
        with gr.Row():
            return gr.Examples(
                examples=EXAMPLE_PROMPTS,
                inputs=chat_input,
                label="💡 Try asking:"
            )
    
    @staticmethod
    def create_help_section() -> gr.Accordion:
        """Create the help accordion section."""
        with gr.Accordion("ℹ️ How to use this assistant", open=False):
            gr.Markdown(HELP_CONTENT)
    
    @staticmethod
    def create_model_comparison_section() -> gr.Accordion:
        """Create the model comparison accordion section."""
        with gr.Accordion("🤖 Model Comparison Guide", open=False):
            gr.Markdown(MODEL_COMPARISON_CONTENT)
    
    @staticmethod
    def create_voice_conversation_section() -> tuple:
        """
        Create the voice conversation section with controls and audio components.
        
        Returns:
            Tuple of (voice_btn, voice_status, voice_audio, voice_output, voice_exit_btn)
        """
        with gr.Row():
            gr.Markdown("### 🎙️ Voice Conversation")
        
        with gr.Row():
            voice_btn = gr.Button(
                "🎤 Start Voice Conversation", 
                variant="primary",
                size="lg"
            )
            voice_exit_btn = gr.Button(
                "❌ Exit Voice Chat", 
                variant="stop",
                size="lg",
                visible=False
            )
        
        # Voice conversation status indicator
        voice_status = gr.Markdown(
            value="",
            visible=False,
            elem_id="voice-status"
        )
        
        with gr.Row(visible=False, elem_id="voice-conversation-row") as voice_row:
            with gr.Column():
                # Audio input for voice conversation
                voice_audio = gr.Audio(
                    label="🎤 Voice Input",
                    sources=["microphone"],
                    type="numpy",
                    streaming=False,
                    waveform_options=gr.WaveformOptions(waveform_color="#B83A4B"),
                    elem_id="voice-audio"
                )
            
            with gr.Column():
                # Audio output for voice responses
                voice_output = gr.Audio(
                    label="🔊 AI Voice Response",
                    streaming=False,
                    autoplay=True,
                    show_download_button=True,
                    elem_id="voice-output"
                )
        
        # Voice conversation chatbot - use main chatbot instead of separate one
        # Remove separate voice_chatbot to use shared main chatbot
        
        return voice_btn, voice_status, voice_audio, voice_output, voice_exit_btn, voice_row

    @staticmethod
    def create_fitness_plan_section() -> tuple:
        """
        Create the fitness plan display section.
        
        Returns:
            Tuple of (plan_display, view_plan_btn, clear_plan_btn)
        """
        # Create a scrollable fitness plan display similar to chatbot
        plan_display = gr.Markdown(
            value="**No Fitness Plan Available**\n\nNo fitness plan has been generated yet. Ask me to create a personalized fitness plan for you!",
            label="Current Fitness Plan",
            elem_id="fitness-plan-display",
            elem_classes=["fitness-plan-container"],
            show_label=False,  # Hide the label to save space
            container=True
        )
        
        with gr.Row(elem_classes=["fitness-plan-buttons"]):
            view_plan_btn = gr.Button(
                "📋 View Latest Plan", 
                variant="primary",
                size="sm",
                scale=1
            )
            clear_plan_btn = gr.Button(
                "🗑️ Clear Plan", 
                variant="secondary", 
                size="sm",
                scale=1
            )
        
        return plan_display, view_plan_btn, clear_plan_btn
