# Overview

The `smold/tools/edit_tool.py` file defines `FileEditTool`, a tool for the SmolD agent to perform in-place edits to files. It can replace a specific string within a file with a new string or create a new file if `old_string` is empty and the `file_path` does not exist. The tool emphasizes making small, targeted edits and includes logic to handle whitespace differences and to remove line numbers that might be accidentally included from `ViewTool` output.

# Key Components

-   **`FileEditTool` class (inherits from `smolagents.Tool`)**:
    *   **`name`**: "Edit"
    *   **`description`**: A comprehensive guide for the LLM on how to use the tool. It specifies:
        *   When to use Edit (in-place changes) vs. Bash `mv` (renaming/moving) or WriteTool (replacing entire file).
        *   Pre-requisites: Use ViewTool to understand context, LS to confirm parent directory for new files.
        *   Required inputs: `file_path` (absolute), `old_string` (exact text to replace, NO line numbers), `new_string` (replacement text).
        *   Behavior: Replaces one occurrence of `old_string`.
        *   Critical Rules: No line numbers in `old_string`, prefer small edits (5-15 lines), automatic whitespace flexibility, verify uniqueness of `old_string` before calling.
        *   Guidance for new files: Use fresh `file_path`, empty `old_string`, full content in `new_string`.
    *   **`inputs`**:
        *   `file_path` (string, required): Absolute path to the file.
        *   `old_string` (string, required): Text to be replaced.
        *   `new_string` (string, required): Replacement text.
    *   **`output_type`**: "string" (a success/error message, often including a snippet of the edited file with line numbers).
    *   **Core Logic (`forward(file_path: str, old_string: str, new_string: str) -> str`)**:
        1.  Ensures `file_path` is absolute.
        2.  **New File Creation**: If `file_path` doesn't exist and `old_string` is empty, it creates the parent directory (if needed) and writes `new_string` to `file_path`. Returns a success message with a snippet.
        3.  **Existing File Validation**: Checks if `file_path` exists, is a file, and is writable. Returns errors if not.
        4.  Cleans `old_string` using `_remove_line_numbers()`.
        5.  Reads file content, trying multiple encodings (`utf-8`, `latin-1`, `cp1252`).
        6.  **Empty `old_string` (Append/Prepend-like behavior for existing files)**: If `cleaned_old_string` is empty, it appends `new_string` to the existing file content.
        7.  **Non-empty `old_string`**:
            *   Checks if `cleaned_old_string` is in `file_content`.
            *   If not found, it tries matching with normalized whitespace using `_normalize_whitespace()` and `_find_original_text()`.
            *   If still not found, it returns an error with suggestions via `_suggest_alternatives()`.
            *   If found, it counts occurrences. If more than one, returns an error asking for a unique `old_string`.
            *   Replaces the first occurrence of `cleaned_old_string` (or the whitespace-flexible match) with `new_string`.
        8.  Writes the `new_content` back to the file.
        9.  Generates a snippet of the modified area using `_get_snippet()` and formats the result with line numbers using `_format_result()` and `_add_line_numbers()`.
    *   **Helper Methods**:
        *   `_remove_line_numbers(text: str) -> str`: Removes leading line numbers (e.g., "123\t") from lines in `text`.
        *   `_normalize_whitespace(text: str) -> str`: Standardizes spaces, tabs, and line endings, and strips leading/trailing whitespace from lines to allow for more flexible matching.
        *   `_find_original_text(...)`: Attempts to find the original segment in `file_content` that corresponds to a `normalized_old` string found within `normalized_content`. (This is a heuristic approach).
        *   `_suggest_alternatives(...)`: Provides helpful error messages if `old_string` isn't found, including checking if line numbers were an issue and looking for lines containing parts of the `old_string`.
        *   `_get_snippet(...)`: Extracts a few lines of context around the edited section (or the beginning of the file for new files/appends).
        *   `_format_result(...)`: Creates the final success message string, including the file path and the line-numbered snippet.
        *   `_add_line_numbers(...)`: Prepends line numbers to each line of a given string.

-   **`file_edit_tool = FileEditTool()`**: A global instance for easy use.

# Important Variables/Constants

-   `MAX_DIFF_SIZE` and `DIFF_TRUNCATION_MESSAGE` are defined but not directly used in the current implementation of `FileEditTool` (they seem more relevant for a diff-based tool).

# Usage Examples

The agent uses this tool to modify file contents based on user instructions.

**Agent making a targeted change:**

```python
# User: "In main.py, change 'print(\"Hello\")' to 'print(\"Hello, World!\")'"
# Agent uses ViewTool to confirm main.py content and finds the exact string.
result = file_edit_tool.forward(
    file_path="/abs/path/to/main.py",
    old_string="print(\"Hello\")",
    new_string="print(\"Hello, World!\")"
)
# Output:
# The file /abs/path/to/main.py has been updated. Here's the result of running `cat -n` on a snippet of the edited file:
#      1	# Some code
#      2	print("Hello, World!") # Changed line
#      3	# Some other code
```

**Agent creating a new file:**

```python
# User: "Create a new file named 'config.txt' with 'debug=true'."
result = file_edit_tool.forward(
    file_path="/abs/path/to/config.txt",
    old_string="",
    new_string="debug=true"
)
# Output:
# The file /abs/path/to/config.txt has been updated. Here's the result of running `cat -n` on a snippet of the edited file:
#      1	debug=true
```

**Agent encounters an error (old_string not found):**

```python
result = file_edit_tool.forward(
    file_path="/abs/path/to/main.py",
    old_string="print(\"NonExistent\")",
    new_string="print(\"SomeValue\")"
)
# Output might be:
# Error: The specified text was not found in the file.
#
# Suggestions:
# • ... (suggestions based on content)
#
# Consider:
# • Using the View tool to see the actual file content...
```

# Dependencies and Interactions

-   **Standard Libraries**:
    *   `os`: Extensive use for file operations (checking existence, type, writability, paths, making directories).
    *   `difflib`: (Imported but not directly used in the provided code for `FileEditTool`. Could be for a planned diff feature).
    *   `re`: Used by `_remove_line_numbers` and `_normalize_whitespace` for pattern matching and substitution.
    *   `pathlib.Path`: (Imported but standard `os.path` functions are predominantly used).
-   **`smolagents.Tool`**: The base class.
-   **Other Tools**:
    *   **ViewTool**: The description strongly advises the LLM to use ViewTool before EditTool to get the correct `old_string`.
    *   **LSTool**: Advised for confirming parent directory existence before creating new files.
    *   **WriteTool**: Suggested as an alternative for replacing an entire file's content.
    *   **BashTool (with `mv`)**: Suggested for renaming or moving files.

This tool is critical for enabling the agent to modify code and other text files. Its detailed description and error handling (especially around string matching and line numbers) aim to guide the LLM towards successful and precise edits. The whitespace normalization adds a degree of robustness to the matching process.
