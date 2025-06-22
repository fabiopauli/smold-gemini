# Overview

The `smold/google_genai_model.py` file defines the `GoogleGenAIModel` class, which serves as a wrapper around the Google Generative AI (Gemini) Python SDK. This class implements the `smolagents.models.Model` interface, allowing Gemini models (like `gemini-2.5-pro` and `gemini-2.5-flash`) to be seamlessly integrated into the `smolagents` framework, and by extension, into the SmolD application. It handles the conversion of message formats, API client initialization, and the specifics of calling the Google GenAI API.

# Key Components

-   **`GoogleGenAIModel` class (inherits from `smolagents.models.Model`)**:
    *   **Initialization (`__init__`)**:
        *   Takes `model_id` (e.g., "gemini-2.5-pro"), `api_key`, `temperature`, `thinking_budget`, and `system_prompt` as parameters.
        *   The API key is sourced from the `api_key` parameter or the `GEMINI_API_KEY` environment variable.
        *   Initializes the `google.genai.Client`.
        *   Stores configuration and sets `tool_name_key` and `tool_arguments_key` required by `smolagents` for tool calling.
    *   **`generate(messages, stop_sequences=None, grammar=None, **kwargs) -> ChatMessage`**:
        *   The core method required by the `smolagents.Model` interface.
        *   Converts the input `messages` (in `smolagents` format) to Google GenAI's `Contents` format using `_convert_messages_to_contents`. System messages are handled separately via `system_instruction`.
        *   Creates a `GenerateContentConfig` using `_create_generation_config`, including temperature, system instructions, and thinking budget.
        *   Calls the `self.client.models.generate_content` (non-streaming) method of the Google GenAI SDK.
        *   Extracts the response text and token usage information from the API response.
        *   Returns a `smolagents.models.ChatMessage` object containing the role, content, raw response, and token usage.
        *   Includes error handling for API calls.
    *   **`__call__(...)`**: A convenience method that makes the class instance callable, simply forwarding to the `generate` method.
    *   **`_convert_messages_to_contents(messages: List[Dict[str, Any]]) -> List[types.Content]`**:
        *   Translates a list of `smolagents`-style message dictionaries (with "role" and "content") into Google GenAI's `types.Content` objects.
        *   Maps roles (e.g., "assistant" to "model", "user" to "user").
        *   Skips system messages (as they are passed via `system_instruction` in `GenerateContentConfig`).
        *   Handles different content structures (string, list of text parts).
    *   **`_create_generation_config(**kwargs) -> types.GenerateContentConfig`**:
        *   Constructs the `GenerateContentConfig` object for the API call.
        *   Sets temperature, `response_mime_type` ("text/plain").
        *   If a `system_prompt` is set on the model instance, it's included as `system_instruction`.
        *   Includes `thinking_config` if `thinking_budget` is specified.
    *   **`set_system_prompt(system_prompt: str)`**: Allows updating the system prompt for the model instance.
    *   **`get_system_prompt() -> Optional[str]`**: Retrieves the current system prompt.
    *   **`model_name` (property)**: Returns the `model_id`, for compatibility with parts of `smolagents` that might expect this property.

# Important Variables/Constants

-   **`model_id` (instance variable)**: The specific Gemini model to use (e.g., "gemini-2.5-pro").
-   **`api_key` (instance variable/environment variable)**: The Google Cloud API key for authentication.
-   **`system_prompt` (instance variable)**: The system-level instructions provided to the model.
-   **`client` (instance variable)**: An instance of `google.genai.Client`.

# Usage Examples

This class is primarily intended to be used by the `smolagents` library, particularly by `ToolCallingAgent` or other agent types when configured to use a Gemini model.

```python
# Example of how SmolDAgent might (indirectly via smolagents) use this:
from smold.google_genai_model import GoogleGenAIModel
from smolagents import ToolCallingAgent # Assuming this is the base agent

# Initialize the Google GenAI model wrapper
gemini_model = GoogleGenAIModel(
    model_id="gemini-2.5-flash",
    api_key="YOUR_GEMINI_API_KEY", # Or set GEMINI_API_KEY environment variable
    system_prompt="You are a helpful assistant."
)

# This model instance would then be passed to a smolagent
# For example (conceptual):
# agent = ToolCallingAgent(tools=[...], model=gemini_model)

# Direct invocation (more for testing the wrapper itself)
messages_for_llm = [
    {"role": "user", "content": "What is the capital of France?"}
]
chat_response = gemini_model.generate(messages=messages_for_llm)
print(f"Assistant: {chat_response.content}")
if chat_response.token_usage:
    print(f"Tokens used: Input {chat_response.token_usage.input_tokens}, Output {chat_response.token_usage.output_tokens}")

# Setting a new system prompt
gemini_model.set_system_prompt("You are a poetic assistant. Respond in verse.")
chat_response_poetic = gemini_model.generate(messages=[{"role": "user", "content": "Tell me about clouds."}])
print(f"Poet Assistant: {chat_response_poetic.content}")
```

# Dependencies and Interactions

-   **`google-generativeai` (as `google.genai`)**: The official Google Python SDK for interacting with Gemini models. This is the primary external dependency.
-   **`smolagents.models.Model`**: The base class from which `GoogleGenAIModel` inherits, defining the interface it must implement.
-   **`smolagents.models.ChatMessage` and `smolagents.models.TokenUsage`**: Data classes from `smolagents` used for structuring the response.
-   **`os`**: Used to fetch the `GEMINI_API_KEY` from environment variables if not provided directly.
-   **`SmolDAgent` (`smold/agent.py`)**: While `SmolDAgent` itself uses `LiteLLMModel` in the current project structure, `GoogleGenAIModel` represents an alternative or potentially more direct way to integrate Gemini models, especially if deeper control over Google-specific features were required than what `LiteLLMModel` abstracts. The project currently uses `LiteLLMModel` which in turn can use Google models, making this specific file potentially less directly used by `create_agent` but available for specific needs or future refactoring.

This class ensures that Google's powerful Gemini models can be used as a backend for agents built with the `smolagents` library by adhering to its expected model interface. It abstracts the direct API interaction details specific to Google GenAI.
