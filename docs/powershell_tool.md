# Overview

The `smold/tools/powershell_tool.py` file defines the `PowerShellTool` class, enabling the SmolD agent to execute PowerShell commands. This tool is intended primarily for Windows environments but can also work with PowerShell Core on other platforms if `pwsh` is available. It aims to provide a persistent PowerShell session (though the current implementation of `_execute_command_with_timeout` creates a new process for each command for reliability) and includes features like command timeout, output truncation, and safety measures such as banning certain commands.

# Key Components

-   **`PowerShellTool` class (inherits from `smolagents.Tool`)**:
    *   **`name`**: "PowerShell"
    *   **`description`**: A detailed guide for the LLM on using the tool. It covers:
        *   Safety: Confirming parent directory existence (using LS tool) before creating files/folders.
        *   Banned commands: A list of restricted commands (e.g., `Invoke-WebRequest`, `Start-Process`, browsers) to prevent misuse.
        *   Operational notes: Mandatory `command` argument, optional `timeout` (max 10 minutes, default 30 minutes), output truncation at 30,000 characters.
        *   Guidance on alternatives: Advises against using `Select-String` (use `GrepTool`), `Get-Content`/`Get-ChildItem` (use `View`/`LS`).
        *   Command chaining: Use `;` for multiple commands.
        *   Session persistence: States that variables, modules, and current directory persist (though the current `_execute_command_with_timeout` implementation might not fully support this as it creates new processes).
        *   Directory changes: Advises using absolute paths and avoiding `Set-Location` unless explicitly instructed.
    *   **`inputs`**:
        *   `command` (string, required): The PowerShell command to execute.
        *   `timeout` (number, optional): Timeout in milliseconds.
    *   **`output_type`**: "string" (the command's stdout and/or stderr).
    *   **Constants**:
        *   `DEFAULT_TIMEOUT`: 30 minutes.
        *   `MAX_TIMEOUT`: 10 minutes.
        *   `MAX_OUTPUT_CHARS`: 30,000.
        *   `BANNED_COMMANDS`: List of disallowed PowerShell cmdlets and aliases (e.g., `Invoke-WebRequest`, `curl`, `Start-Process`).
    *   **Initialization (`__init__`, `_initialize_shell`)**:
        *   `_initialize_shell()`: Attempts to start a persistent PowerShell process (`powershell.exe` on Windows, `pwsh` otherwise) with specific arguments (`-NoProfile`, `-NoLogo`, `-Command -`). It sets up `stdin`, `stdout`, `stderr` pipes. If PowerShell is not found, it raises a `RuntimeError`.
        *   *Note: The current implementation of `_execute_command_with_timeout` seems to bypass the persistent shell for individual command execution for reliability, opting for fresh processes.*
    *   **Execution Logic (`forward`, `_execute_command_with_timeout`)**:
        *   `forward(command: str, timeout: Optional[int] = None) -> str`:
            *   Checks if the (persistent) shell process is alive; tries to restart if not.
            *   Performs a security check using `_is_banned_command()`.
            *   Sets the timeout.
            *   Calls `_execute_command_with_timeout()`.
        *   `_execute_command_with_timeout(command: str, timeout_sec: float) -> str`:
            *   **Current Implementation Detail**: This method, as written in the provided code, creates a *new* PowerShell process for *each command* (`powershell.exe -Command {command}` or `pwsh -Command {command}`). This approach ensures command isolation and simplifies timeout handling with `process.communicate(timeout=timeout_sec)` but sacrifices true session persistence for variables and environment across multiple tool calls.
            *   Captures `stdout` and `stderr`.
            *   If the command times out, it kills the process and returns a timeout message.
            *   Formats and returns `stdout`, including `stderr` if the command had a non-zero exit code and `stderr` has content.
    *   **Helper Methods (some might be less relevant with the current non-persistent execution in `_execute_command_with_timeout`)**:
        *   `_read_line_nonblocking_with_source()`: Intended for reading from a persistent shell's stdout/stderr without blocking.
        *   `_read_line_blocking()`: Intended for blocking reads from a persistent shell.
        *   `_kill_current_command()`: Intended to interrupt a command in a persistent shell (e.g., via `SIGINT` or `terminate()`) and then reinitialize the shell.
        *   `_is_banned_command(command: str) -> bool`: Checks if the input `command` contains any of the `BANNED_COMMANDS` using regex word boundary matching.
        *   `_format_write_host_output(output: str) -> str`: Placeholder for formatting `Write-Host` output (currently returns input as is).
        *   `_format_truncated_output(content: str) -> str`: Truncates output if it exceeds `MAX_OUTPUT_CHARS`.
        *   `_format_result_with_stderr(stdout: str, stderr: str) -> str`: Combines stdout and stderr.
    *   **Cleanup (`__del__`)**: Attempts to terminate the persistent shell process if it exists.

-   **`powershell_tool = PowerShellTool()`**: A global instance for easy import.

# Important Variables/Constants

(Listed under `PowerShellTool` class component)

# Usage Examples

The agent uses this tool to execute PowerShell commands, typically on a Windows system.

**Agent getting system information (Windows):**

```python
# User: "Get the list of running processes on this Windows machine."
# Agent uses PowerShellTool.
result = powershell_tool.forward(command="Get-Process | Select-Object -Property Name, CPU, Memory | Format-Table -AutoSize")
print(result)
# Output would be a formatted table of processes.
```

**Agent attempting a banned command:**

```python
result = powershell_tool.forward(command="Invoke-WebRequest -Uri https://example.com")
print(result)
# Output: "Error: Command contains one or more banned commands: Invoke-WebRequest, ..."
```

# Dependencies and Interactions

-   **Standard Libraries**:
    *   `os`: Used for `os.getcwd()`.
    *   `re`: Used by `_is_banned_command` for matching banned commands.
    *   `subprocess`: Core library for creating and managing PowerShell processes.
    *   `time`: Used for timeout logic and generating unique markers (though markers are less relevant with non-persistent execution).
    *   `signal`: Used by `_kill_current_command` on non-Windows for `SIGINT`.
    *   `platform`: Used to determine the OS for choosing `powershell.exe` vs `pwsh` and for `subprocess.CREATE_NO_WINDOW` flag.
-   **`smolagents.Tool`**: The base class.
-   **Operating System**:
    *   Requires PowerShell to be installed and in the system's PATH.
    *   Uses `powershell.exe` on Windows.
    *   Uses `pwsh` (PowerShell Core) on other platforms.
-   **Other Tools**: The description advises using `LSTool`, `ViewTool`, `GrepTool`, `GlobTool` for tasks that native PowerShell cmdlets like `Get-ChildItem`, `Get-Content`, `Select-String` might otherwise perform.

This tool provides the agent with the ability to interact with the system via PowerShell. The current implementation of executing each command in a new process simplifies some aspects of reliability and timeout but means that session state (like variables or current location changes via `Set-Location`) will not persist between separate calls to the tool. The banned commands list aims to provide a layer of safety.
