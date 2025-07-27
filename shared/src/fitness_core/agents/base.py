"""
Main fitness agent implementation.
"""
from typing import Optional
from agents import Agent
from dotenv import load_dotenv

from .models import FitnessPlan, AgentConfig
from .providers import ModelProvider

load_dotenv()


class FitnessAgent(Agent):
    """
    A helpful assistant for general fitness guidance and handoffs to a plan-building agent.
    
    Supports multiple AI providers via LiteLLM (as of January 2025):
    
    Anthropic models:
    - Claude-4: claude-opus-4-20250514, claude-sonnet-4-20250514 (Premium)
    - Claude-3.7: claude-3-7-sonnet-20250219 (Extended thinking)
    - Claude-3.5: claude-3-5-sonnet-20241022 (latest), claude-3-5-sonnet-20240620 (stable), claude-3-5-haiku-20241022 (fast)
    - Claude-3: claude-3-haiku-20240307 (legacy but reliable)
    
    OpenAI models:
    - GPT-4o: gpt-4o, gpt-4o-mini (Vision + latest capabilities)
    - GPT-4: gpt-4-turbo (Legacy but stable)
    - GPT-3.5: gpt-3.5-turbo (Cost-effective)
    - Reasoning: o1-preview, o1-mini, o3-mini (Advanced reasoning)
    
    Note: Some older models may be deprecated. Always check provider documentation.
    """

    def __init__(self, model_name: Optional[str] = None, config: Optional[AgentConfig] = None):
        """
        Initialize the Fitness Agent with configurable AI model (Anthropic or OpenAI).
        
        Args:
            model_name: Name of the AI model to use. Can be a key from SUPPORTED_MODELS
                       or a full model identifier. Defaults to gpt-4o-mini if not specified.
                       Can also be set via AI_MODEL, ANTHROPIC_MODEL, or OPENAI_MODEL environment variables.
            config: Optional AgentConfig for additional configuration
        """
        # Resolve model name
        resolved_model_name = ModelProvider.resolve_model_name(model_name)
        final_model = ModelProvider.get_final_model_identifier(resolved_model_name)

        # Store the model information for debugging
        self.model_name = resolved_model_name
        self.full_model_name = ModelProvider.SUPPORTED_MODELS.get(resolved_model_name, resolved_model_name)
        self.final_model = final_model
        self.provider = ModelProvider.get_provider(resolved_model_name, self.full_model_name)
        self.config = config

        # Create fitness plan agent with model-specific configuration
        # Check if this is a Groq model that might struggle with structured output
        is_groq_model = "groq" in final_model.lower() or resolved_model_name in [
            "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-8b-8192", 
            "llama3-70b-8192", "gemma2-9b-it", 
            "mixtral-8x7b-32768", "qwen3-32b", "kimi-k2-instruct"
        ]
        
        if is_groq_model:
            # For Groq models, use simpler instructions without strict structured output
            fitness_plan_agent = Agent(
                name="Fitness Plan Assistant",
                instructions="""You are an expert fitness plan creation specialist. Create detailed fitness plans.

IMPORTANT: Respond directly with the fitness plan. Do not use <think> tags or internal reasoning. 

When responding, always provide:
1. A clear plan name
2. A complete training plan with specific exercises, sets, and reps
3. A detailed meal plan with specific foods and portions

Format your response clearly and include all three components above. Be specific and actionable.

Example response format:
**Plan Name:** Intermediate Muscle Building Program

**Training Plan:**
Day 1: Upper Body
- Bench Press: 4 sets × 8-10 reps
- Pull-ups: 3 sets × 6-8 reps
- Overhead Press: 3 sets × 10-12 reps

Day 2: Lower Body
- Squats: 4 sets × 8-10 reps
- Deadlifts: 3 sets × 5-6 reps

**Meal Plan:**
Breakfast: 3 whole eggs + 2 egg whites, 1 cup oatmeal, 1 banana
Lunch: 6oz chicken breast, 1.5 cups brown rice, mixed vegetables
Dinner: 6oz salmon, 1 cup quinoa, steamed broccoli

Now create a comprehensive fitness plan based on the user's request.""",
                model=final_model
                # Note: No output_type for Groq models to avoid structured output issues
            )
        else:
            # For OpenAI and Anthropic models, use structured output
            fitness_plan_agent = Agent(
                name="Fitness Plan Assistant",
                instructions="""You are an expert fitness plan creation specialist. Create detailed fitness plans with the following structure:

CRITICAL: You must respond with a valid FitnessPlan object containing exactly these three fields:
- name: A descriptive title for the plan
- training_plan: Complete workout program with exercises, sets, and reps  
- meal_plan: Detailed nutrition plan with specific foods and portions

TRAINING PLAN REQUIREMENTS:
- Organize by days (Day 1, Day 2, etc.) or muscle groups
- Include specific exercises with sets × reps (e.g., "Push-ups: 3 sets × 10 reps")
- Mention rest periods and progression tips
- Consider the user's fitness level and available equipment

MEAL PLAN REQUIREMENTS:
- Provide specific meals for breakfast, lunch, dinner, and snacks
- Include portion sizes and macronutrient balance
- Consider the user's goals (muscle gain, weight loss, etc.)
- Make it practical and achievable

IMPORTANT: Always fill in ALL three fields (name, training_plan, meal_plan) with detailed, specific content. Never leave any field empty or use placeholder text.

Example format:
- name: "Intermediate Muscle Building Program"
- training_plan: "Day 1: Upper Body\n- Bench Press: 4 sets × 8-10 reps\n- Pull-ups: 3 sets × 6-8 reps\n\nDay 2: Lower Body\n- Squats: 4 sets × 8-10 reps"
- meal_plan: "Breakfast: 3 whole eggs + 2 egg whites, 1 cup oatmeal, 1 banana\nLunch: 6oz chicken breast, 1.5 cups brown rice"

Now create a comprehensive fitness plan based on the user's request.""",
                model=final_model,
                output_type=FitnessPlan
            )

        # Initialize parent Agent with improved instructions
        super().__init__(
            name="Fitness Assistant",
            model=final_model,
            instructions="""You are a professional fitness and nutrition assistant with expertise in creating personalized fitness programs.

CORE CAPABILITIES:
- Fitness program design and workout planning
- Nutrition guidance and meal planning  
- Exercise technique and form advice
- Goal setting and progress tracking
- Injury prevention and modification strategies

WHEN TO TRANSFER TO FITNESS PLAN ASSISTANT:
Transfer immediately when users request:
- "Create a workout plan" or "design a program"
- "I need a fitness plan" or "help me with a routine"
- "Build a meal plan" or nutrition planning
- Any structured fitness or nutrition program creation

CONVERSATION GUIDELINES:
- Be encouraging and supportive
- Ask clarifying questions about fitness level, goals, and preferences
- Provide evidence-based advice
- Consider individual limitations and equipment availability
- Always prioritize safety and proper form

For detailed fitness plan creation, immediately transfer to the Fitness Plan Assistant who will create comprehensive, structured programs.""",
            handoffs=[fitness_plan_agent]
        )

    @classmethod
    def list_supported_models(cls) -> dict:
        """Return a dictionary of supported model names and their full identifiers."""
        return ModelProvider.SUPPORTED_MODELS.copy()

    @classmethod
    def get_model_info(cls, model_name: str) -> str:
        """Get information about a specific model."""
        return ModelProvider.get_model_info(model_name)

    @classmethod
    def get_recommended_models(cls) -> list:
        """Get a list of recommended models that are most likely to be available."""
        return ModelProvider.get_recommended_models()

    @classmethod 
    def get_models_by_provider(cls) -> dict:
        """Get models organized by provider."""
        return ModelProvider.get_models_by_provider()

    @classmethod
    def get_models_table_data(cls) -> list:
        """Get model data formatted for table display."""
        return ModelProvider.get_models_table_data()

    @classmethod
    def validate_model_name(cls, model_name: str) -> tuple[bool, str]:
        """
        Validate if a model name is in our supported list and provide helpful feedback.
        
        Returns:
            tuple: (is_valid, message)
        """
        return ModelProvider.validate_model_name(model_name)
