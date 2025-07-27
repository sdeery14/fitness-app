"""
Example usage of the Fitness Agent with different AI providers and models.

Run this script to see different ways to use the FitnessAgent with both
Anthropic Claude and OpenAI GPT models.
"""

from fitness_agent import FitnessAgent
from agents import Runner
import os

def basic_example():
    """Example using the default model."""
    print("=== Basic Usage (Default Model) ===")
    agent = FitnessAgent()
    print(f"Using model: {agent.model_name}")
    print(f"Provider: {agent.provider}")
    print(f"Final model path: {agent.final_model}")
    
    # In a real scenario, you would run this:
    # result = Runner.run_sync(agent, "Create a beginner fitness plan.")
    # print(f"Result: {result.final_output}")
    print("✅ Agent created successfully!")
    print()

def anthropic_example():
    """Example using Anthropic Claude models."""
    print("=== Anthropic Claude Example ===")
    agent = FitnessAgent("claude-3.5-sonnet")
    print(f"Using model: {agent.model_name}")
    print(f"Provider: {agent.provider}")
    print(f"Final model path: {agent.final_model}")
    print("✅ Anthropic agent created successfully!")
    print()

def openai_example():
    """Example using OpenAI GPT models."""
    print("=== OpenAI GPT Example ===")
    try:
        agent = FitnessAgent("gpt-4o-mini")
        print(f"Using model: {agent.model_name}")
        print(f"Provider: {agent.provider}")
        print(f"Final model path: {agent.final_model}")
        print("✅ OpenAI agent created successfully!")
    except Exception as e:
        print(f"⚠️ Could not create OpenAI agent: {e}")
        print("   (Make sure you have OPENAI_API_KEY set in your .env file)")
    print()

def reasoning_model_example():
    """Example using OpenAI reasoning models (o1/o3 series)."""
    print("=== OpenAI Reasoning Model Example ===")
    try:
        agent = FitnessAgent("o1-mini")
        print(f"Using model: {agent.model_name}")
        print(f"Provider: {agent.provider}")
        print(f"Final model path: {agent.final_model}")
        print("✅ Reasoning model agent created successfully!")
        print("💡 o1-mini is great for complex fitness planning and analysis")
    except Exception as e:
        print(f"⚠️ Could not create reasoning model agent: {e}")
        print("   (o1 models may require special access)")
    print()

def environment_variable_example():
    """Example using environment variable."""
    print("=== Using Environment Variable ===")
    # Set environment variable (in practice, this would be in your .env file)
    os.environ["AI_MODEL"] = "gpt-4o"
    
    agent = FitnessAgent()  # Will use the model from environment variable
    print(f"Using model: {agent.model_name}")
    print(f"Provider: {agent.provider}")
    print("✅ Agent created with environment variable!")
    print()

def list_available_models():
    """Display all available models organized by provider."""
    print("=== Available Models by Provider ===")
    
    providers = FitnessAgent.get_models_by_provider()
    
    print("🔵 ANTHROPIC MODELS:")
    for model in providers["anthropic"]:
        full_name = providers["anthropic"][model]
        info = FitnessAgent.get_model_info(model)
        print(f"  • {model}")
        print(f"    Path: {full_name}")
        print(f"    Info: {info}")
        print()
    
    print("🟢 OPENAI MODELS:")
    for model in providers["openai"]:
        full_name = providers["openai"][model]
        info = FitnessAgent.get_model_info(model)
        print(f"  • {model}")
        print(f"    Path: {full_name}")
        print(f"    Info: {info}")
        print()
    
    print("🎯 RECOMMENDED MODELS:")
    for model in FitnessAgent.get_recommended_models():
        provider_icon = "🔵" if "claude" in model else "🟢" if any(x in model for x in ["gpt", "o1", "o3"]) else "⚪"
        print(f"  {provider_icon} {model}")
    print()

def compare_providers():
    """Show comparison between providers."""
    print("=== Provider Comparison ===")
    print("🔵 ANTHROPIC CLAUDE:")
    print("  ✅ Excellent for detailed analysis and safety")
    print("  ✅ Great context understanding")
    print("  ✅ Strong reasoning capabilities")
    print("  ❓ Requires ANTHROPIC_API_KEY")
    print()
    
    print("🟢 OPENAI GPT:")
    print("  ✅ Familiar and widely used")
    print("  ✅ Good general performance")
    print("  ✅ Vision capabilities (GPT-4o)")
    print("  ✅ Reasoning models (o1/o3 series)")
    print("  ❓ Requires OPENAI_API_KEY")
    print()

if __name__ == "__main__":
    print("🤖 Fitness Agent Examples - Multi-Provider Support")
    print("=" * 60)
    
    list_available_models()
    compare_providers()
    basic_example()
    anthropic_example()
    openai_example()
    reasoning_model_example()
    environment_variable_example()
    
    print("=" * 60)
    print("✅ All examples completed!")
    print()
    print("💡 To actually run the agents:")
    print("  1. Copy .env.example to .env")
    print("  2. Add your OPENAI_API_KEY and/or ANTHROPIC_API_KEY")
    print("  3. Uncomment the Runner.run_sync lines in the examples")
    print("  4. Run: python fitness_agent/examples.py")
    print()
    print("🚀 Or launch the web interface: python fitness_agent/app.py")
