# Overview

The `smold/agent.py` file is responsible for creating and managing the core AI agent of the SmolD application. It defines the `SmolDAgent` class, which enhances a base `ToolCallingAgent` with features like conversation history management, context awareness (especially regarding the current working directory), and dynamic tool loading based on the operating system. This file also includes the factory function `create_agent` to instantiate and configure the agent.

# Key Components

-   **`SmolDAgent` class**:
    *   Wraps a `ToolCallingAgent` (from the `smolagents` library).
    *   Manages conversation history using a `ContextManager`.
    *   Integrates a `DebugLogger` for logging API calls, tool usage, and context information when debug mode is enabled.
    *   Handles the dynamic system prompt which includes context about the current working directory.
    *   Provides methods like `run(query)` to process user input, `clear_conversation()` to reset history, and `get_context_info()` to retrieve details about the current conversational state.
-   **`create_agent(cwd=None, debug=False, use_pro=False)` function**:
    *   The main factory function for creating a `SmolDAgent` instance.
    *   Initializes the debug logger if `debug` is true.
    *   Determines the appropriate Gemini model (Flash or Pro) based on the `use_pro` flag.
    *   Instantiates a `LiteLLMModel` with the selected Gemini model and API key.
    *   Generates a dynamic system prompt using `get_system_prompt(cwd)` which includes information about the current working directory and available tools.
    *   Loads available tools using `get_available_tools()`.
    *   **Monkey-patches `litellm.completion`**: This is a critical part. It intercepts calls to the underlying LLM to:
        *   Ensure the custom dynamic system prompt is always used, overriding any other system messages.
        *   Log raw API requests and responses if debug mode is enabled.
    *   Instantiates the base `ToolCallingAgent` and then wraps it with `SmolDAgent`.
-   **`get_available_tools()` function**:
    *   Dynamically discovers and loads available tools (e.g., `ls_tool`, `edit_tool`, `bash_tool` or `powershell_tool` depending on the OS).
    *   Uses `import_tool_safely` to load tool modules.
-   **`refresh_agent_context(agent, new_cwd=None)` function**:
    *   Updates an existing agent's system prompt and context when the current working directory changes, without needing to recreate the entire agent. This is more efficient.
-   **`import_tool_safely(module_path, tool_name)` function**:
    *   A utility to safely import tool modules by their file path, handling potential import errors.

# Important Variables/Constants

-   **`system_prompt`**: A dynamically generated string that provides instructions and context to the LLM. It includes the current working directory, OS information, and a list of available tools. This prompt is crucial for guiding the agent's behavior.
-   **`agent_model` (LiteLLMModel)**: An instance of the language model wrapper, configured to use either Gemini Flash or Pro.
-   **`tools` (list)**: A list of tool instances that the agent can use (e.g., file system tools, shell command tools).

# Usage Examples

The `agent.py` module is primarily used internally by `main.py`. The `create_agent` function is the main interface for other parts of the application to get an initialized agent.

```python
# In main.py or another module:
from smold.agent import create_agent, refresh_agent_context
import os

# Create a new agent for the current directory
my_agent = create_agent(cwd=os.getcwd(), debug=True)

# Run a query
response = my_agent.run("List all python files in the current directory.")
print(response)

# Change working directory and refresh context
new_working_dir = "/path/to/another/project"
if os.path.exists(new_working_dir):
    my_agent = refresh_agent_context(my_agent, new_cwd=new_working_dir)
    response_after_cd = my_agent.run("What is in the README here?")
    print(response_after_cd)
```

# Dependencies and Interactions

-   **`os`**: Used extensively for path manipulation, getting current working directory, and checking platform.
-   **`platform`**: Used to determine the operating system for loading appropriate shell tools (Bash or PowerShell).
-   **`importlib.util`**: Used for dynamically importing tool modules.
-   **`dotenv` (`load_dotenv`)**: For loading environment variables (like `GEMINI_API_KEY`).
-   **`smolagents` (`CodeAgent`, `ToolCallingAgent`, `LiteLLMModel`)**: This is the base library providing the core agent and model functionalities. `SmolDAgent` extends `ToolCallingAgent`.
-   **`smold.system_prompt` (`get_system_prompt`)**: Provides the function to generate the detailed system prompt.
-   **`smold.context_manager` (`ContextManager`)**: Manages the conversation history and token limits.
-   **`smold.debug_logger` (`get_debug_logger`, `initialize_debug_logger`)**: Handles logging for debugging purposes.
-   **Tool modules (e.g., `smold.tools.ls_tool`, `smold.tools.bash_tool`, etc.)**: These files define the actual tools that the agent can invoke.
-   **`litellm`**: The library used to interact with various LLMs, including Google's Gemini models. The `create_agent` function monkey-patches `litellm.completion` to customize system prompt handling and enable logging.

This file is central to the agent's intelligence and its ability to interact with its environment and the user effectively. The monkey-patching of `litellm.completion` is a key mechanism for ensuring consistent behavior and deep integration of the custom system prompt.
