"""
Example usage and demonstration of the fitness app.
"""
import asyncio
from agents import Runner

from fitness_core.agents import FitnessAgent
from fitness_core.utils import setup_logging, get_logger

# Setup logging for examples
setup_logging()
logger = get_logger(__name__)


def example_model_listing():
    """Example of listing available models."""
    print("🤖 Available AI Models (Anthropic + OpenAI):")
    print("=" * 60)
    
    # Show models by provider
    providers = FitnessAgent.get_models_by_provider()
    
    print("🔵 ANTHROPIC MODELS:")
    for name, full_id in providers["anthropic"].items():
        print(f"  • {name}: {full_id}")
        print(f"    {FitnessAgent.get_model_info(name)}")
        print()
    
    print("🟢 OPENAI MODELS:")
    for name, full_id in providers["openai"].items():
        print(f"  • {name}: {full_id}")
        print(f"    {FitnessAgent.get_model_info(name)}")
        print()
    
    print("🎯 RECOMMENDED MODELS (most likely to work):")
    recommended = FitnessAgent.get_recommended_models()
    for model in recommended:
        provider_icon = "🔵" if "claude" in model else "🟢" if any(x in model for x in ["gpt", "o1", "o3"]) else "⚪"
        print(f"  {provider_icon} {model}")


def example_agent_creation():
    """Example of creating agents with different models."""
    print("\n" + "="*60 + "\n")
    
    # Create agent with default model
    print("Creating agent with default model (gpt-4o-mini)...")
    agent = FitnessAgent()
    print(f"✅ Created agent:")
    print(f"   Model name: {agent.model_name}")
    print(f"   Provider: {agent.provider}")
    print(f"   Final model: {agent.final_model}")
    
    print("\n" + "="*60 + "\n")
    
    # Example with OpenAI model
    print("Creating agent with OpenAI model (gpt-4o-mini)...")
    try:
        openai_agent = FitnessAgent("gpt-4o-mini")
        print(f"✅ Created OpenAI agent:")
        print(f"   Model name: {openai_agent.model_name}")
        print(f"   Provider: {openai_agent.provider}")
        print(f"   Final model: {openai_agent.final_model}")
    except Exception as e:
        print(f"⚠️ Could not create OpenAI agent: {e}")
        print("   (This is normal if you don't have OPENAI_API_KEY set)")


async def example_agent_conversation():
    """Example of having a conversation with the agent."""
    print("\n" + "="*60)
    print("🗣️ EXAMPLE CONVERSATION")
    print("="*60 + "\n")
    
    try:
        # Create agent
        agent = FitnessAgent()
        print(f"Using model: {agent.model_name}")
        print()
        
        # Example conversation
        example_messages = [
            "Hello! I'm new to fitness and want to start working out.",
            "I want to build muscle but I only have 30 minutes a day, 3 times a week.",
            "Can you create a specific workout plan for me?"
        ]
        
        for i, message in enumerate(example_messages, 1):
            print(f"👤 User (Message {i}): {message}")
            
            try:
                # Run the agent
                result = Runner.run_sync(agent, message)
                response = result.final_output
                
                print(f"🤖 Assistant: {response}")
                print("\n" + "-"*40 + "\n")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print("   (This is expected if you don't have API keys configured)")
                break
                
    except Exception as e:
        print(f"❌ Could not create agent: {e}")
        print("   Make sure you have OPENAI_API_KEY or ANTHROPIC_API_KEY configured")


def run_examples():
    """Run all examples."""
    print("🏋️‍♀️ FITNESS APP EXAMPLES")
    print("="*60)
    
    # Model listing example
    example_model_listing()
    
    # Agent creation example  
    example_agent_creation()
    
    print("\n💡 To actually run the agents:")
    print("   - Set ANTHROPIC_API_KEY for Claude models")
    print("   - Set OPENAI_API_KEY for GPT models")
    print("   - Use Runner.run_sync(agent, 'your message') to chat")
    
    # Conversation example (commented out by default since it requires API keys)
    print("\n🔄 To see a conversation example, uncomment the following:")
    print("   # asyncio.run(example_agent_conversation())")
    
    # Uncomment this line to run the conversation example:
    # asyncio.run(example_agent_conversation())


if __name__ == "__main__":
    run_examples()
