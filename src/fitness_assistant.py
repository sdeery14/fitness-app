from openai import OpenAI
from dotenv import load_dotenv
from src.user_profile import UserProfile
import json
from src.fitness_plan import FitnessPlan
from src.utils.calculations import (
    calculate_calories_and_macros,
    convert_weight_lbs_to_kg,
    convert_height_in_to_cm,
)

load_dotenv()

client = OpenAI()

## Fitness Instructor class
class FitnessAssistant():

    # Initialize conversation history with a system message
    default_system_prompt = {
        "role": "system",
        "content": """
    You are a friendly, concise, knowledgeable fitness assistant.
    
    Your goal is to create a personalized fitness plan for the user and to help the user learn about fitness.
    
    A fitness plan includes a workout plan and a meal plan.

    You will lead the conversation by asking the user questions and generating the fitness plan based on the results.

    The user can also ask you questions. If they do, answer their questions like an amazing teacher would, and then
    step back in as the leader of the conversation once the user seems satisfied with their questions. 

    To start the conversation, create a short welcome message based on the following guidelines:
    - Start with a concise explanation of the process.
    - Explain that you will be concise, so encourage the user to ask questions and you will go into further detail
    - Ask for the user's fitness goal.

    Generate the fitness plan as soon as you know the user's fitness goal.

    Once the tool call to generate the fitness plan is made, do not include the plan in your response to the user. The fitness
    plan will be displayed elsewhere.

    Regenerate the fitness plan if the user provides new information that helps you personalize the plan.

    Be concise. Provide short answers when possible but go into detail when the user asks for it.
    
    Do not discuss topics unrelated to fitness, health, nutrition, or exercise. 
    
    If a user asks about something off-topic, politely steer the conversation back to their fitness goals.
    """
    }

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_fitness_plan",
                "description": "Generates a fitness plan based on the user's fitness goals.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False
                },
                "strict": True
            }
        }

    ]

    def __init__(
            self, name: str = "FitBot", 
            system_prompt: dict = default_system_prompt
            ):
        self.name = name
        self.user_profile = UserProfile()
        self.system_prompt = system_prompt
        self.chat_history_full = [self.system_prompt]
        self.chat_history_display = []
        self.fitness_plan = None
        self.generate_welcome_message()

    def generate_welcome_message(self):
        """
        Uses OpenAI to generate a personalized greeting and first question for the user.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[self.system_prompt]
        )

        greeting_message = response.choices[0].message.content

        self.add_message_to_chat(greeting_message, "assistant")

        return self.chat_history_display

    def generate_fitness_plan(self):

        # Add user profile data to full chat
        self.chat_history_full.append({"role": "system", "content": f"Here is the user's profile data: {self.user_profile.model_dump()}"})        

        # Get the OpenAI API generated Fitness Plan
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=self.chat_history_full,
            response_format=FitnessPlan,
        ) 
        
        self.fitness_plan = completion.choices[0].message.parsed.model_dump()

        return self.chat_history_display, self.fitness_plan

    def add_message_to_chat(self, user_message, role="user", metadata=None):        
        message = {"role": role, "content": user_message}
        if metadata:
            message["metadata"] = metadata
        
        self.chat_history_full.append(message)
        self.chat_history_display.append(message)

        # return an empty string for the front end to clear the user input box
        # and return the updated chat history for display
        return "", self.chat_history_display

    def call_function(self, name, args):
        if name == "generate_fitness_plan":
            return self.generate_fitness_plan(**args)
        # if name == "send_email":
        #     return send_email(**args)

    def process_chat(self):

        # Start streaming the OpenAI API response
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=self.chat_history_full,
            tools=self.tools
        )

        # check if the response contains a tool call
        if completion.choices[0].message.tool_calls is not None:

            

            # Call tools
            for tool_call in completion.choices[0].message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                result = self.call_function(name, args)

                # Add the tool call message to the chat history
                self.chat_history_full.append(completion.choices[0].message)

                # Add the tool call result to the chat history
                self.chat_history_full.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

            # Start streaming the OpenAI API response
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=self.chat_history_full
            )
        
        chatbot_response = completion.choices[0].message.content

        self.add_message_to_chat(chatbot_response, "assistant")

        return self.chat_history_display, self.fitness_plan



    