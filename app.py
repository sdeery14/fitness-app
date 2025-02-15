import gradio as gr
import random
import time
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai = OpenAI()

# Initialize conversation history with a system message
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
You are a friendly, knowledgeable fitness assistant. Your goal is to help users achieve their fitness goals by providing clear, actionable advice about exercise, nutrition, and healthy habits. 

When a user shares their goals, help them develop a personalized workout plan that fits their lifestyle, fitness level, and objectives. If they want, create a meal plan that supports their workouts by focusing on balanced, nutrient-rich foods. 

Be encouraging, informative, and adaptable to the user's preferences. Avoid overly technical jargon unless the user requests detailed explanations. Always prioritize safe, sustainable, and realistic practices.

Do not discuss topics unrelated to fitness, health, nutrition, or exercise. If a user asks about something off-topic, politely steer the conversation back to their fitness goals.
"""
}

def chatbot_message(history):
    completion = openai.chat.completions.create(
        model="gpt-4o",
        messages=history,
        stream=True
    )

    for chunk in completion:
        yield chunk.choices[0].delta.content

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    def user(user_message, history: list):
        if not history:
            history = [SYSTEM_PROMPT]
        return "", history + [{"role": "user", "content": user_message}]

    def bot(history: list):
        bot_message = chatbot_message(history)
        history.append({"role": "assistant", "content": ""})
        for character in bot_message:
            if character is not None:
                history[-1]['content'] += character
            time.sleep(0.05)
            yield history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    server_name = os.getenv("SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("SERVER_PORT", 7860))
    demo.launch(server_name=server_name, server_port=server_port)