# Overview

The `main.py` file is the main entry point for the SmolD application. It handles command-line argument parsing, initializes the agent, and manages the interactive mode or single query execution. It also provides user-friendly welcome messages and help information.

# Key Components

-   **`print_welcome()`**: Displays a welcome message with usage instructions and examples when the script is run without arguments.
-   **`main()`**: The primary function that orchestrates the application flow. It parses command-line arguments, sets up the working directory, initializes the `SmolDAgent`, and processes user queries either directly or by entering interactive mode.
-   **`recreate_agent_with_cwd(new_cwd, current_agent=None, debug_mode=False)`**: Handles changing the agent's working directory. It attempts to refresh the existing agent's context or creates a new agent instance if necessary.
-   **`run_interactive_mode(agent, verbose_errors=False, debug_mode=False, current_model="Flash")`**: Manages the interactive session, allowing users to input multiple queries. It handles special commands like `help`, `cd`, `ls`, `clear`, `context`, and `pro` (to switch LLM models).
-   **`print_help_commands()`**: Displays detailed help information about available tools and commands within the interactive mode.

# Important Variables/Constants

-   **`parser` (argparse.ArgumentParser)**: Used to define and parse command-line arguments such as query input, interactive mode flag, custom working directory, debug mode, and model selection (Pro vs. Flash).
-   **`agent` (SmolDAgent)**: An instance of the SmolD agent, responsible for processing queries and interacting with the language model and tools.

# Usage Examples

**Running a single query:**

```bash
python main.py "What files are in the current directory?"
```

**Starting interactive mode:**

```bash
python main.py -i
```

**Setting a custom working directory for a query:**

```bash
python main.py --cwd /path/to/your/project "Summarize the README.md in this project."
```

**Using the higher-quality Gemini Pro model:**

```bash
python main.py --pro "Analyze the complexity of the main function in main.py"
```

**Interactive mode commands:**

-   `help`: Show available tools and capabilities.
-   `cd <path>`: Change working directory.
-   `ls` or `dir`: List contents of the current directory.
-   `clear`: Clear conversation history.
-   `context`: Show conversation context and token usage.
-   `pro`: Switch between Gemini Flash and Pro models.
-   `exit` or `quit`: End the interactive session.

# Dependencies and Interactions

-   **`sys`**: Used for accessing command-line arguments (`sys.argv`) and exiting the script (`sys.exit`).
-   **`os`**: Used for file system operations like getting the current working directory (`os.getcwd()`), changing directories (`os.chdir()`), path manipulation (`os.path.expanduser`, `os.path.isabs`, `os.path.join`, `os.path.normpath`).
-   **`argparse`**: For parsing command-line arguments.
-   **`traceback`**: For printing detailed error tracebacks when in verbose or debug mode.
-   **`smold.create_agent`**: Factory function to create an instance of the `SmolDAgent`.
-   **`smold.agent.refresh_agent_context`**: Function to update an existing agent's context when the working directory changes.
-   **`smold.tools.ls_tool.ls_tool`**: Used to directly handle `ls` or `dir` commands in interactive mode for faster local execution.

The `main.py` script orchestrates the core functionality of SmolD by integrating various modules from the `smold` package, particularly `agent.py` for the agent logic and various tools within `smold.tools`. It acts as the user-facing interface to the underlying AI assistant capabilities.
