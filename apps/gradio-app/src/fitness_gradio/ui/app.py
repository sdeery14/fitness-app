"""
Main Gradio UI application for the fitness app.
"""
import gradio as gr
from typing import Dict, Any

from .components import UIComponents
from .handlers import UIHandlers
from .styles import MAIN_CSS
from .voice_conversation import (
    get_voice_conversation_js, 
    VoiceConversationState,
    reset_voice_audio_input
)
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
            css=MAIN_CSS,
            js=get_voice_conversation_js()  # Add VAD JavaScript
        ) as self.demo:
            
            # Header
            UIComponents.create_header()
            
            # Model selection section
            with gr.Row():
                (model_dropdown, selected_model) = UIComponents.create_model_selection_section()
            
            # Main chat interface
            chatbot = UIComponents.create_chatbot()
            
            chat_input = UIComponents.create_chat_input()
            
            # Control buttons
            clear_btn, streaming_toggle, tts_toggle = UIComponents.create_control_buttons()
            
            # Voice conversation section
            (voice_btn, voice_status, voice_audio, voice_output, 
             voice_exit_btn, voice_row, voice_chatbot) = UIComponents.create_voice_conversation_section()
            
            # Voice conversation state
            voice_state = gr.State(value=VoiceConversationState())
            
            # Audio response (positioned near TTS controls)
            with gr.Row():
                with gr.Column():
                    output_audio = UIComponents.create_output_audio()
            
            # Examples section
            UIComponents.create_examples_section(chat_input)
            
            # Help sections
            UIComponents.create_help_section()
            UIComponents.create_model_comparison_section()
            
            # Event handlers
            self._setup_event_handlers(
                chatbot, chat_input, clear_btn, streaming_toggle, tts_toggle,
                model_dropdown, selected_model, output_audio,
                voice_btn, voice_status, voice_audio, voice_output, 
                voice_exit_btn, voice_row, voice_chatbot, voice_state
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
        output_audio: gr.Audio,
        voice_btn: gr.Button,
        voice_status: gr.Markdown,
        voice_audio: gr.Audio,
        voice_output: gr.Audio,
        voice_exit_btn: gr.Button,
        voice_row: gr.Row,
        voice_chatbot: gr.Chatbot,
        voice_state: gr.State
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

        # TTS toggle handler to show/hide audio component
        tts_toggle.change(
            UIHandlers.toggle_audio_visibility,
            inputs=[tts_toggle],
            outputs=[output_audio]
        )

        # Like/dislike feedback
        chatbot.like(UIHandlers.print_like_dislike, None, None, like_user_message=True)
        
        # Voice conversation event handlers
        
        # Start voice conversation
        voice_btn.click(
            UIHandlers.start_voice_conversation,
            inputs=[],
            outputs=[voice_state, voice_status]
        ).then(
            # Update component visibility
            lambda: (gr.update(visible=True), gr.update(visible=True), 
                    gr.update(visible=True), gr.update(visible=False), 
                    gr.update(visible=True)),
            outputs=[voice_status, voice_row, voice_chatbot, voice_btn, voice_exit_btn]
        )
        
        # End voice conversation and merge history
        voice_exit_btn.click(
            UIHandlers.end_voice_conversation,
            inputs=[voice_state, chatbot],
            outputs=[voice_state, voice_status, voice_chatbot, chatbot]
        ).then(
            # Update component visibility
            lambda: (gr.update(visible=False), gr.update(visible=False), 
                    gr.update(visible=False), gr.update(visible=True), 
                    gr.update(visible=False)),
            outputs=[voice_status, voice_row, voice_chatbot, voice_btn, voice_exit_btn]
        )
        
        # Voice input handling with automatic recording
        voice_stream = voice_audio.start_recording(
            lambda audio, state: (audio, state),  # Simple pass-through
            inputs=[voice_audio, voice_state],
            outputs=[voice_audio, voice_state]
        )
        
        voice_response = voice_audio.stop_recording(
            UIHandlers.handle_voice_input,
            inputs=[voice_state, voice_audio, selected_model],
            outputs=[voice_state, voice_chatbot, voice_output]
        )
        
        # Reset audio input after response to prepare for next conversation turn
        voice_response.then(
            lambda state: (state, reset_voice_audio_input()),  # Clear audio input
            inputs=[voice_state],
            outputs=[voice_state, voice_audio]
        )
    
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
