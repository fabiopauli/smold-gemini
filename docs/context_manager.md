# Overview

The `smold/context_manager.py` file provides classes for managing the conversational context of the SmolD agent. This includes storing the history of user-assistant interactions, counting tokens to stay within the language model's limits, and combining the conversation history with a system prompt. The primary goal is to provide the LLM with relevant context for generating coherent and informed responses while preventing context overflow.

# Key Components

-   **`ConversationHistory` class**:
    *   Manages a deque (double-ended queue) of user-assistant interaction pairs.
    *   **Token Counting**: Uses the `tiktoken` library (specifically `gpt-4o-mini` encoding as a proxy for Gemini models) to count tokens in text and messages. It includes a fallback mechanism if `tiktoken` fails.
    *   **Limits**: Enforces limits on the number of interactions (`max_interactions`) and total tokens (`max_tokens`) in the conversation history.
    *   **Trimming**: Automatically trims the oldest interactions from the history if either the interaction count or token count exceeds the defined limits. This trimming considers the token count of the system prompt to ensure the total context (system prompt + conversation) fits.
    *   **Methods**:
        *   `add_interaction(user_query, assistant_response, system_prompt_tokens)`: Adds a new interaction and its token count, then trims if necessary.
        *   `get_messages_for_llm()`: Formats the history into a list of message dictionaries suitable for LLM API calls (e.g., `[{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]`).
        *   `clear()`: Empties the conversation history.
        *   `is_empty()`: Checks if the history is empty.
        *   `get_context_summary()`: Provides a brief string summary of the history state.
        *   `count_tokens(text)`: Counts tokens in a single string.
        *   `count_messages_tokens(messages)`: Counts tokens for a list of LLM message objects, accounting for message structure overhead.

-   **`ContextManager` class**:
    *   Orchestrates the overall context by combining a system prompt with the conversation history.
    *   Holds an instance of `ConversationHistory`.
    *   **System Prompt**: Stores and allows updating of the system prompt string.
    *   **Methods**:
        *   `set_system_prompt(prompt)`: Sets or updates the system prompt.
        *   `add_interaction(user_query, assistant_response)`: Adds an interaction to its `ConversationHistory` instance, ensuring the system prompt's token count is considered for trimming.
        *   `get_full_context_for_llm(include_system=True)`: Returns a list of messages for the LLM, optionally prepending the system prompt to the conversation history.
        *   `get_context_info()`: Provides a dictionary with details about the current context state, including total messages, interaction count, token counts (total, system, conversation), and whether the context is within the token limit.
        *   `clear_conversation()`: Clears only the conversation history, leaving the system prompt intact.
        *   `refresh_with_system_prompt(new_system_prompt)`: Updates the system prompt and re-evaluates/trims the conversation history to ensure the combined context fits within limits. This is useful when the system prompt changes (e.g., due to a change in working directory).

# Important Variables/Constants

-   **`max_interactions` (in `ConversationHistory` and `ContextManager`)**: The maximum number of user-assistant interaction pairs to retain in the history.
-   **`max_tokens` (in `ConversationHistory`) / `max_context_tokens` (in `ContextManager`)**: The maximum total number of tokens allowed for the conversation history (or the entire context including the system prompt for `ContextManager`).
-   **`tokenizer` (in `ConversationHistory`)**: An instance of `tiktoken.Encoding` used for tokenizing text. It defaults to `gpt-4o-mini`'s encoding.

# Usage Examples

This module is primarily used by the `SmolDAgent` to manage its conversational memory.

```python
# Example of direct usage (typically done within SmolDAgent)
from smold.context_manager import ContextManager

# Initialize with limits
context_mgr = ContextManager(max_interactions=5, max_context_tokens=4000)

# Set a system prompt
system_prompt = "You are a helpful assistant."
context_mgr.set_system_prompt(system_prompt)

# Add some interactions
context_mgr.add_interaction("Hello", "Hi there!")
context_mgr.add_interaction("How are you?", "I'm doing well, thank you for asking!")

# Get context for LLM
llm_messages = context_mgr.get_full_context_for_llm()
# llm_messages would look like:
# [
#   {'role': 'system', 'content': 'You are a helpful assistant.'},
#   {'role': 'user', 'content': 'Hello'},
#   {'role': 'assistant', 'content': 'Hi there!'},
#   {'role': 'user', 'content': 'How are you?'},
#   {'role': 'assistant', 'content': "I'm doing well, thank you for asking!"}
# ]

# Get context info
info = context_mgr.get_context_info()
# info might be:
# {
#   'total_messages': 5,
#   'conversation_interactions': 2,
#   'total_tokens': 50, # Example value
#   'system_prompt_tokens': 10, # Example value
#   'conversation_tokens': 40, # Example value
#   'under_limit': True
# }

# Clear conversation
context_mgr.clear_conversation()
```

# Dependencies and Interactions

-   **`tiktoken`**: Used for counting tokens accurately. This is a crucial dependency for managing context size effectively.
-   **`collections.deque`**: Used by `ConversationHistory` to efficiently manage the list of past interactions, allowing for easy addition and removal from both ends (though primarily used as a FIFO queue here with `maxlen`).
-   **`SmolDAgent` (`smold/agent.py`)**: The `SmolDAgent` instantiates and uses a `ContextManager` to keep track of the conversation and provide the necessary context to the LLM for each `run`. It also calls `refresh_with_system_prompt` when the agent's working directory (and thus its system prompt) changes.

The `ContextManager` plays a vital role in enabling multi-turn conversations by preserving relevant history while respecting the constraints of the language model's context window. Accurate token counting and intelligent trimming are key to its effectiveness.
