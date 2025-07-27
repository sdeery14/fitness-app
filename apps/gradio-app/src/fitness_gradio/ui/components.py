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
        Create the model selection section with dropdown and controls.
        
        Returns:
            Tuple of (model_dropdown, model_filter, selected_model, model_info_display)
        """
        with gr.Column():
            gr.Markdown("### 🤖 AI Model Selection")
            
            # Get model data and organize by provider
            table_data = FitnessAgent.get_models_table_data()
            
            # Organize models by provider
            anthropic_models = []
            openai_models = []
            
            for row in table_data:
                star, provider, model_name, capability, speed, cost, description = row
                
                # Create simple display text: model name (provider)
                provider_short = "Anthropic" if "Anthropic" in provider else "OpenAI"
                display_text = f"{model_name} ({provider_short})"
                
                if "Anthropic" in provider:
                    anthropic_models.append((display_text, model_name))
                else:  # OpenAI
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
            }
            
            anthropic_models.sort(key=lambda x: model_order.get(x[1], 999))
            openai_models.sort(key=lambda x: model_order.get(x[1], 999))
            
            # Create final dropdown choices without headers
            dropdown_choices = []
            
            # Add Anthropic models first (alphabetically first)
            dropdown_choices.extend(anthropic_models)
            
            # Add OpenAI models
            dropdown_choices.extend(openai_models)
            
            # Main model selection dropdown (full width)
            model_dropdown = gr.Dropdown(
                choices=dropdown_choices,
                value="gpt-4o-mini",
                label="Select AI Model",
                info="Choose your preferred AI model for fitness guidance",
                elem_classes=["model-dropdown"]
            )
            
            # Dummy filter dropdown for compatibility (hidden)
            model_filter = gr.Dropdown(
                choices=["All Models"],
                value="All Models",
                visible=False
            )
            
            # Hidden component to manage selection (for compatibility)
            selected_model = gr.Textbox(
                value="gpt-4o-mini",
                visible=False,
                label="Selected Model"
            )
        
        # Hidden model info display (for compatibility with existing handlers)
        model_info_display = gr.Markdown(
            value="",
            visible=False,
            elem_classes=["model-info"]
        )
        
        return model_dropdown, model_filter, selected_model, model_info_display
    
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
    def create_chat_input() -> gr.MultimodalTextbox:
        """Create the chat input component."""
        return gr.MultimodalTextbox(
            interactive=True,
            file_count="multiple",
            placeholder="Ask me about fitness, request a workout plan, or get meal planning advice...",
            show_label=False,
            sources=["microphone", "upload"],
        )
    
    @staticmethod
    def create_control_buttons() -> tuple:
        """
        Create the control buttons (clear, streaming toggle).
        
        Returns:
            Tuple of (clear_btn, streaming_toggle)
        """
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Conversation", variant="secondary", size="sm")
            streaming_toggle = gr.Checkbox(
                label="🚀 Enable Real-time Streaming", 
                value=True, 
                info="Stream responses in real-time as the agent generates them"
            )
        
        return clear_btn, streaming_toggle
    
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
