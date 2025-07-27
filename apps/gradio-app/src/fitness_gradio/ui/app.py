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
                (model_table, model_filter, 
                 selected_model, model_info_display) = UIComponents.create_model_selection_section()
            
            # Main chat interface
            chatbot = UIComponents.create_chatbot()
            chat_input = UIComponents.create_chat_input()
            
            # Control buttons
            clear_btn, streaming_toggle = UIComponents.create_control_buttons()
            
            # Examples section
            UIComponents.create_examples_section(chat_input)
            
            # Help sections
            UIComponents.create_help_section()
            UIComponents.create_model_comparison_section()
            
            # Event handlers
            self._setup_event_handlers(
                chatbot, chat_input, clear_btn, streaming_toggle,
                model_table, model_filter, selected_model, model_info_display
            )
    
    def _setup_event_handlers(
        self, 
        chatbot: gr.Chatbot,
        chat_input: gr.MultimodalTextbox,
        clear_btn: gr.Button,
        streaming_toggle: gr.Checkbox,
        model_table: gr.DataFrame,
        model_filter: gr.Dropdown,
        selected_model: gr.Textbox,
        model_info_display: gr.Markdown
    ) -> None:
        """Set up all event handlers."""
        
        # Chat message handling
        chat_msg = chat_input.submit(
            UIHandlers.add_message, 
            [chatbot, chat_input], 
            [chatbot, chat_input]
        )
        bot_msg = chat_msg.then(
            UIHandlers.dynamic_bot, 
            [chatbot, streaming_toggle, selected_model], 
            chatbot, 
            api_name="bot_response"
        )
        bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

        # Model table filtering
        model_filter.change(
            UIHandlers.filter_model_table,
            inputs=[model_filter],
            outputs=[model_table]
        )
        
        # Model selection from table
        model_table.select(
            UIHandlers.select_model_from_table,
            inputs=[model_table],
            outputs=[selected_model, model_info_display]
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
