from openai import OpenAI
from dotenv import load_dotenv
from user_profile import UserProfile
import json
from fitness_plan import FitnessPlan
import requests

load_dotenv()

client = OpenAI()

## Fitness Instructor class
class FitnessAssistant():

    # Initialize conversation history with a system message
    default_system_prompt = {
        "role": "system",
        "content": """
    You are a friendly, knowledgeable fitness assistant. 
    
    Your goal is to create a personalized fitness plan for the user.
    
    A fitness plan includes a workout plan and a meal plan.

    You will lead the conversation by asking the user questions and updating the fitness plan based on the results. 

    Create a welcome message based on the following guidelines:
    - Start with a concise explanation of the process.
    - Do not overwhelm the user with information.
    - Ask for the user's fitness goals but let them tell you whatever they want.

    Once the goal is determined, create the fitness plan, and then go over each section to help the user personalize it.
    
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



        

        

    def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
        """Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation."""
        if sex.lower() == "male":
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """Calculate Total Daily Energy Expenditure (TDEE) based on activity level."""
        activity_factors = {
            "sedentary": 1.2,
            "lightly active": 1.375,
            "moderately active": 1.55,
            "very active": 1.725,
            "super active": 1.9,
        }
        return bmr * activity_factors.get(activity_level.lower(), 1.2)

    def calculate_macros(calories: float, goal: str) -> dict:
        """Calculate macronutrient distribution based on fitness goal."""
        macro_ratios = {
            "cutting": {"protein": 0.40, "carbs": 0.35, "fats": 0.25},
            "maintenance": {"protein": 0.30, "carbs": 0.45, "fats": 0.25},
            "bulking": {"protein": 0.30, "carbs": 0.50, "fats": 0.20},
        }
        
        ratios = macro_ratios.get(goal.lower(), macro_ratios["maintenance"])
        protein_grams = (calories * ratios["protein"]) / 4
        fat_grams = (calories * ratios["fats"]) / 9
        carb_grams = (calories * ratios["carbs"]) / 4
        
        return {
            "calories": round(calories, 2),
            "protein_grams": round(protein_grams, 2),
            "fat_grams": round(fat_grams, 2),
            "carb_grams": round(carb_grams, 2)
        }

    def get_daily_calories(self, tdee: float, goal: str) -> float:
        """Adjust calories based on the goal."""
        adjustments = {
            "cutting": -500,
            "maintenance": 0,
            "bulking": 300,
        }
        return tdee + adjustments.get(goal.lower(), 0)

    def convert_weight_lbs_to_kg(self, weight_lbs: float) -> float:
        return weight_lbs * 0.453592

    def convert_height_in_to_cm(self, height_in: float) -> float:
        return height_in * 2.54

    def calculate_calories_and_macros(self):
        weight_kg = self.convert_weight_lbs_to_kg(self.intake_form.weight_lbs)
        height_cm = self.convert_height_in_to_cm(self.intake_form.height_in)
        bmr = self.calculate_bmr(weight_kg, height_cm, self.intake_form.age, self.intake_form.sex)
        tdee = self.calculate_tdee(bmr, self.intake_form.activity_level)
        daily_calories = self.get_daily_calories(tdee, self.intake_form.diet_phase)
        macros = self.calculate_macros(daily_calories, self.intake_form.diet_phase)
        return bmr, tdee, daily_calories, macros

    def search_usda_api(self, query: str):
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        headers = {"Content-Type": "application/json"}
        data = {"query": query}
        params = {"api_key": "DEMO_KEY"}
        
        response = requests.post(url, headers=headers, json=data, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def process_meal_plan(self, meal_plan):
        """
        Loops through each food in the meal plan, runs the food name through the search_usda_api function,
        and appends the results to the food object.

        Args:
            meal_plan (list): The meal plan JSON object.
            search_usda_api (function): Function to search USDA API for food data.

        Returns:
            list: Updated meal plan with USDA API results added to each food item.
        """
        for meal in meal_plan:
            for food in meal.get("foods", []):
                food_name = food.get("food_name", "")
                if food_name:
                    food["usda_data"] = self.search_usda_api(food_name)  # Append USDA API results

        return meal_plan



    