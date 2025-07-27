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
        Create the model selection section with table and controls.
        
        Returns:
            Tuple of (model_table, model_filter, selected_model, model_info_display)
        """
        with gr.Column():
            gr.Markdown("### 🤖 AI Model Selection")
            gr.Markdown("Browse and select your preferred AI model. Click on a row to select it.")
            
            # Create model table data
            table_data = FitnessAgent.get_models_table_data()
            
            model_table = gr.DataFrame(
                value=table_data,
                headers=["⭐", "Provider", "Model Name", "Capability", "Speed", "Cost", "Description"],
                datatype=["str", "str", "str", "str", "str", "str", "str"],
                interactive=False,
                wrap=True,
                elem_classes=["model-table"]
            )
            
            # Hidden component to manage selection
            selected_model = gr.Textbox(
                value="gpt-4o-mini",
                visible=False,
                label="Selected Model"
            )
            
            # Model filter dropdown
            with gr.Row():
                model_filter = gr.Dropdown(
                    choices=["All Models", "🔵 Anthropic Only", "🟢 OpenAI Only", "⭐ Recommended Only"],
                    value="All Models",
                    label="Filter Models",
                    scale=3
                )
        
        # Model information display
        model_info_display = gr.Markdown(
            value=f"""🤖 **Current Model:** `gpt-4o-mini`

💡 **Description:** {FitnessAgent.get_model_info('gpt-4o-mini')}

📊 **Status:** Ready to chat!""",
            visible=True,
            elem_classes=["model-info"]
        )
        
        return model_table, model_filter, selected_model, model_info_display
    
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
