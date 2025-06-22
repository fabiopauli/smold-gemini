# Overview

The `smold/tools/ls_tool.py` file defines `LSTool`, a tool for the SmolD agent to list the contents of a specified directory. Unlike a recursive tree view, this tool lists only the immediate children (files and subdirectories) of the given path. It requires an absolute path and can optionally ignore files/directories matching provided glob patterns. It also includes a safety check to warn the user if they attempt to list the root directory.

# Key Components

-   **`LSTool` class (inherits from `smolagents.Tool`)**:
    *   **`name`**: "LS"
    *   **`description`**: Explains that the tool displays a directory's immediate contents. It mandates an absolute `path` argument and mentions an optional `ignore` parameter (array of glob patterns). It suggests that `GlobTool` or `GrepTool` might be better for targeted searches if specific directories are already known.
    *   **`inputs`**:
        *   `path` (string, required): The absolute path to the directory to list.
        *   `ignore` (array of strings, optional): Glob patterns for items to ignore.
    *   **`output_type`**: "string" (a formatted string showing directories and files within the specified path).
    *   **Constants**:
        *   `MAX_FILES`: 1000 (though not directly used in the current non-recursive listing logic, it's defined).
        *   `TRUNCATED_MESSAGE`: A message for truncation if `MAX_FILES` were to be exceeded (again, less relevant for the current non-recursive implementation).
    *   **Core Logic (`forward(path: str, ignore: Optional[List[str]] = None) -> str`)**:
        1.  Ensures `path` is absolute. If not, it converts it using `os.path.abspath()`.
        2.  Validates that `path` exists and is a directory. Returns an error message if not.
        3.  **Root Directory Safety Check**: If `path` is the root directory (`/` or `os.path.sep`), it uses `user_input_tool` to ask for user confirmation before proceeding, due to potential performance issues and exposure of sensitive information. If the user denies, it returns a cancellation message.
        4.  Calls `_list_directory()` to get a list of immediate children of `path`, respecting `ignore` patterns.
        5.  Calls `_create_file_tree()` to structure this flat list (though for a non-recursive list, this structure is very simple).
        6.  Calls `_print_tree()` to format the structured list into a human-readable string.
        7.  Returns the formatted string.
    *   **Helper Methods**:
        *   `_list_directory(initial_path: str, ignore_patterns: List[str]) -> List[str]`:
            *   Uses `os.listdir(initial_path)` to get all items in the directory.
            *   For each item, checks if it should be skipped using `_should_skip()`.
            *   Sorts the remaining entries alphabetically.
            *   Converts absolute paths to paths relative to `initial_path`.
            *   Appends a trailing slash (`/`) to directory names.
            *   Returns a list of these relative path strings.
        *   `_should_skip(path: str, ignore_patterns: List[str]) -> bool`:
            *   Determines if a given `path` should be ignored.
            *   Skips hidden files/directories (starting with `.`, except `.` itself).
            *   Skips `__pycache__` directories.
            *   Skips paths matching any of the `ignore_patterns` (using `fnmatch.fnmatch`).
        *   `_create_file_tree(sorted_paths: List[str]) -> List[Dict]`:
            *   Converts the flat list of relative paths from `_list_directory` into a list of dictionaries, where each dictionary represents a file or directory with `name`, `path`, and `type` ('directory' or 'file'). For this non-recursive tool, it's essentially just reformatting the list.
        *   `_print_tree(tree: List[Dict], root_path: str, level: int = 0, prefix: str = '') -> str`:
            *   Formats the list of file/directory nodes into a string.
            *   Starts with "Contents of {root_path}:".
            *   If empty, prints "(empty directory)".
            *   Separates directories and files, listing them under "Directories (count):" and "Files (count):" headings, prefixed with folder (📁) or page (📄) emojis.

-   **`ls_tool = LSTool()`**: A global instance for easy use.

# Important Variables/Constants

-   `user_input_tool` (imported from `.user_input_tool`): Used for the root directory listing confirmation.

# Usage Examples

The agent uses this tool to explore the file system one directory level at a time.

**Agent listing a project's root directory:**

```python
# User: "List the contents of my project directory /home/user/my_project."
# Agent uses LSTool.
result = ls_tool.forward(path="/home/user/my_project")
print(result)
# Output:
# Contents of /home/user/my_project/:
#
# Directories (3):
#   📁 docs/
#   📁 src/
#   📁 tests/
#
# Files (2):
#   📄 README.md
#   📄 requirements.txt
```

**Agent listing a directory and ignoring certain files:**

```python
# User: "Show me what's in /home/user/data, but ignore all .log files and the temp/ folder."
result = ls_tool.forward(path="/home/user/data", ignore=["*.log", "temp/"])
print(result)
# Output would list contents of /home/user/data, excluding any .log files and the temp/ directory.
```

**Agent attempting to list root directory (triggering confirmation):**

```python
result = ls_tool.forward(path="/")
# User sees: "Warning: You are attempting to list the root directory... Are you sure? (yes/no)"
# If user types "no":
# Output: "Operation cancelled by user. Root directory listing was not performed."
```

# Dependencies and Interactions

-   **Standard Libraries**:
    *   `os`: Extensively used for path operations (`path.isabs`, `path.abspath`, `path.exists`, `path.isdir`, `path.normpath`, `listdir`, `path.join`, `path.relpath`, `path.basename`, `sep`).
    *   `fnmatch`: Used by `_should_skip` for glob pattern matching against ignore patterns.
-   **`smolagents.Tool`**: The base class.
-   **`smold.tools.user_input_tool.user_input_tool`**: Used to get confirmation before listing the root directory. If this tool is unavailable, the safety check for root listing might not prompt the user.
-   **Other Tools**: The description suggests `GlobTool` and `GrepTool` for more targeted searches if the agent already has an idea of what it's looking for, implying `LSTool` is more for general, immediate-level directory exploration.

This tool provides a safe and clear way for the agent to inspect the immediate contents of directories, which is fundamental for navigation and understanding the file system structure. The non-recursive nature keeps the output concise and manageable.
