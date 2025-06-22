# Overview

The `smold/tools/glob_tool.py` file defines `GlobTool`, a tool for the SmolD agent to find files using glob pattern matching. It's designed to be fast and scalable. The tool searches for files based on a given glob pattern (e.g., `**/*.py`, `src/**/*.ts`) within a specified directory (defaulting to the current working directory). Results are returned sorted by modification time (newest first) and can be truncated if too many files match. It also includes logic to handle some Node.js-style glob patterns like brace expansion (`{js,ts}`) and optional groups (`?(x)`).

# Key Components

-   **`GlobTool` class (inherits from `smolagents.Tool`)**:
    *   **`name`**: "GlobTool"
    *   **`description`**: Describes the tool as a fast file-pattern matcher for any codebase size, understanding glob expressions, returning results sorted by last-modified time (descending). Advises using it for locating files by name patterns and suggests using the "Agent tool" (likely referring to `dispatch_agent` or a more general agent capability) for complex multi-step searches.
    *   **`inputs`**:
        *   `pattern` (string, required): The glob pattern (e.g., `**/*.js`).
        *   `path` (string, optional): The directory to search in; defaults to the current working directory.
    *   **`output_type`**: "string" (a newline-separated list of matching file paths, potentially with a truncation message).
    *   **Core Logic (`forward(pattern: str, path: Optional[str] = None) -> str`)**:
        1.  Sets the `search_path` (defaults to `os.getcwd()`, ensures it's absolute).
        2.  Calls `_find_matching_files()` to get the initial list of matches (limited to 100 by default).
        3.  **Smart Fallback**: If no files are found and the `pattern` looks like a simple filename (e.g., `README.md`, checked by `_is_simple_filename_pattern()`), it automatically retries the search with a recursive pattern like `**/{pattern}`.
        4.  Formats the list of files into a newline-separated string using `_format_result_for_assistant()`.
        5.  The description mentions returning structured data like `durationMs`, `numFiles`, `truncated` but the `forward` method currently returns only the formatted string.
    *   **File Matching Logic (`_find_matching_files(pattern: str, search_path: str, limit: int = 100, offset: int = 0) -> Tuple[List[str], bool]`)**:
        1.  **Pattern Expansion**:
            *   Handles brace expansion (e.g., `**/*config*.{js,json,ts}` becomes multiple patterns).
            *   Handles Node.js-style optional groups like `**/*.ts?(x)` (becomes patterns for `**/*.ts` and `**/*.tsx`).
        2.  Iterates through the (potentially expanded) patterns:
            *   If a pattern contains `**` (recursive), it uses `glob.glob(os.path.join(search_path, p), recursive=True)`.
            *   Otherwise, it uses `pathlib.Path(search_path).glob(p)`.
        3.  Collects all matches, ensuring only files (not directories) are included.
        4.  Removes duplicates.
        5.  Sorts the unique matches by modification time in descending order (newest first).
        6.  Applies pagination (`offset` and `limit`) and determines if the result set was `truncated`.
        7.  Returns the list of paginated file paths and the `truncated` boolean flag.
    *   **Helper Methods**:
        *   `_is_simple_filename_pattern(pattern: str) -> bool`: Checks if a pattern is likely a simple filename (no path separators, doesn't start with `*` or `?`) to decide if the smart recursive fallback should be applied.
        *   `_format_result_for_assistant(files: List[str], truncated: bool) -> str`: Converts the list of file paths into a newline-separated string. If `truncated` is true, appends a message about truncation.

-   **`glob_tool = GlobTool()`**: A global instance for easy registration and use.

# Important Variables/Constants

-   None explicitly defined as top-level constants in the file, but `limit=100` and `offset=0` are default parameters within `_find_matching_files`.

# Usage Examples

The agent uses this tool to find files based on patterns.

**Agent searching for Python files recursively:**

```python
# User: "Find all Python files in the project."
# Agent uses GlobTool.
result = glob_tool.forward(pattern="**/*.py")
print(result)
# Output:
# /abs/path/to/project/main.py
# /abs/path/to/project/src/utils.py
# /abs/path/to/project/src/models.py
# ... (sorted by modification time, newest first)
```

**Agent searching for specific config files in a directory:**

```python
# User: "List all .json and .yaml config files in the 'configs' directory."
# Agent uses GlobTool.
result = glob_tool.forward(pattern="*.{json,yaml}", path="./configs")
print(result)
# Output:
# /abs/path/to/project/configs/database.json
# /abs/path/to/project/configs/settings.yaml
# ...
```

**Agent searching for a simple filename (triggering smart fallback):**

```python
# Assume 'my_document.txt' exists deep within the project structure.
# User: "Find my_document.txt"
result = glob_tool.forward(pattern="my_document.txt")
# _find_matching_files initially might not find it if cwd is not the directory of the file.
# _is_simple_filename_pattern returns true.
# Retries with pattern="**/my_document.txt".
print(result)
# Output:
# /abs/path/to/project/some/nested/dir/my_document.txt
```

# Dependencies and Interactions

-   **Standard Libraries**:
    *   `glob` (as `glob_module`): Used for recursive globbing (`**`) when `recursive=True`.
    *   `os`: Used for path manipulation (`getcwd`, `path.abspath`, `path.join`, `path.isfile`, `path.getmtime`).
    *   `pathlib`: Used for `Path.glob()` for non-recursive patterns and general path object handling.
    *   `time`: Used to calculate `durationMs` (though this data isn't part of the string output of `forward`).
-   **`smolagents.Tool`**: The base class.
-   **Other Tools**: The description suggests that for more complex, multi-step exploratory searches (e.g., iterative globbing and grepping), the "Agent tool" (likely meaning `dispatch_agent` or a general agent loop) should be used, implying GlobTool is for more direct, single-shot pattern matching.

This tool provides a powerful and efficient way for the agent to locate files. The sorting by modification time is a useful heuristic for finding recently worked-on files. The handling of some Node.js-style patterns and the smart fallback for simple filenames enhance its usability.
