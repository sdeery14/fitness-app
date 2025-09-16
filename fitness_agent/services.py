"""
Services for the fitness agent including model providers and agent runner.
"""
import os
import asyncio
import logging
from typing import Union, List, Dict, Any, Generator, AsyncGenerator, Optional
from concurrent.futures import ThreadPoolExecutor
from agents import Runner

from .models import AgentConfig, FitnessPlan

logger = logging.getLogger(__name__)


class ModelProvider:
    """Manages AI model configurations and provider-specific logic."""

    # Available models - simplified list of most commonly used
    SUPPORTED_MODELS = {
        # OpenAI models (most reliable)
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini", 
        "gpt-4-turbo": "gpt-4-turbo",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
        
        # Anthropic models
        "claude-3.5-sonnet": "litellm/anthropic/claude-3-5-sonnet-20241022",
        "claude-3.5-haiku": "litellm/anthropic/claude-3-5-haiku-20241022",
        "claude-3-haiku": "litellm/anthropic/claude-3-haiku-20240307",
        
        # Groq models (fast and cost-effective)
        "llama-3.3-70b-versatile": "litellm/groq/llama-3.3-70b-versatile",
        "llama-3.1-8b-instant": "litellm/groq/llama-3.1-8b-instant",
        "mixtral-8x7b-32768": "litellm/groq/mixtral-8x7b-32768",
    }

    @classmethod
    def resolve_model_name(cls, model_name: Optional[str] = None) -> str:
        """Resolve model name from various sources."""
        if model_name and model_name in cls.SUPPORTED_MODELS:
            return model_name
            
        # Check environment variables
        for env_var in ["AI_MODEL", "ANTHROPIC_MODEL", "OPENAI_MODEL"]:
            env_model = os.getenv(env_var)
            if env_model and env_model in cls.SUPPORTED_MODELS:
                return env_model
                
        # Default to a reliable model
        return "llama-3.3-70b-versatile"

    @classmethod
    def get_final_model_identifier(cls, model_name: str) -> str:
        """Get the full model identifier."""
        return cls.SUPPORTED_MODELS.get(model_name, model_name)

    @classmethod
    def get_provider(cls, resolved_model_name: str, full_model_name: str) -> str:
        """Get the provider name for a model."""
        if "gpt-" in resolved_model_name or "o1-" in resolved_model_name:
            return "openai"
        elif "claude" in resolved_model_name:
            return "anthropic"
        elif "groq" in full_model_name or "llama" in resolved_model_name or "mixtral" in resolved_model_name:
            return "groq"
        else:
            return "unknown"


