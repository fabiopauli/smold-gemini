# Overview

The `smold/tools/cd_tool.py` file defines the `ChangeDirectoryTool`, which allows the SmolD agent to change its current working directory (`cwd`). This tool is more than a simple `os.chdir()` wrapper; it includes validation, support for special path syntaxes (like `~` for home, `.` for current, `..` for parent, and `-` for previous directory), safety checks against restricted system directories, and helpful feedback like directory content summaries and suggestions for mistyped paths.

# Key Components

-   **`ChangeDirectoryTool` class (inherits from `smolagents.Tool`)**:
    *   **`name`**: "ChangeDirectory"
    *   **`description`**: Details the tool's ability to change the agent's working directory, highlighting features like path validation, support for absolute/relative paths, tilde expansion, environment variable expansion, suggestions for typos, and safety features (restricted directories).
    *   **`inputs`**: Defines one input:
        *   `path` (string, required): The target directory path.
    *   **`output_type`**: "string" (a status message indicating success or failure, along with context).
    *   **Initialization (`__init__`)**:
        *   Initializes `self.previous_directory` to `None` (used for `cd -` functionality).
        *   Calls `_get_restricted_directories()` to populate `self.restricted_dirs` based on the operating system.
    *   **Core Logic (`forward(path: str) -> str`)**:
        *   Stores the current directory before attempting a change.
        *   Handles special path arguments:
            *   `-`: Changes to `self.previous_directory` if set.
            *   `~`: Changes to the user's home directory (`Path.home()`).
        *   For other paths, it expands user tilde (`os.path.expanduser`) and environment variables (`os.path.expandvars`), then resolves it to an absolute path (`os.path.abspath`).
        *   Validates the target path using `_validate_directory()`. If invalid, returns an error message (possibly with suggestions).
        *   Checks if the target path is a restricted directory using `_is_restricted_directory()`. If so, returns a safety error.
        *   Attempts `os.chdir(target_path)`.
        *   On success, updates `self.previous_directory`, gets a summary of the new directory's contents using `_get_directory_summary()`, and returns a success message including previous and new `cwd`, and the content summary.
        *   Handles `PermissionError` and other exceptions during `os.chdir`.
    *   **Helper Methods**:
        *   `_get_restricted_directories() -> list[str]`: Returns a list of paths that the tool should prevent access to, depending on whether the OS is Windows or Unix-like (e.g., `C:\Windows\System32`, `/bin`, `/sbin`).
        *   `_validate_directory(path: str) -> dict`: Checks if a path exists and is a directory. Returns a dictionary `{"valid": bool, "message": str}`. If the path doesn't exist, it calls `_get_directory_suggestions()`.
        *   `_is_restricted_directory(path: str) -> bool`: Checks if the normalized version of `path` starts with any of the paths in `self.restricted_dirs`.
        *   `_get_directory_suggestions(path: str) -> str`: If a target path doesn't exist, this method looks in its parent directory for items with similar names (using basic string matching and Levenshtein distance via `_levenshtein_distance()`) and returns them as suggestions.
        *   `_levenshtein_distance(s1: str, s2: str) -> int`: A standard implementation of the Levenshtein distance algorithm to measure string similarity.
        *   `_get_directory_summary(path: str) -> str`: Lists the number of files and directories in the given `path`, along with a preview of the first few names. Returns a summary string or an error message if contents are inaccessible.

-   **`cd_tool = ChangeDirectoryTool()`**: A global instance of `ChangeDirectoryTool` is created for easy import and use.

# Important Variables/Constants

-   **`previous_directory` (instance variable)**: Stores the last working directory before a successful `cd` operation, enabling `cd -`.
-   **`restricted_dirs` (instance variable)**: A list of directory paths that are considered off-limits for safety.

# Usage Examples

The agent would use this tool when a user requests to navigate the file system.

**Agent's internal call (conceptual):**

```python
# User asks: "Go to my project's source folder"
# Agent identifies "src" as the target relative path.
result = cd_tool.forward(path="./src")
print(result)
# Possible output:
# Directory changed successfully!
#
# Previous: /home/user/my_project
# Current:  /home/user/my_project/src
#
# 📁 3 directories: components, utils, services (and 1 more)
# 📄 5 files: main.py, helpers.py, api.py (and 2 more)

# User asks: "cd to /etc" (on Linux)
result = cd_tool.forward(path="/etc")
print(result)
# Possible output:
# Error: Cannot change to restricted system directory '/etc'. This is prevented for safety reasons.

# User asks: "cd to non_existent_folder"
result = cd_tool.forward(path="non_existent_folder")
print(result)
# Possible output (if 'existent_folder' exists):
# Error: Directory '/home/user/project/non_existent_folder' does not exist.
#
# Did you mean one of these?
#   - /home/user/project/existent_folder
```

# Dependencies and Interactions

-   **Standard Libraries**:
    *   `os`: Core library for all directory and path operations (`getcwd`, `chdir`, `path.exists`, `path.isdir`, `path.abspath`, `path.expanduser`, `path.expandvars`, `listdir`, etc.).
    *   `platform`: Used by `_get_restricted_directories` to determine the operating system and provide appropriate restricted paths.
    *   `pathlib.Path`: Used for `Path.home()` to reliably get the user's home directory.
-   **`smolagents.Tool`**: The base class from which `ChangeDirectoryTool` inherits.
-   **Agent Core Logic**: The agent needs to interpret user requests for directory changes and map them to calls to this tool. Crucially, after this tool successfully changes the directory, the agent's internal state (especially the system prompt which includes `cwd`) **must be updated** to reflect the new working directory. `main.py`'s `recreate_agent_with_cwd` or `smold.agent.refresh_agent_context` handles this.

This tool provides a robust and user-friendly way for the agent to manage its working directory, enhancing its ability to interact with the file system effectively and safely. The suggestions and content summaries improve the user experience when the agent uses this tool.
