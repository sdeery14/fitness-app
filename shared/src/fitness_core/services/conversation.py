"""
Conversation management for the fitness agent.
"""
from typing import List, Dict, Union, Any
from ..agents.agent_models import ConversationMessage
from .exceptions import ConversationError


class ConversationManager:
    """Manages conversation history and state for the fitness agent"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.thread_id = "fitness_thread_001"  # Could be made dynamic per session
        
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history"""
        if not content or not content.strip():
            raise ConversationError("Cannot add empty message to conversation")
        
        self.conversation_history.append({"role": "user", "content": content.strip()})
        
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history"""
        if not content or not content.strip():
            raise ConversationError("Cannot add empty assistant message to conversation")
        
        self.conversation_history.append({"role": "assistant", "content": content.strip()})
        
    def get_input_for_agent(self) -> Union[str, List[Dict[str, str]]]:
        """Get the input format needed for the agent"""
        if not self.conversation_history:
            return "Hello"
        elif len(self.conversation_history) == 1:
            # First message - just send the content
            return self.conversation_history[0]["content"]
        else:
            # Multiple messages - send the full history
            return self.conversation_history
            
    def update_from_result(self, result: Any) -> None:
        """Update conversation history from agent result"""
        try:
            if hasattr(result, 'to_input_list'):
                # Update our history with the complete conversation from the agent
                self.conversation_history = result.to_input_list()
            else:
                # Extract content and add as assistant message
                content = self._extract_content_from_result(result)
                if content:
                    self.add_assistant_message(content)
        except Exception as e:
            raise ConversationError(f"Failed to update conversation from result: {str(e)}")
    
    def _extract_content_from_result(self, result: Any) -> str:
        """Extract content from various result formats"""
        if hasattr(result, 'final_output'):
            return str(result.final_output)
        elif hasattr(result, 'content'):
            return str(result.content)
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    
    def clear_history(self) -> None:
        """Clear the conversation history"""
        self.conversation_history = []
        
    def get_history_summary(self) -> str:
        """Get a summary of the conversation for debugging"""
        return f"Conversation has {len(self.conversation_history)} messages"
    
    def get_last_user_message(self) -> str:
        """Get the last user message"""
        for message in reversed(self.conversation_history):
            if message["role"] == "user":
                return message["content"]
        return ""
    
    def get_last_assistant_message(self) -> str:
        """Get the last assistant message"""
        for message in reversed(self.conversation_history):
            if message["role"] == "assistant":
                return message["content"]
        return ""
    
    def get_conversation_as_messages(self) -> List[ConversationMessage]:
        """Get conversation as structured ConversationMessage objects"""
        return [
            ConversationMessage(role=msg["role"], content=msg["content"]) 
            for msg in self.conversation_history
        ]
