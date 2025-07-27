"""
Example usage of the Fitness Agent with different Anthropic models.

Run this script to see different ways to use the FitnessAgent.
"""

from fitness_agent import FitnessAgent
from agents import Runner
import os

def basic_example():
    """Example using the default model."""
    print("=== Basic Usage (Default Model) ===")
    agent = FitnessAgent()
    print(f"Using model: {agent.model_name}")
    
    # In a real scenario, you would run this:
    # result = Runner.run_sync(agent, "Create a beginner fitness plan.")
    # print(f"Result: {result.final_output}")
    print("Agent created successfully!")
    print()

def specific_model_example():
    """Example using a specific model."""
    print("=== Using Specific Model ===")
    agent = FitnessAgent("claude-3.5-sonnet")
    print(f"Using model: {agent.model_name}")
    print("Agent created successfully!")
    print()

def environment_variable_example():
    """Example using environment variable."""
    print("=== Using Environment Variable ===")
    # Set environment variable (in practice, this would be in your .env file)
    os.environ["ANTHROPIC_MODEL"] = "claude-3.7-sonnet"
    
    agent = FitnessAgent()  # Will use the model from environment variable
    print(f"Using model: {agent.model_name}")
    print("Agent created successfully!")
    print()

def list_available_models():
    """Display all available models."""
    print("=== Available Models ===")
    models = FitnessAgent.list_supported_models()
    
    print("Recommended models:")
    for model in FitnessAgent.get_recommended_models():
        full_name = models.get(model, "Not found")
        info = FitnessAgent.get_model_info(model)
        print(f"  • {model}: {full_name}")
        print(f"    {info}")
        print()
    
    print("All available models:")
    for name, full_id in models.items():
        print(f"  • {name}: {full_id}")
    print()

if __name__ == "__main__":
    print("🤖 Fitness Agent Examples")
    print("=" * 50)
    
    list_available_models()
    basic_example()
    specific_model_example()
    environment_variable_example()
    
    print("✅ All examples completed!")
    print("\nTo actually run the agent, uncomment the Runner.run_sync lines")
    print("and make sure you have your ANTHROPIC_API_KEY set in .env")
