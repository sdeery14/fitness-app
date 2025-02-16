import gradio as gr
import random
import time
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI()

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
    try:
        #Make your OpenAI API request here
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=history,
            stream=True
        )
        for chunk in completion:
            yield chunk.choices[0].delta.content
    except APIConnectionError as e:
        #Handle connection error here
        yield f"Failed to connect to OpenAI API: {e}"
        pass
    except RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
        yield f"OpenAI API request exceeded rate limit: {e}"
        pass
    except APIError as e:
        #Handle API error here, e.g. retry or log
        yield f"OpenAI API returned an API Error: {e}"
        pass

def initialize_history():
    return [SYSTEM_PROMPT]

def update_history(history, role, content):
    history.append({"role": role, "content": content})
    return history

def user(user_message, history: list):
    if not history:
        history = initialize_history()
    return "", update_history(history, "user", user_message)

def bot(history: list):
    bot_message = chatbot_message(history)
    update_history(history, "assistant", "")
    for character in bot_message:
        if character is not None:
            history[-1]['content'] += character
        time.sleep(0.05)
        yield history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    server_name = os.getenv("SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("SERVER_PORT", 7860))
    if not server_name or not server_port:
        raise ValueError("SERVER_NAME and SERVER_PORT must be set in the environment variables.")
    demo.launch(server_name=server_name, server_port=server_port)