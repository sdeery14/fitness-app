from openai import OpenAI
from dotenv import load_dotenv
from intake_form import IntakeForm
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
    
    Your goal is to help users achieve their fitness goals by providing clear, 
    actionable advice about exercise, nutrition, and healthy habits.

    You also help users create a fitness plan, which includes a workout plan and a meal plan.

    In order to do this, you will need to ask the user for their fitness details,
    and help them develop a personalized workout plan and meal plan.

    Fitness details include fitness goals, current activity level, desired activity level, height, weight, body fat percentage, 
    age, sex, activity level.
    
    Do not discuss topics unrelated to fitness, health, nutrition, or exercise. 
    
    If a user asks about something off-topic, politely steer the conversation back to their fitness goals.
    """
    }

    tools = [
        {
            "type": "function",
            "function": {
                "name": "update_intake_form",
                "description": "Fills the intake form with any details provided in the user prompt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intake_form": {"type": "string", "description": "The workout plan to be created."}
                    },
                    "required": ["workout_plan"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_fitness_plan",
                "description": "Creates a workout plan based on the user's fitness goals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workout_plan": {"type": "string", "description": "The workout plan to be created."}
                    },
                    "required": ["workout_plan"],
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
        self.intake_form = IntakeForm()
        self.system_prompt = system_prompt
        self.welcome_message = self.process_chat([self.system_prompt])
        self.chat_history_full = []
        self.chat_history_display = []
        self.fitness_plan = {}

    def generate_welcome_message(self):
        """
        Uses OpenAI to generate a personalized greeting and first question for the user.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[self.system_prompt]
        )

        greeting_message = response.choices[0].message.content.strip()

        self.welcome_message = {"role": "assistant", "content": greeting_message}
        self.chat_history_full.append(self.welcome_message)
        self.chat_history_display.append(self.welcome_message)

        return self.chat_history_display



    def generate_fitness_plan(self, height_in, weight_lbs, age, sex, activity_level, goals, diet_phase):

        # Add thinking message to display chat
        self.chat_history_display.append({"role": "assistant", "content": "Gathering intake form.📂", "metadata": {"title": "Thinking...🧠"}})
        yield self.chat_history_display, None

        # Update intake form
        self.intake_form.update_values({
            "height_in": height_in,
            "weight_lbs": weight_lbs,
            "age": age,
            "sex": sex,
            "activity_level": activity_level,
            "goals": goals,
            "diet_phase": diet_phase
        })

        # Add intake form data to full chat
        self.chat_history_full.append({"role": "system", "content": f"Here is the user's intake data: {self.intake_form.model_dump()}"})
    
        # Add to thinking message in display chat
        self.chat_history_display[-1]["content"] += "\nIntake form updated.✔️\nGenerating fitness plan.✏️"
        yield self.chat_history_display, None
        
        # Calculate BMR, TDEE, daily calories, and macros
        #bmr, tdee, daily_calories, macros = self.calculate_calories_and_macros()

        # Stream the OpenAI API generated Fitness Plan
        with client.beta.chat.completions.stream(
            model="gpt-4o",
            messages=self.chat_history_full,
            response_format=FitnessPlan,
        ) as stream:
            for event in stream:
                if event.type == "content.delta":
                    if event.parsed is not None:
                        # Yield the parsed data as it comes up
                        yield self.chat_history_display, event.parsed
                elif event.type == "content.done":
                    print("content.done")
                elif event.type == "error":
                    print("Error in stream:", event.error)

        final_completion = stream.get_final_completion()

        # Add to thinking message in display chat
        self.chat_history_display[-1]["content"] += "\nFitness Plan generated.✔️"
        yield self.chat_history_display, final_completion.choices[0].message.parsed.model_dump()

        final_completion.choices[0].message.parsed

    def add_message_to_chat(self, user_message):        
        self.chat_history_full.append({"role": "user", "content": user_message})
        self.chat_history_display.append({"role": "user", "content": user_message})
        return "", self.chat_history_display

    def call_function(self, tool_name, args):
        if tool_name == "create_fitness_plan":
            return self.create_fitness_plan(**args)

    def process_chat(self, history):

        # Start streaming the OpenAI API response
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=history,
            #tools=self.tools,
            stream=True
        )

        # Initialize the assistant message in the history
        history.append({"role": "assistant", "content": ""})

        for chunk in stream:

            # Handle streaming function call response
            if chunk.choices[0].delta.tool_calls is not None:
                
                # Add metadata to the last message in history if not present
                if "metadata" not in history[-1]:
                    history[-1]["metadata"] = {"title": "Thinking...\n"}
                
                # Yield the current state of history
                yield history, None

                final_tool_calls = {}
                
                # Collect all tool calls from the response
                for tool_call in chunk.choices[0].delta.tool_calls or []:
                    index = tool_call.index
                    if index not in final_tool_calls:
                        final_tool_calls[index] = tool_call
                    final_tool_calls[index].function.arguments += tool_call.function.arguments
                    history[-1]["content"] += str(tool_call.function.arguments)
                    print(history[-1])

                # Yield the current state of history
                yield history, None

                # Execute each tool call and update the history with the results
                for tool_call in final_tool_calls.values():
                    tool_name = tool_call.function.name
                    if tool_call.function.arguments:
                        args = json.loads(tool_call.function.arguments)
                        print(args)
                        result = self.call_function(tool_name, args)
                        print(result)
                        history[-1]["content"] += f"\nFunction {tool_name} results: {str(result)}"
                yield history, result
                
                # Initialize a new assistant message in the history
                history.append({"role": "assistant", "content": ""})
                
                # Start a second stream to continue the conversation
                second_stream = self.stream_openai_api(history)
                if second_stream is None:
                    return

                # Initialize another assistant message in the history
                history.append({"role": "assistant", "content": ""})
                for chunk in second_stream:
                    history[-1]["content"] += chunk.choices[0].delta.content or ""
                    yield history, None

            # Handle regular content response
            elif chunk.choices[0].delta.content is not None:
                history[-1]["content"] += chunk.choices[0].delta.content or ""
                yield history, None

    
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



    