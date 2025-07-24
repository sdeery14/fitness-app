import gradio as gr
import time
import asyncio
import threading
from fitness_agent import FitnessAgent
from agents import Runner

# Chatbot demo with multimodal input (text, markdown, LaTeX, code blocks, image, audio, & video). Plus shows support for streaming text.


def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)


def add_message(history, message):
    for x in message["files"]:
        history.append({"role": "user", "content": {"path": x}})
    if message["text"] is not None:
        history.append({"role": "user", "content": message["text"]})
    return history, gr.MultimodalTextbox(value=None, interactive=False)


def convert_gradio_history_to_agent_format(history):
    """Convert Gradio history format to agents library format"""
    # Build a conversation string that includes context
    conversation_parts = []
    
    for message in history:
        if isinstance(message, dict):
            role = message.get("role", "user")
            content = message.get("content", "")
            
            # Handle file content
            if isinstance(content, dict) and "path" in content:
                content = f"[File uploaded: {content['path']}]"
            
            # Add to conversation with proper formatting
            if role == "user":
                conversation_parts.append(f"User: {content}")
            elif role == "assistant" and content:
                conversation_parts.append(f"Assistant: {content}")
    
    # If we have conversation history, format it properly
    if len(conversation_parts) > 1:
        # Include previous context and the current user message
        full_conversation = "\n".join(conversation_parts[:-1])
        current_message = conversation_parts[-1].replace("User: ", "")
        return f"Previous conversation:\n{full_conversation}\n\nCurrent message: {current_message}"
    elif conversation_parts:
        # Just the current message
        return conversation_parts[-1].replace("User: ", "")
    else:
        return "Hello"


def run_agent_in_new_loop(agent, history):
    """Run the agent in a new event loop in a separate thread"""
    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Convert Gradio history to agent format
            user_input = convert_gradio_history_to_agent_format(history)
            result = Runner.run_sync(agent, user_input)
            return result
        finally:
            loop.close()
    
    # Run in a thread to avoid event loop conflicts
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_run)
        return future.result()


def format_fitness_plan(plan_obj):
    """Format a FitnessPlan object into a nicely structured markdown string"""
    if hasattr(plan_obj, 'name') and hasattr(plan_obj, 'training_plan') and hasattr(plan_obj, 'meal_plan'):
        formatted_response = f"""# 🏋️ {plan_obj.name}

## 💪 Training Plan
{plan_obj.training_plan}

## 🥗 Meal Plan
{plan_obj.meal_plan}

---
*Your personalized fitness plan is ready! Feel free to ask any questions about the plan or request modifications.*
"""
        return formatted_response
    return str(plan_obj)


def bot(history: list):
    agent = FitnessAgent()
    result = run_agent_in_new_loop(agent, history)
    
    # Handle different response types
    if hasattr(result, 'final_output'):
        response_data = result.final_output
    else:
        response_data = result
    
    # Check if this is a structured FitnessPlan output
    if hasattr(response_data, 'name') and hasattr(response_data, 'training_plan') and hasattr(response_data, 'meal_plan'):
        # Format the structured plan beautifully
        response = format_fitness_plan(response_data)
    elif isinstance(response_data, str):
        response = response_data
    else:
        # Fallback for other types
        response = str(response_data)
    
    history.append({"role": "assistant", "content": ""})
    for character in response:
        history[-1]["content"] += character
        time.sleep(0.02)  # Slightly faster streaming for better UX
        yield history


with gr.Blocks(theme=gr.themes.Soft(), title="Fitness AI Assistant") as demo:
    gr.Markdown("""
    # 🏋️‍♀️ Fitness AI Assistant
    Your personal fitness companion for workout plans, meal planning, and fitness guidance!
    """)
    
    chatbot = gr.Chatbot(
        elem_id="chatbot", 
        type="messages",
        height=600,
        show_copy_button=True
    )

    chat_input = gr.MultimodalTextbox(
        interactive=True,
        file_count="multiple",
        placeholder="Ask me about fitness, request a workout plan, or get meal planning advice...",
        show_label=False,
        sources=["microphone", "upload"],
    )
    
    # Add example buttons for common requests
    with gr.Row():
        gr.Examples(
            examples=[
                "Create a beginner workout plan for me",
                "I want to lose weight - help me with a fitness plan",
                "Design a muscle building program",
                "I need a meal plan for gaining muscle",
                "What exercises should I do for better cardiovascular health?"
            ],
            inputs=chat_input,
            label="💡 Try asking:"
        )

    chat_msg = chat_input.submit(
        add_message, [chatbot, chat_input], [chatbot, chat_input]
    )
    bot_msg = chat_msg.then(bot, chatbot, chatbot, api_name="bot_response")
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

    chatbot.like(print_like_dislike, None, None, like_user_message=True)

demo.launch()