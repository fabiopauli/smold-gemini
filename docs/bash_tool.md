# Overview

The `smold/tools/bash_tool.py` file defines the `BashTool` class, which allows the SmolD agent to execute shell commands in a persistent Bash session. This tool is designed for Unix-like systems. It includes features for command timeout, output truncation, and safety measures like banning certain potentially harmful or redundant commands.

# Key Components

-   **`BashTool` class (inherits from `smolagents.Tool`)**:
    *   **`name`**: "Bash"
    *   **`description`**: A detailed description for the LLM on how to use the tool, including safety checks (confirming parent directory existence before creating files/folders, avoiding banned commands) and operational notes (persistent session, timeout, output truncation, avoiding `find`/`grep`/`cat`/`ls` in favor of other specialized tools like `GrepTool`, `GlobTool`, `View`, `LS`).
    *   **`inputs`**: Defines the expected input arguments:
        *   `command` (string, required): The Bash command to execute.
        *   `timeout` (number, optional): Timeout in milliseconds (max 600,000 ms or 10 minutes, defaults to 30 minutes if not set).
    *   **`output_type`**: "string" (the command's stdout and/or stderr).
    *   **Constants**:
        *   `DEFAULT_TIMEOUT`: 30 minutes (1,800,000 ms).
        *   `MAX_TIMEOUT`: 10 minutes (600,000 ms).
        *   `MAX_OUTPUT_CHARS`: 30,000 characters for output truncation.
        *   `BANNED_COMMANDS`: A list of commands that are disallowed (e.g., `curl`, `wget`, `rm -rf /`, network utilities, browsers).
    *   **Initialization (`__init__`, `_initialize_shell`)**:
        *   When an instance of `BashTool` is created, it calls `_initialize_shell()` to start a persistent `/bin/bash` subprocess.
        *   `stdin`, `stdout`, and `stderr` of this subprocess are piped for communication.
        *   A unique `output_marker` string is generated to help identify the end of a command's output in the persistent session.
    *   **Execution Logic (`forward`, `_execute_command_with_timeout`)**:
        *   `forward(command: str, timeout: Optional[int] = None) -> str`:
            *   Checks if the shell process is alive; restarts it if not.
            *   Performs a security check using `_is_banned_command()`. If a banned command is detected, it returns an error message.
            *   Sets the timeout (respecting `MAX_TIMEOUT`).
            *   Calls `_execute_command_with_timeout()` to run the command.
        *   `_execute_command_with_timeout(command: str, timeout_sec: float) -> str`:
            *   Appends the `output_marker` (e.g., `echo __COMMAND_OUTPUT_MARKER_1678886400_`) to the user's command to delimit its output.
            *   Writes the combined command to the shell's `stdin`.
            *   Enters a loop to read lines from `stdout` and `stderr` non-blockingly using `_read_line_nonblocking_with_source()`.
            *   If the timeout is exceeded, it calls `_kill_current_command()` and returns a timeout message.
            *   Stops reading when the `output_marker` is detected in the output.
            *   If `MAX_OUTPUT_CHARS` is exceeded, the output is truncated in the middle by `_format_truncated_output()`.
            *   Handles special formatting for `echo` commands via `_format_echo_output()`.
            *   Combines `stdout` and `stderr` using `_format_result_with_stderr()`.
    *   **Helper Methods**:
        *   `_read_line_nonblocking_with_source()`: Reads a line from `stdout` or `stderr` without blocking, indicating the source.
        *   `_read_line_blocking()`: Reads a line, blocking until data is available.
        *   `_kill_current_command()`: Sends a `SIGINT` (Ctrl+C) to the shell process to interrupt the currently running command. Restarts the shell if `SIGINT` fails.
        *   `_is_banned_command(command: str) -> bool`: Checks if the input `command` (or any part of it if it's a complex command) is in the `BANNED_COMMANDS` list.
        *   `_contains_search_or_read_commands(command: str) -> bool`: (Defined but seems not directly used in the primary execution flow of `forward`) Checks for commands like `grep`, `find`, `cat`, `ls`, suggesting the agent should use dedicated tools instead.
        *   `_format_echo_output(output: str) -> str`: Escapes special characters in the output of `echo` commands.
        *   `_format_truncated_output(content: str) -> str`: Truncates output string if it exceeds `MAX_OUTPUT_CHARS`, adding a "truncated" message in the middle.
        *   `_format_result_with_stderr(stdout: str, stderr: str) -> str`: Combines stdout and stderr into a single string.
    *   **Cleanup (`__del__`)**: When the `BashTool` instance is destroyed, it attempts to terminate the persistent shell process.

-   **`bash_tool = BashTool()`**: A global instance of `BashTool` is created, making it readily available for import and use.

# Important Variables/Constants

(Already listed under `BashTool` class component)

# Usage Examples

The `BashTool` is intended to be invoked by the SmolD agent when it determines a shell command needs to be executed on a Unix-like system.

**Agent's internal call (conceptual):**

```python
# Agent decides to run a bash command
command_to_run = "ls -la /tmp"
timeout_ms = 5000 # 5 seconds

# Assuming 'bash_tool' is an available tool instance
result = bash_tool.forward(command=command_to_run, timeout=timeout_ms)
print(result)
# Output would be the string result of 'ls -la /tmp' or an error/timeout message.
```

**Agent attempting a banned command:**

```python
result = bash_tool.forward(command="curl https://example.com")
print(result)
# Output: "Error: Command contains one or more banned commands: curl, wget, ..."
```

**Agent running a long command that times out:**

```python
result = bash_tool.forward(command="sleep 60", timeout=1000) # 1 second timeout
print(result)
# Output: "Command timed out after 1.0 seconds"
```

# Dependencies and Interactions

-   **Standard Libraries**:
    *   `os`: Used for `os.getcwd()` and `os.path.basename()`.
    *   `re`: (Defined `_contains_search_or_read_commands` uses it, but this method isn't directly in the `forward` path).
    *   `subprocess`: Core library for creating and managing the persistent Bash process.
    *   `shlex`: Used by `_is_banned_command` to safely split command strings into tokens.
    *   `time`: Used for timeout logic and generating unique markers.
    *   `threading`: (Not directly used, `signal` is used for interruption).
    *   `signal`: Used by `_kill_current_command` to send `SIGINT`.
-   **`smolagents.Tool`**: The base class from which `BashTool` inherits.
-   **Operating System**: This tool is specifically for Bash and thus expects a Unix-like environment where `/bin/bash` is available. It will not work correctly on Windows systems (which would typically use `powershell_tool.py`).
-   **Other Tools**: The description explicitly guides the LLM to use other tools like `LSTool`, `ViewTool`, `GrepTool`, `GlobTool` for tasks that `ls`, `cat`, `grep`, `find` might traditionally do, promoting the use of more specialized and potentially safer/structured tool interactions.

This tool provides a powerful capability for the agent to interact with the shell, with considerations for persistence, safety, and resource management (timeouts, output limits). The persistent session is a key feature, allowing commands to build on each other (e.g., setting environment variables, changing directories if explicitly allowed).
