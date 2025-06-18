"""
Context Manager for SmolD
Manages conversation history and token counting to maintain context within limits.
"""

import tiktoken
from typing import List, Dict, Any, Optional
from collections import deque


class ConversationHistory:
    """Manages conversation history with token counting and size limits."""
    
    def __init__(self, max_interactions: int = 8, max_tokens: int = 100000):
        """
        Initialize conversation history manager.
        
        Args:
            max_interactions: Maximum number of user-assistant interaction pairs to keep
            max_tokens: Maximum total tokens allowed for conversation history
        """
        self.max_interactions = max_interactions
        self.max_tokens = max_tokens
        self.history = deque(maxlen=max_interactions)
        
        # Track token counts for each interaction for efficient trimming
        self.interaction_token_counts = deque(maxlen=max_interactions)
        self.total_tokens = 0
        
        # Initialize tiktoken for DeepSeek (use gpt-4o-mini encoding as fallback)
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        except KeyError:
            print("Warning: Using o200k_base encoding for token counting")
            self.tokenizer = tiktoken.get_encoding("o200k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text using tiktoken."""
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            print(f"WARNING: Tiktoken fallback active! Token counting may be inaccurate. Error: {e}")
            return len(text) // 4  # Rough fallback estimate
    
    def count_messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Count tokens for a list of messages in the format expected by DeepSeek/OpenAI.
        Based on OpenAI's token counting specifications.
        """
        total = 0
        tokens_per_message = 3  # Standard overhead per message
        tokens_per_name = 1     # Overhead for name field
        
        for message in messages:
            total += tokens_per_message
            for key, value in message.items():
                if isinstance(value, str):
                    total += self.count_tokens(value)
                elif isinstance(value, list):
                    # Handle content arrays
                    for item in value:
                        if isinstance(item, dict) and 'text' in item:
                            total += self.count_tokens(item['text'])
                if key == "name":
                    total += tokens_per_name
        
        total += 3  # Assistant reply preamble
        return total
    
    def add_interaction(self, user_query: str, assistant_response: str, system_prompt_tokens: int = 0):
        """
        Add a user-assistant interaction pair to the history.
        
        Args:
            user_query: The user's query/input
            assistant_response: The assistant's response
            system_prompt_tokens: Token count of system prompt for proper trimming
        """
        interaction = {
            "user": user_query,
            "assistant": assistant_response
        }
        
        # Calculate token count for this interaction (2 messages: user + assistant)
        user_tokens = self.count_tokens(user_query) + 3  # message overhead
        assistant_tokens = self.count_tokens(assistant_response) + 3  # message overhead
        interaction_tokens = user_tokens + assistant_tokens
        
        # If history is at max capacity and we're adding a new item,
        # we need to remove the oldest token count first
        if len(self.history) == self.max_interactions:
            if self.interaction_token_counts:
                oldest_tokens = self.interaction_token_counts[0]
                self.total_tokens -= oldest_tokens
        
        # Add to history (deque automatically handles max_interactions limit)
        self.history.append(interaction)
        self.interaction_token_counts.append(interaction_tokens)
        self.total_tokens += interaction_tokens
        
        # Check token limits and trim if necessary, accounting for system prompt
        self._trim_to_token_limit(system_prompt_tokens)
    
    def _trim_to_token_limit(self, system_prompt_tokens: int = 0):
        """Trim history to stay within token limits, removing oldest interactions."""
        # The check now includes the system prompt's token count.
        while len(self.history) > 0 and (self.total_tokens + system_prompt_tokens) > self.max_tokens:
            # Remove oldest interaction and its token count
            self.history.popleft()
            if self.interaction_token_counts:
                removed_tokens = self.interaction_token_counts.popleft()
                self.total_tokens -= removed_tokens
    
    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """
        Get conversation history formatted as messages for LLM.
        
        Returns:
            List of message dictionaries in the format: [{"role": "user", "content": "..."}, ...]
        """
        messages = []
        
        for interaction in self.history:
            # Add user message
            messages.append({
                "role": "user",
                "content": interaction["user"]
            })
            
            # Add assistant message
            messages.append({
                "role": "assistant", 
                "content": interaction["assistant"]
            })
        
        return messages
    
    def get_context_summary(self) -> str:
        """Get a summary of the current conversation context."""
        if not self.history:
            return "No conversation history"
        
        return (
            f"Conversation history: {len(self.history)} interactions, "
            f"~{self.total_tokens:,} tokens"
        )
    
    def clear(self):
        """Clear all conversation history."""
        self.history.clear()
        self.interaction_token_counts.clear()
        self.total_tokens = 0
    
    def is_empty(self) -> bool:
        """Check if conversation history is empty."""
        return len(self.history) == 0


class ContextManager:
    """Main context manager that combines system prompt and conversation history."""
    
    def __init__(self, max_interactions: int = 8, max_context_tokens: int = 100000):
        """
        Initialize context manager.
        
        Args:
            max_interactions: Maximum conversation interactions to keep
            max_context_tokens: Maximum total tokens for entire context
        """
        self.conversation = ConversationHistory(max_interactions, max_context_tokens)
        self.system_prompt = ""
        self.max_context_tokens = max_context_tokens
    
    def set_system_prompt(self, prompt: str):
        """Set or update the system prompt."""
        self.system_prompt = prompt
    
    def add_interaction(self, user_query: str, assistant_response: str):
        """Add a conversation interaction."""
        # Calculate system prompt tokens for proper trimming
        system_tokens = self.conversation.count_tokens(self.system_prompt) if self.system_prompt else 0
        self.conversation.add_interaction(user_query, assistant_response, system_tokens)
    
    def get_full_context_for_llm(self, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get complete context (system + history) formatted for LLM.
        
        Args:
            include_system: Whether to include system prompt as first message
            
        Returns:
            List of messages ready for LLM API call
        """
        messages = []
        
        # Add system prompt if requested and available
        if include_system and self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # Add conversation history
        messages.extend(self.conversation.get_messages_for_llm())
        
        return messages
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get information about current context state."""
        messages = self.get_full_context_for_llm()
        total_tokens = self.conversation.count_messages_tokens(messages)
        system_tokens = self.conversation.count_tokens(self.system_prompt) if self.system_prompt else 0
        
        return {
            "total_messages": len(messages),
            "conversation_interactions": len(self.conversation.history),
            "total_tokens": total_tokens,
            "system_prompt_tokens": system_tokens,
            "conversation_tokens": total_tokens - system_tokens,
            "under_limit": total_tokens <= self.max_context_tokens
        }
    
    def clear_conversation(self):
        """Clear conversation history but keep system prompt."""
        self.conversation.clear()
    
    def refresh_with_system_prompt(self, new_system_prompt: str):
        """Update system prompt and check if context still fits within limits."""
        self.set_system_prompt(new_system_prompt)
        
        # Calculate the new system prompt's token count
        system_tokens = self.conversation.count_tokens(self.system_prompt)
        
        # Now, trim the conversation history if the *combined* context is too large.
        if (self.conversation.total_tokens + system_tokens) > self.max_context_tokens:
            print(f"Context exceeds limit, trimming history...")
            # Pass the system prompt token count to the trimming function.
            self.conversation._trim_to_token_limit(system_prompt_tokens=system_tokens)