"""
Basic tests for the fitness agent.
"""
import unittest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from fitness_app.agents import FitnessAgent, ModelProvider


class TestFitnessAgent(unittest.TestCase):
    """Test cases for FitnessAgent."""
    
    def test_model_listing(self):
        """Test that models can be listed."""
        models = FitnessAgent.list_supported_models()
        self.assertIsInstance(models, dict)
        self.assertGreater(len(models), 0)
        
        # Test that we have both OpenAI and Anthropic models
        model_names = list(models.keys())
        has_openai = any("gpt" in name or "o1" in name or "o3" in name for name in model_names)
        has_anthropic = any("claude" in name for name in model_names)
        
        self.assertTrue(has_openai, "Should have OpenAI models")
        self.assertTrue(has_anthropic, "Should have Anthropic models")
    
    def test_model_validation(self):
        """Test model name validation."""
        # Test valid model
        is_valid, message = FitnessAgent.validate_model_name("gpt-4o-mini")
        self.assertTrue(is_valid)
        
        # Test invalid model
        is_valid, message = FitnessAgent.validate_model_name("invalid-model")
        self.assertFalse(is_valid)
        self.assertIn("not found", message.lower())
    
    def test_model_info(self):
        """Test getting model information."""
        info = FitnessAgent.get_model_info("gpt-4o-mini")
        self.assertIsInstance(info, str)
        self.assertGreater(len(info), 0)
        
    def test_recommended_models(self):
        """Test getting recommended models."""
        recommended = FitnessAgent.get_recommended_models()
        self.assertIsInstance(recommended, list)
        self.assertGreater(len(recommended), 0)
        
        # Test that recommended models are valid
        for model in recommended:
            is_valid, _ = FitnessAgent.validate_model_name(model)
            self.assertTrue(is_valid, f"Recommended model {model} should be valid")


class TestModelProvider(unittest.TestCase):
    """Test cases for ModelProvider."""
    
    def test_provider_detection(self):
        """Test provider detection logic."""
        # OpenAI models
        self.assertTrue(ModelProvider.is_openai_model("gpt-4o", "gpt-4o"))
        self.assertTrue(ModelProvider.is_openai_model("o1-mini", "o1-mini"))
        
        # Anthropic models (should return False for is_openai_model)
        self.assertFalse(ModelProvider.is_openai_model("claude-3.5-sonnet", "litellm/anthropic/claude-3-5-sonnet-20240620"))
    
    def test_model_resolution(self):
        """Test model name resolution."""
        resolved = ModelProvider.resolve_model_name("gpt-4o-mini")
        self.assertEqual(resolved, "gpt-4o-mini")
        
        # Test with None (should return default)
        resolved = ModelProvider.resolve_model_name(None)
        self.assertIsInstance(resolved, str)
        self.assertGreater(len(resolved), 0)


if __name__ == "__main__":
    unittest.main()
