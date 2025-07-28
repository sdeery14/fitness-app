"""
Main Gradio UI application for the fitness app.
"""
import gradio as gr
from typing import Dict, Any

from .components import UIComponents
from .handlers import UIHandlers
from .styles import MAIN_CSS
from fitness_core.utils import Config, get_logger

logger = get_logger(__name__)


class FitnessAppUI:
    """Main UI application class."""
    
    def __init__(self):
        """Initialize the UI application."""
        self.demo = None
        self._setup_interface()
    
    def _setup_interface(self) -> None:
        """Set up the Gradio interface."""
        with gr.Blocks(
            theme=gr.themes.Soft(), 
            title="Fitness AI Assistant",
            css=MAIN_CSS
        ) as self.demo:
            
            # Header
            UIComponents.create_header()
            
            # Model selection section
            with gr.Row():
                (model_dropdown, selected_model) = UIComponents.create_model_selection_section()
            
            # Main chat interface
            with gr.Row():
                with gr.Column():
                    chatbot = UIComponents.create_chatbot()
                with gr.Column(scale=0.3):
                    output_audio = UIComponents.create_output_audio()
            
            chat_input = UIComponents.create_chat_input()
            
            # Control buttons
            clear_btn, streaming_toggle, tts_toggle = UIComponents.create_control_buttons()
            
            # Examples section
            UIComponents.create_examples_section(chat_input)
            
            # Help sections
            UIComponents.create_help_section()
            UIComponents.create_model_comparison_section()
            
            # Event handlers
            self._setup_event_handlers(
                chatbot, chat_input, clear_btn, streaming_toggle, tts_toggle,
                model_dropdown, selected_model, output_audio
            )
    
    def _setup_event_handlers(
        self, 
        chatbot: gr.Chatbot,
        chat_input: gr.MultimodalTextbox,
        clear_btn: gr.Button,
        streaming_toggle: gr.Checkbox,
        tts_toggle: gr.Checkbox,
        model_dropdown: gr.Dropdown,
        selected_model: gr.Textbox,
        output_audio: gr.Audio
    ) -> None:
        """Set up all event handlers."""
        
        # Chat message handling (text/file/audio input)
        chat_msg = chat_input.submit(
            UIHandlers.add_message_with_audio, 
            [chatbot, chat_input], 
            [chatbot, chat_input],
            queue=False
        )
        bot_msg = chat_msg.then(
            UIHandlers.dynamic_bot, 
            [chatbot, streaming_toggle, tts_toggle, selected_model], 
            [chatbot, output_audio], 
            api_name="bot_response"
        )
        bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

        # Model selection from dropdown
        model_dropdown.change(
            UIHandlers.select_model_from_dropdown,
            inputs=[model_dropdown],
            outputs=[selected_model]
        )

        # Clear conversation handler
        clear_btn.click(UIHandlers.clear_conversation, None, chatbot)

        # Like/dislike feedback
        chatbot.like(UIHandlers.print_like_dislike, None, None, like_user_message=True)
    
    def launch(self, **kwargs) -> None:
        """Launch the Gradio app."""
        # Get default config and merge with provided kwargs
        config = Config.get_gradio_config()
        config.update(kwargs)
        
        logger.info(f"Launching fitness app UI on {config['server_name']}:{config['server_port']}")
        self.demo.launch(**config)
    
    def get_demo(self) -> gr.Blocks:
        """Get the Gradio demo object."""
        return self.demo


def create_fitness_app() -> gr.Blocks:
    """Create and return a new fitness app UI instance."""
    app = FitnessAppUI()
    return app.get_demo()
