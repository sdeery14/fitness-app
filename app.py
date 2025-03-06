import gradio as gr
import os
from fitness_assistant import FitnessAssistant

# Create a Fitness Assistant instance
fitness_assistant = FitnessAssistant()

with gr.Blocks() as demo:

    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(type="messages", value=fitness_assistant.chat_history_display)
            msg = gr.Textbox()
            clear = gr.Button("Clear")
        with gr.Column():
            with gr.Group():
                gr.Markdown("### Enter Your Fitness Information")
                height_in = gr.Number(label="Height (inches)", value=None)
                weight_lb = gr.Number(label="Weight (pounds)", value=None)
                age = gr.Number(label="Age", value=None)
                sex = gr.Radio(label="Sex", choices=["Male", "Female"], value=None)
                activity_level = gr.Dropdown(label="Current Activity Level", choices=["Sedentary", "Lightly active", "Moderately active", "Very active", "Super active"], value=None)
                goals = gr.Textbox(label="Fitness Goals", placeholder="e.g., Lose weight, Build muscle, Improve endurance", value=None)
                diet_phase = gr.Radio(label="Diet Phase", choices=["Cutting", "Bulking", "Maintenance"], value=None)
                generate_fitness_plan_button = gr.Button("Generate Fitness Plan")
    with gr.Row():
        fitness_plan = gr.JSON(label="Your Fitness Plan")

    msg.submit(
        fitness_assistant.add_message_to_chat, 
        [msg, chatbot],
        [msg, chatbot],
        queue=False
    ).then(
        fitness_assistant.process_chat, 
        [chatbot], 
        [chatbot, fitness_plan]
    )
    clear.click(lambda: None, None, chatbot, queue=False)

    generate_fitness_plan_button.click(
        fitness_assistant.generate_fitness_plan,
        [height_in, weight_lb, age, sex, activity_level, goals, diet_phase],
        [chatbot, fitness_plan]
    )

if __name__ == "__main__":

    server_name = os.getenv("SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("SERVER_PORT", 7860))
    
    demo.launch(server_name=server_name, server_port=server_port)