class FitnessAgentRunner:
    """Handles fitness agent execution with streaming and error management."""
    
    @staticmethod
    def run_agent_with_streaming_sync(
        agent, 
        agent_input: Union[str, List[Dict[str, str]]]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Run the agent with streaming support in a synchronous context (for Gradio)
        
        Args:
            agent: The fitness agent instance
            agent_input: Input for the agent (string for first message, list for conversation)
            
        Yields:
            Streaming response chunks from the agent with content and final result
        """
        try:
            logger.info(f"Running agent with streaming (sync). Input type: {type(agent_input)}")
            
            # Handle event loop creation for worker threads
            def _run_with_new_loop():
                """Create a new event loop and run the agent"""
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return Runner.run_sync(agent, agent_input)
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
            
            try:
                # Try direct call first (in case we're in main thread)
                final_result = Runner.run_sync(agent, agent_input)
            except RuntimeError as e:
                if "no current event loop" in str(e).lower() or "anyio worker thread" in str(e).lower():
                    # We're in a worker thread, create new event loop
                    final_result = _run_with_new_loop()
                else:
                    raise
            
            # Extract content and yield it
            content = FitnessAgentRunner._extract_content_from_result(final_result)
            
            # Simulate streaming by yielding the result
            yield {
                'type': 'final_result',
                'result': final_result,
                'content': content
            }
                
        except Exception as e:
            logger.error(f"Agent execution error: {str(e)}")
            # Return error as a final result-like object
            class ErrorResult:
                def __init__(self, content):
                    self.final_output = content
                    
                def to_input_list(self):
                    return [{"role": "assistant", "content": self.final_output}]
                    
            yield {
                'type': 'error',
                'result': ErrorResult(f"Sorry, I encountered an error while processing your request: {str(e)}"),
                'content': f"Sorry, I encountered an error while processing your request: {str(e)}"
            }

    @staticmethod
    async def run_agent_with_streaming(
        agent, 
        agent_input: Union[str, List[Dict[str, str]]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run the agent with streaming support using the correct Runner.run_streamed API
        
        Args:
            agent: The fitness agent instance
            agent_input: Input for the agent (string for first message, list for conversation)
            
        Yields:
            Streaming response chunks from the agent with content and final result
        """
        try:
            logger.info(f"Running agent with streaming. Input type: {type(agent_input)}")
            
            # Use the correct streaming API
            result = Runner.run_streamed(agent, agent_input)
            
            accumulated_content = ""
            final_result = None
            has_content = False
            
            try:
                async for chunk in result:
                    if hasattr(chunk, 'content') and chunk.content:
                        accumulated_content += chunk.content
                        has_content = True
                        yield {
                            'type': 'content',
                            'content': chunk.content,
                            'accumulated': accumulated_content
                        }
                    elif hasattr(chunk, 'final_output'):
                        final_result = chunk
                        break
                
                # If we didn't get content through streaming, try direct execution
                if not has_content:
                    logger.info("No streaming content received, falling back to direct execution")
                    final_result = Runner.run_sync(agent, agent_input)
                    accumulated_content = FitnessAgentRunner._extract_content_from_result(final_result)
            
            except Exception as streaming_error:
                logger.warning(f"Streaming failed: {streaming_error}, falling back to sync execution")
                final_result = Runner.run_sync(agent, agent_input)
                accumulated_content = FitnessAgentRunner._extract_content_from_result(final_result)
            
            # Get the final result if we haven't already from fallback
            if final_result is None:
                final_result = Runner.run_sync(agent, agent_input)
            
            # Yield the final result for conversation management
            yield {
                'type': 'final_result',
                'result': final_result,
                'content': accumulated_content
            }
                
        except Exception as e:
            logger.error(f"Agent streaming error: {str(e)}")
            # Return error as a final result-like object
            class ErrorResult:
                def __init__(self, content):
                    self.final_output = content
                    
                def to_input_list(self):
                    return [{"role": "assistant", "content": self.final_output}]
                    
            yield {
                'type': 'error',
                'result': ErrorResult(f"Sorry, I encountered an error while processing your request: {str(e)}"),
                'content': f"Sorry, I encountered an error while processing your request: {str(e)}"
            }

    @staticmethod
    def run_agent_safely_sync(
        agent, 
        agent_input: Union[str, List[Dict[str, str]]]
    ) -> Any:
        """
        Synchronous wrapper for the agent execution - with event loop handling
        
        Args:
            agent: The fitness agent instance
            agent_input: Input for the agent (string for first message, list for conversation)
            
        Returns:
            Final agent result
        """
        try:
            # Handle event loop creation for worker threads
            def _run_with_new_loop():
                """Create a new event loop and run the agent"""
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return Runner.run_sync(agent, agent_input)
                finally:
                    loop.close()
                    asyncio.set_event_loop(None)
            
            try:
                # Try direct call first (in case we're in main thread)
                return Runner.run_sync(agent, agent_input)
            except RuntimeError as e:
                if "no current event loop" in str(e).lower() or "anyio worker thread" in str(e).lower():
                    return _run_with_new_loop()
                else:
                    raise
                    
        except Exception as e:
            logger.error(f"Agent execution error: {str(e)}")
            
            # Create a mock result object for error cases
            class ErrorResult:
                def __init__(self, error_message):
                    self.final_output = error_message
                
                def to_input_list(self):
                    return [{"role": "assistant", "content": self.final_output}]
            
            return ErrorResult(f"Sorry, I encountered an error while processing your request: {str(e)}")

    @staticmethod
    def _extract_content_from_result(result: Any) -> str:
        """
        Extract content from agent response with proper error handling
        
        Args:
            result: Agent response object
            
        Returns:
            Formatted response string
        """
        try:
            if hasattr(result, 'final_output'):
                content = result.final_output
                
                # Check if this looks like a fitness plan
                if hasattr(content, 'name') and hasattr(content, 'training_plan'):
                    return f"Created fitness plan: {content.name}\n\n{content.description}"
                else:
                    return str(content)
            elif hasattr(result, 'content'):
                return str(result.content)
            elif isinstance(result, str):
                return result
            else:
                return str(result)
        except Exception as e:
            logger.error(f"Error extracting content from result: {str(e)}")
            return f"Sorry, I encountered an error while formatting the response: {str(e)}"


# Exception classes for better error handling
class AgentExecutionError(Exception):
    """Exception raised when agent execution fails."""
    pass


class ConfigurationError(Exception):
    """Exception raised when configuration is invalid."""
    pass
