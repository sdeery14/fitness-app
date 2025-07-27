"""
Test script to verify OpenAI model integration with the Fitness Agent.
This will help identify which models are available and test the integration.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fitness_agent import FitnessAgent

def test_openai_models():
    """Test OpenAI model availability and integration"""
    print("🧪 Testing OpenAI Model Integration")
    print("=" * 60)
    
    # Get OpenAI models specifically
    providers = FitnessAgent.get_models_by_provider()
    openai_models = providers["openai"]
    
    if not openai_models:
        print("❌ No OpenAI models found in configuration!")
        return
    
    print("📋 Configured OpenAI Models:")
    for name, full_id in openai_models.items():
        info = FitnessAgent.get_model_info(name)
        print(f"  • {name}: {full_id}")
        print(f"    {info}")
        print()
    
    # Test recommended OpenAI models
    recommended = FitnessAgent.get_recommended_models()
    openai_recommended = [m for m in recommended if any(x in m for x in ["gpt", "o1", "o3"])]
    
    print("🎯 Recommended OpenAI Models:")
    for model in openai_recommended:
        print(f"  🟢 {model}")
    
    print("\n" + "=" * 60)
    
    # Test creating agents with different OpenAI models
    test_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "o1-mini"]
    
    for model in test_models:
        if model in openai_models:
            print(f"🚀 Testing agent creation with {model}...")
            try:
                agent = FitnessAgent(model)
                print(f"✅ Successfully created agent:")
                print(f"   Model name: {agent.model_name}")
                print(f"   Provider: {agent.provider}")
                print(f"   Final model: {agent.final_model}")
                print(f"   Expected format: {openai_models[model]}")
                
                # Verify the model format is correct
                if agent.provider == "openai":
                    print("✅ Correctly identified as OpenAI model")
                else:
                    print(f"⚠️ Provider detection issue: expected 'openai', got '{agent.provider}'")
                    
            except Exception as e:
                print(f"❌ Error creating agent with {model}: {str(e)}")
                if "api" in str(e).lower() or "key" in str(e).lower():
                    print("   💡 This might be due to missing OPENAI_API_KEY")
                
            print()

def test_model_detection():
    """Test the model provider detection logic"""
    print("🔍 Testing Model Provider Detection")
    print("=" * 60)
    
    test_cases = [
        ("gpt-4o", "openai"),
        ("gpt-4o-mini", "openai"),
        ("gpt-3.5-turbo", "openai"), 
        ("o1-preview", "openai"),
        ("o3-mini", "openai"),
        ("claude-3.5-haiku", "anthropic"),
        ("claude-4-opus", "anthropic"),
        ("openai/gpt-4o", "openai"),
    ]
    
    for model, expected_provider in test_cases:
        try:
            agent = FitnessAgent(model)
            actual_provider = agent.provider
            status = "✅" if actual_provider == expected_provider else "❌"
            print(f"{status} {model}: expected {expected_provider}, got {actual_provider}")
        except Exception as e:
            print(f"❌ {model}: Error - {str(e)}")

def check_environment():
    """Check environment setup for OpenAI"""
    print("\n🔧 Environment Check")
    print("=" * 60)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    ai_model = os.getenv("AI_MODEL")
    
    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"ANTHROPIC_API_KEY: {'✅ Set' if anthropic_key else '❌ Not set'}")
    print(f"AI_MODEL: {ai_model if ai_model else 'Not set (will use default)'}")
    
    if not openai_key and not anthropic_key:
        print("\n⚠️ No API keys found! Set at least one in your .env file:")
        print("   OPENAI_API_KEY=your_openai_key_here")
        print("   ANTHROPIC_API_KEY=your_anthropic_key_here")
    elif openai_key and not anthropic_key:
        print("\n🟢 OpenAI setup detected - you can use GPT models")
    elif anthropic_key and not openai_key:
        print("\n🔵 Anthropic setup detected - you can use Claude models")
    else:
        print("\n🎉 Both providers configured - you can use all models!")

def show_usage_examples():
    """Show examples of how to use OpenAI models"""
    print("\n📚 Usage Examples")
    print("=" * 60)
    
    examples = [
        ("Basic OpenAI", "FitnessAgent('gpt-4o-mini')"),
        ("Latest GPT-4o", "FitnessAgent('gpt-4o')"),
        ("Cost-effective", "FitnessAgent('gpt-3.5-turbo')"),
        ("Reasoning", "FitnessAgent('o1-mini')"),
        ("Environment var", "os.environ['AI_MODEL'] = 'gpt-4o'; FitnessAgent()"),
        ("Via prefix", "FitnessAgent('openai/gpt-4o-mini')"),
    ]
    
    for name, code in examples:
        print(f"# {name}")
        print(f"agent = {code}")
        print()

if __name__ == "__main__":
    check_environment()
    test_openai_models()
    test_model_detection()
    show_usage_examples()
    
    print("=" * 60)
    print("🎯 Summary:")
    print("  • OpenAI models are now supported alongside Anthropic")
    print("  • Use gpt-4o-mini for balanced performance")
    print("  • Use claude-3.5-haiku for fast responses")
    print("  • Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY in .env")
    print("  • Launch with: python app.py")
