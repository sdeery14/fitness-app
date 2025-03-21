import gradio as gr
import os
from fitness_assistant import FitnessAssistant

# Create a Fitness Assistant instance
fitness_assistant = FitnessAssistant()

with gr.Blocks() as demo:

    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(type="messages", value=fitness_assistant.generate_welcome_message())
            msg = gr.Textbox()
            clear = gr.Button("Clear")
        with gr.Column():
            fitness_plan = gr.JSON(label="Your Fitness Plan")

    msg.submit(
        fitness_assistant.add_message_to_chat, 
        [msg],
        [msg, chatbot],
        queue=False
    ).then(
        fitness_assistant.process_chat, 
        [chatbot], 
        [chatbot, fitness_plan]
    )
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":

    server_name = os.getenv("SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("SERVER_PORT", 7860))
    
    demo.launch(server_name=server_name, server_port=server_port)