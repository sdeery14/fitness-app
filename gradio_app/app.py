"""
Main Gradio UI application for the fitness app.
"""
import gradio as gr
from typing import Generator, List, Dict, Any
import logging

from fitness_agent import FitnessAgent, FitnessAgentRunner
from fitness_agent.utils import Config

logger = logging.getLogger(__name__)


def create_app() -> gr.Blocks:
    """Create and return the Gradio application."""
    
    def chat_with_agent(message: str, history: List[List[str]], model_name: str) -> Generator[List[List[str]], None, None]:
        """Handle chat messages with the fitness agent."""
        try:
            # Initialize agent with selected model
            agent = FitnessAgent(model_name=model_name)
            
            # Convert history to agent format
            agent_input = []
            for user_msg, assistant_msg in history:
                agent_input.append({"role": "user", "content": user_msg})
                if assistant_msg:
                    agent_input.append({"role": "assistant", "content": assistant_msg})
            
            # Add current message
            agent_input.append({"role": "user", "content": message})
            
            # Stream response
            response_text = ""
            for chunk in FitnessAgentRunner.run_agent_with_streaming_sync(agent, agent_input):
                if chunk['type'] == 'content':
                    response_text += chunk['content']
                    # Update history with partial response
                    new_history = history + [[message, response_text]]
                    yield new_history
                elif chunk['type'] == 'final_result':
                    response_text = chunk['content']
                    # Final update
                    new_history = history + [[message, response_text]]
                    yield new_history
                    
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            new_history = history + [[message, error_msg]]
            yield new_history

    # Create the interface
    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="Fitness AI Assistant"
    ) as demo:
        
        # Header
        gr.Markdown("# 💪 Fitness AI Assistant")
        gr.Markdown("Get personalized fitness plans and nutrition advice from your AI trainer!")
        
        # Model selection
        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=[
                    "gpt-4o",
                    "gpt-4o-mini", 
                    "claude-3.5-sonnet",
                    "claude-3.5-haiku",
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant"
                ],
                value="llama-3.3-70b-versatile",
                label="AI Model",
                info="Choose which AI model to use for your fitness assistant"
            )
        
        # Chat interface
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Chat with your Fitness AI",
                    height=500,
                    show_label=True
                )
                
                with gr.Row():
                    msg_textbox = gr.Textbox(
                        placeholder="Ask about fitness plans, exercises, nutrition...",
                        label="Your message",
                        scale=4
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                
                # Clear button
                clear_btn = gr.Button("Clear Chat", variant="secondary")
        
        # Example questions
        with gr.Row():
            gr.Markdown("### 💡 Try asking:")
            with gr.Column():
                example1 = gr.Button("Create a workout plan for muscle building", variant="secondary")
                example2 = gr.Button("I'm a beginner, what should I start with?", variant="secondary")
                example3 = gr.Button("Plan a nutrition strategy for weight loss", variant="secondary")
        
        # Event handlers
        def clear_chat():
            return []
        
        def send_example(example_text):
            return example_text
        
        # Set up event handling
        msg_textbox.submit(
            chat_with_agent,
            inputs=[msg_textbox, chatbot, model_dropdown],
            outputs=[chatbot]
        ).then(
            lambda: "",  # Clear the textbox
            outputs=[msg_textbox]
        )
        
        send_btn.click(
            chat_with_agent,
            inputs=[msg_textbox, chatbot, model_dropdown],
            outputs=[chatbot]
        ).then(
            lambda: "",  # Clear the textbox
            outputs=[msg_textbox]
        )
        
        clear_btn.click(clear_chat, outputs=[chatbot])
        
        # Example button handlers
        example1.click(send_example, inputs=[example1], outputs=[msg_textbox])
        example2.click(send_example, inputs=[example2], outputs=[msg_textbox])
        example3.click(send_example, inputs=[example3], outputs=[msg_textbox])
    
    return demo


if __name__ == "__main__":
    # Run the app
    app = create_app()
    app.launch(**Config.get_gradio_config())
