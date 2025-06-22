# Overview

The `smold/council.py` script implements a "Council of AI Specialists." Its purpose is to provide enhanced advice or solutions by querying multiple Large Language Models (LLMs) in parallel and then presenting their combined outputs. This script is designed to be callable both as a standalone utility and potentially integrated as a tool by the main SmolD agent (via `council_tool.py`). It queries OpenAI's `o4-mini`, Google's `gemini-2.5-pro`, and `deepseek-reasoner` to get diverse perspectives on a given prompt and context.

# Key Components

-   **`CouncilConsultation` class**:
    *   **Initialization (`__init__`, `initialize_clients`)**: Loads API keys from environment variables (using `.env` files) and initializes API clients for OpenAI, Google Gemini, and DeepSeek. It also sets up a `tiktoken` tokenizer for token counting.
    *   **Context Handling (`read_context_file`, `prepare_consultation_content`)**:
        *   `read_context_file`: Reads text content from a specified file path to be used as context.
        *   `prepare_consultation_content`: Combines the user's prompt, any direct context string, and content from a context file into a single input string for the LLMs. It also performs token counting using `num_tokens_from_messages` to ensure the input doesn't exceed the `max_tokens` limit (60,000).
    *   **Token Counting (`count_tokens`, `num_tokens_from_messages`)**:
        *   `count_tokens`: Basic token counting for a string.
        *   `num_tokens_from_messages`: More accurate token counting for message-based API structures, accounting for roles and message overhead. Uses `gpt-4o-mini` encoding as a reference.
    *   **LLM API Calls**:
        *   `call_openai_o3(content)`: Sends the content to OpenAI's `o4-mini` model.
        *   `call_gemini_pro(content)`: Sends the content to Google's `gemini-2.5-pro` model, enabling Google Search tool and streaming the response.
        *   `call_deepseek_reasoner(content)`: Sends the content to the `deepseek-reasoner` model.
        *   Each of these methods formats a specific system prompt tailored to the specialist role of the respective AI.
    *   **Parallel Execution (`run_parallel_consultation`)**: Uses `concurrent.futures.ThreadPoolExecutor` to run the three LLM API calls concurrently, improving overall response time.
    *   **Response Formatting (`format_council_response`)**: Combines the responses from the three LLMs into a single, well-formatted string, clearly attributing each part to its source specialist. Includes a timestamp and a summary.
    *   **Logging (`save_consultation_log`)**: Saves the original request and the formatted council responses to a timestamped Markdown file in a `consultation` subdirectory.

-   **`main()` function**:
    *   Handles command-line argument parsing using `argparse`. Arguments include `--prompt` (required), `--context` (optional), and `--context-file` (optional).
    *   Instantiates `CouncilConsultation`, initializes clients, prepares content, runs the parallel consultation, prints the formatted response, and saves the log.
    *   Includes error handling for invalid arguments, keyboard interrupts, and general exceptions.

# Important Variables/Constants

-   **API Keys**: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY` (loaded from `.env`).
-   **`tokenizer` (in `CouncilConsultation`)**: `tiktoken` tokenizer instance, typically using `gpt-4o-mini`'s encoding.
-   **`max_tokens` (in `CouncilConsultation`)**: Set to 60,000, the maximum token limit for the input content.
-   **LLM Models**:
    *   OpenAI: `o4-mini`
    *   Google: `gemini-2.5-pro`
    *   DeepSeek: `deepseek-reasoner`

# Usage Examples

**Command-line usage:**

1.  **Simple prompt:**
    ```bash
    python smold/council.py --prompt "What are the best practices for API security?"
    ```

2.  **Prompt with additional context:**
    ```bash
    python smold/council.py --prompt "How to refactor this Python class for better testability?" --context "The class currently has many private methods and tight coupling."
    ```

3.  **Prompt with context from a file:**
    ```bash
    python smold/council.py --prompt "Suggest improvements for the following code:" --context-file "path/to/your/code.py"
    ```

4.  **Prompt with both file and string context:**
    ```bash
    python smold/council.py --prompt "Develop a migration strategy." --context-file "docs/legacy_system_architecture.md" --context "Target platform is AWS cloud."
    ```

The script will output the formatted responses from all three AI specialists to the console and save a log file in `smold/consultation/`.

# Dependencies and Interactions

-   **External Libraries**:
    *   `python-dotenv`: For loading environment variables from `.env` files.
    *   `tiktoken`: For tokenizing text to estimate API usage and enforce limits.
    *   `openai`: The official OpenAI Python client library.
    *   `google-generativeai` (as `google.genai`): The official Google Gemini Python client library.
-   **Standard Libraries**:
    *   `argparse`: For command-line argument parsing.
    *   `asyncio`: (Although `concurrent.futures` is used for parallelism, asyncio might be implicitly used by client libraries or planned for future use).
    *   `os`: For environment variable access and path manipulation.
    *   `sys`: For exiting the script (`sys.exit`).
    *   `pathlib`: For object-oriented path manipulation.
    *   `concurrent.futures`: For running LLM calls in parallel using a thread pool.
    *   `json`: (Potentially used by underlying API clients).
    *   `datetime`: For timestamping responses and log files.
-   **Environment Variables**: Requires `OPENAI_API_KEY`, `GEMINI_API_KEY`, and `DEEPSEEK_API_KEY` to be set, typically in a `.env` file at the project root or in the same directory as `council.py`.
-   **`council_tool.py`**: This script is designed to be invoked by `council_tool.py`, which acts as a tool interface for the main SmolD agent, allowing the agent to request consultation from the council.

The council script is a powerful utility for getting comprehensive and diverse AI-generated advice by leveraging the strengths of multiple specialized models. Its parallel execution model ensures timely responses.
