# Overview

The `smold/tools/grep_tool.py` file defines `GrepTool`, a tool for the SmolD agent to search the content of files using regular expressions. It's designed for speed and scalability, allowing the agent to find files containing specific patterns. The tool can filter which files to search using glob patterns and returns a list of matching file paths, sorted by modification time (newest first).

# Key Components

-   **`GrepTool` class (inherits from `smolagents.Tool`)**:
    *   **`name`**: "GrepTool"
    *   **`description`**: Describes the tool as a fast content-search utility using standard regular expressions. It highlights the ability to narrow the search by file glob patterns (`include` parameter) and that results are ordered by most-recent modification time. It advises using the "Agent tool" (likely `dispatch_agent` or general agent capabilities) for more complex, multi-step searches.
    *   **`inputs`**:
        *   `pattern` (string, required): The regular expression to search for within file contents.
        *   `include` (string, optional): A file glob pattern to filter which files are searched (e.g., `*.py`, `src/**/*.{ts,tsx}`).
        *   `path` (string, optional): The directory to search in; defaults to the current working directory.
    *   **`output_type`**: "string" (a message indicating the number of files found, followed by a newline-separated list of their paths, potentially with a truncation message).
    *   **Core Logic (`forward(pattern: str, include: Optional[str] = None, path: Optional[str] = None) -> str`)**:
        1.  Sets the `search_path` (defaults to `os.getcwd()`, ensures it's absolute).
        2.  Compiles the input `pattern` into a regular expression object (`re.compile`). Returns an error if the regex is invalid.
        3.  Finds all files to be searched within `search_path` that match the `include` glob pattern using `_find_files()`.
        4.  If no files are found to search, returns "No files found".
        5.  Iterates through the list of files to search:
            *   For each file, calls `_file_contains_pattern()` to check if its content matches the compiled `regex`.
            *   Collects paths of files that contain the pattern.
        6.  Sorts the list of `matching_files` by modification time (newest first).
        7.  Truncates the list of `matching_files` to a maximum of 100.
        8.  Formats the result string: "Found X file(s)\npath1\npath2..." with a truncation message if applicable. If no matches, returns "No files found".
    *   **File Finding Logic (`_find_files(base_path: str, include: Optional[str] = None) -> List[str]`)**:
        1.  If `include` is provided:
            *   Handles brace expansion in `include` patterns (e.g., `*.{js,ts}` becomes `*.js` and `*.ts`).
            *   For each (expanded) pattern:
                *   If it contains `**` (recursive), uses `glob.glob(os.path.join(base_path, pattern), recursive=True)`.
                *   Otherwise, uses `os.walk()` and `fnmatch.fnmatch()` to find matching files.
        2.  If `include` is not provided, uses `os.walk()` to list all regular files in `base_path`.
        3.  Collects all file paths, removes duplicates, and limits the list to the first 1000 files for performance.
        4.  Returns the list of unique file paths to be searched.
    *   **Content Matching Logic (`_file_contains_pattern(file_path: str, regex: re.Pattern) -> bool`)**:
        1.  Checks if the file is binary using `_is_binary_file()`; if so, skips it.
        2.  Tries to open and read the file line by line with multiple encodings (`utf-8`, `latin-1`, `cp1252`).
        3.  For each line, performs `regex.search(line)`. If a match is found, returns `True`.
        4.  If the entire file is read without a match, or if it can't be decoded, returns `False`.
    *   **Binary File Check (`_is_binary_file(file_path: str) -> bool`)**:
        1.  Checks against a list of common binary file extensions.
        2.  Explicitly identifies a test file `test.bin` as binary.
        3.  Attempts to read a chunk of the file as UTF-8 text; if successful, it's likely not binary.
        4.  If UTF-8 decoding fails, reads a chunk in binary mode (`'rb'`) and checks for null bytes (`b'\x00'`) or a high ratio of control characters, which are strong indicators of binary content.
        5.  Returns `True` if the file appears binary, `False` otherwise.

-   **`grep_tool = GrepTool()`**: A global instance for easy registration and use.

# Important Variables/Constants

-   None explicitly defined as top-level constants in the file, but limits like 100 matching files (output) and 1000 files to search (internal) are hardcoded.

# Usage Examples

The agent uses this tool to find files containing specific text or patterns.

**Agent searching for a function definition:**

```python
# User: "Find where the function 'calculate_total' is defined in Python files."
# Agent uses GrepTool.
result = grep_tool.forward(pattern=r"def\s+calculate_total\s*\(", include="*.py")
print(result)
# Output:
# Found 2 file(s)
# /abs/path/to/project/src/billing.py
# /abs/path/to/project/utils/calculations.py
# (Sorted by modification time, newest first)
```

**Agent searching for a specific log message across all files:**

```python
# User: "Show me files that log 'User authentication failed'."
result = grep_tool.forward(pattern="User authentication failed")
print(result)
# Output:
# Found 1 file(s)
# /abs/path/to/project/logs/app.log
```

# Dependencies and Interactions

-   **Standard Libraries**:
    *   `os`: Used for path manipulation, walking directories (`os.walk`), checking file types (`os.path.isfile`), and getting modification times (`os.path.getmtime`).
    *   `re`: Core library for compiling and using regular expressions.
    *   `glob` (as `glob_module`): Used for handling recursive glob patterns (`**`) in the `include` filter.
    *   `fnmatch`: Used for non-recursive glob pattern matching against filenames within `os.walk`.
    *   `time`: Used to calculate execution time (though not currently part of the string output).
    *   `pathlib.Path`: (Imported but `os.path` functions are predominantly used).
-   **`smolagents.Tool`**: The base class.
-   **Other Tools**: The description suggests that for more complex, multi-step exploratory searches, the "Agent tool" (likely `dispatch_agent` or general agent capabilities) should be used, implying GrepTool is for more direct, single-shot content searching.

This tool provides a powerful content searching capability for the agent, leveraging regular expressions for flexibility and glob patterns for targeted file selection. The binary file detection helps avoid errors and performance issues when searching large projects.
