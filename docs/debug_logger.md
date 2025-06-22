# Overview

The `smold/debug_logger.py` module provides a `DebugLogger` class responsible for saving detailed information about the agent's operations when debug mode is active. This includes system prompts, API queries and responses, raw API request/response data, tool invocations, and context manager state. The logs are saved to a specified directory (defaulting to `debug-logs/`) and are organized by session and call number, making it easier to trace and debug the agent's behavior.

# Key Components

-   **`DebugLogger` class**:
    *   **Initialization (`__init__`)**:
        *   Takes `enabled` (boolean) and `debug_dir` (string) as parameters.
        *   If `enabled` is true, it creates the debug directory (if it doesn't exist) and sets a `session_id` based on the current timestamp to group related log files.
    *   **Log Methods**:
        *   `log_system_prompt(system_prompt: str)`: Saves the system prompt used by the agent to a `.txt` file.
        *   `log_api_call(query: str, response: str, call_number: int, full_context: str = None)`: Saves the user query and the agent's response for a specific API call to a `.txt` file. Can optionally include the full context sent to the API.
        *   `log_full_conversation_context(messages: list, call_number: int)`: Saves the complete list of messages (the entire conversation context) sent to the LLM API. It saves both a JSON version and a human-readable `.txt` version.
        *   `log_raw_api_request(messages: list, call_number: int, kwargs: dict = None)`: Logs the exact messages and any additional keyword arguments sent to the `litellm.completion` function. Saves as JSON and a readable `.txt` file.
        *   `log_raw_api_response(response, call_number: int)`: Logs the complete, raw response object received from the LLM API. Saved as a JSON file.
        *   `log_tool_calls(tool_calls: list, call_number: int)`: Saves information about any tools called by the agent during an API interaction to a JSON file.
        *   `log_context_info(context_info: Dict[str, Any])`: Saves the state of the `ContextManager` (e.g., token counts, number of interactions) to a JSON file.
    *   **Directory Setup (`_setup_debug_directory`)**: Ensures the logging directory exists.
-   **Global Instance Management**:
    *   `_debug_logger`: A global variable to hold a singleton instance of `DebugLogger`.
    *   `get_debug_logger() -> DebugLogger`: Returns the global `DebugLogger` instance, creating a default one if it doesn't exist (initially disabled).
    *   `initialize_debug_logger(enabled: bool = False, debug_dir: str = "debug-logs") -> DebugLogger`: Initializes or re-initializes the global `DebugLogger` instance with specified settings. This is the primary way the logger is activated and configured by the application.

# Important Variables/Constants

-   **`enabled` (in `DebugLogger` instance)**: A boolean flag that controls whether logging is active. If `False`, log methods do nothing.
-   **`debug_dir` (in `DebugLogger` instance)**: A `pathlib.Path` object representing the directory where log files are stored. Defaults to `"debug-logs"`.
-   **`session_id` (in `DebugLogger` instance)**: A timestamp string (e.g., `"20231027_143055"`) used to prefix log filenames, grouping logs from a single run of the agent.
-   **Log Filename Conventions**: Log files are named descriptively, including the type of log (e.g., `system_prompt`, `api_call`, `raw_api_request`), the `session_id`, and often a `call_number` (for sequential events like API calls).

# Usage Examples

The `DebugLogger` is typically initialized and used within the agent's core logic, particularly when debug mode is enabled via a command-line flag.

```python
# In smold/agent.py or main.py

from smold.debug_logger import initialize_debug_logger, get_debug_logger

# Initialize the logger when the application starts if debug mode is on
# This is usually done once.
# Example: if args.debug:
# initialize_debug_logger(enabled=True, debug_dir="my_custom_debug_logs")

# Get the logger instance elsewhere in the code
logger = get_debug_logger()

# Example usage within the agent
if logger.enabled:
    logger.log_system_prompt("Current system prompt content...")

    # After an API call
    call_num = 1 # Increment this for each call
    logger.log_raw_api_request(messages_sent_to_llm, call_num, other_params)
    logger.log_raw_api_response(raw_llm_response_object, call_num)
    logger.log_api_call(user_query, agent_text_response, call_num)
    if agent_tool_calls:
        logger.log_tool_calls(agent_tool_calls, call_num)

    # When context info is relevant
    logger.log_context_info({"tokens": 500, "interactions": 3})
```

When debug mode is active, files like the following would appear in the `debug-logs` directory (or the custom specified directory):

-   `system_prompt_20231027_143055.txt`
-   `api_call_20231027_143055_001.txt`
-   `raw_api_request_20231027_143055_001.json`
-   `raw_api_request_20231027_143055_001.txt`
-   `raw_api_response_20231027_143055_001.json`
-   `tool_calls_20231027_143055_001.json`
-   `full_context_20231027_143055_001.json`
-   `full_context_20231027_143055_001.txt`
-   `context_info_20231027_143055.json`

# Dependencies and Interactions

-   **Standard Libraries**:
    *   `os`: (Implicitly via `pathlib`)
    *   `json`: For serializing data structures (like tool calls, raw API responses, context info) into JSON format for log files.
    *   `datetime`: For generating timestamps for `session_id` and within log entries.
    *   `pathlib`: For robust and platform-independent path manipulation for creating directories and file paths.
-   **`SmolDAgent` (`smold/agent.py`)**: The agent logic is the primary consumer of the `DebugLogger`. It calls the logger's methods at various points (e.g., before/after API calls, when system prompt is set, when tools are called) if debugging is enabled.
-   **`litellm` (indirectly via `smold/agent.py`)**: The raw request and response data logged often comes from interactions with the `litellm` library, which `SmolDAgent` uses for LLM communication.

The `DebugLogger` is a crucial tool for developers working on SmolD, providing transparency into the agent's internal state and its interactions with language models. It does not affect the agent's core logic if disabled.
