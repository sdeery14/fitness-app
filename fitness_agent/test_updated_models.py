"""
Test script to verify the updated Anthropic models work correctly.
This will help identify which models are actually available in your API.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fitness_agent import FitnessAgent

def test_model_availability():
    """Test which models are actually available"""
    print("🧪 Testing Updated Anthropic Models")
    print("=" * 60)
    
    # Get all supported models
    models = FitnessAgent.list_supported_models()
    
    print("📋 Currently Configured Models:")
    for name, full_id in models.items():
        info = FitnessAgent.get_model_info(name)
        print(f"  • {name}: {full_id}")
        print(f"    {info}")
        print()
    
    print("🎯 Recommended Models (most likely to work):")
    recommended = FitnessAgent.get_recommended_models()
    for model in recommended:
        print(f"  • {model}: {models.get(model, 'Not found')}")
    
    print("\n" + "=" * 60)
    print("💡 Notes:")
    print("  • Claude-4 models may require special API access")
    print("  • Claude-3.5-haiku is the new default (faster than claude-3-haiku)")
    print("  • Deprecated models (claude-3-opus, claude-3-sonnet, claude-2.x) have been removed")
    print("  • Always check Anthropic's documentation for the latest available models")
    
    # Test creating an agent with the new default
    print(f"\n🚀 Testing agent creation with new default (claude-3.5-haiku)...")
    try:
        agent = FitnessAgent()
        print(f"✅ Successfully created agent with model: {agent.model_name}")
        print(f"   Full model path: {agent.litellm_model}")
    except Exception as e:
        print(f"❌ Error creating agent: {str(e)}")
        print("   Try using a different model or check your API key")

if __name__ == "__main__":
    test_model_availability()
