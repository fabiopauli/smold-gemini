# Overview

The `smold/tools/council_tool.py` file defines the `CouncilConsultationTool`. This tool acts as a bridge between the main SmolD agent and the `smold/council.py` script. It allows the agent to "consult a council of AI specialists" (specifically OpenAI's `o4-mini`, Google's `gemini-2.5-pro`, and `deepseek-reasoner`) to get diverse and expert opinions on a technical prompt. The tool handles user confirmation before making external API calls due to potential costs.

# Key Components

-   **Import Handling**:
    *   It attempts to import `CouncilConsultation` from `smold.council`. If this import fails (e.g., due to missing dependencies for `council.py`), the tool will indicate that the council functionality is unavailable.
    *   It also attempts to import `user_input_tool` from `.user_input_tool` to request confirmation from the user before proceeding with the consultation.

-   **`consult_council(prompt: str, context: str = "", context_file: str = "") -> str` function**:
    *   This is a helper function that encapsulates the logic of interacting with the `CouncilConsultation` class from `smold/council.py`.
    *   If `CouncilConsultation` is not available, it returns an error message.
    *   Otherwise, it:
        1.  Initializes `CouncilConsultation` and its API clients.
        2.  Prepares the content for the LLMs using `council.prepare_consultation_content()`.
        3.  Runs the parallel consultation using `council.run_parallel_consultation()`.
        4.  Formats the combined response using `council.format_council_response()`.
        5.  Attempts to save a log of the consultation using `council.save_consultation_log()`.
        6.  Returns the formatted response string or an error message if an exception occurs.

-   **`CouncilConsultationTool` class (inherits from `smolagents.Tool`)**:
    *   **`name`**: "council_consultation"
    *   **`description`**: Explains that the tool consults a council of AI specialists (OpenAI o4-mini, Gemini 2.5 Pro, DeepSeek Reasoner) for expert technical advice. It emphasizes that this involves external API calls, consumes credits, and thus requires user confirmation. It lists scenarios where this tool is useful (complex problems, architectural guidance, multiple perspectives, etc.) and highlights the different strengths of the council members.
    *   **`inputs`**:
        *   `prompt` (string, required): The main question for the council.
        *   `context` (string, optional): Additional textual context.
        *   `context_file` (string, optional): Path to a file containing further context.
    *   **`output_type`**: "string" (the combined formatted response from the council or an error/cancellation message).
    *   **`forward(self, prompt: str, context: str = "", context_file: str = "") -> str` method**:
        *   This is the method called by the agent to execute the tool.
        *   **User Confirmation**: If `user_input_tool` is available, it first prompts the user to confirm the consultation, explaining that it involves external API calls and potential costs. If the user does not confirm (input is not "yes" or "y"), it returns a cancellation message.
        *   If confirmed (or if `user_input_tool` is not available), it calls the `consult_council` helper function with the provided arguments and returns its result.

-   **`council_tool = CouncilConsultationTool()`**: A global instance of the tool is created for easy registration with the agent.

# Important Variables/Constants

-   None specific to this file beyond what's defined in `smolagents.Tool` or imported from `council.py`.

# Usage Examples

The SmolD agent would invoke this tool when the user's query suggests a need for in-depth technical analysis, architectural advice, or when comparing different approaches would be beneficial.

**Agent's internal call (conceptual):**

```python
# User asks: "What are the pros and cons of using microservices vs. a monolith for a new e-commerce platform?"
# Agent decides this is a good candidate for council consultation.

tool_input = {
    "prompt": "Analyze the pros and cons of microservices vs. monolith architecture for a new e-commerce platform, considering scalability, development complexity, and operational overhead.",
    "context": "The platform is expected to handle high traffic during peak seasons and should support rapid feature development."
}

# Assuming 'council_tool' is an available tool instance
result = council_tool.forward(**tool_input)

# If user_input_tool is available, the user would first see:
# "Council Consultation Request: You are about to consult a council of AI specialists... Are you sure you want to proceed? (yes/no)"
# User types: yes

# Then, 'result' would contain the combined formatted output from OpenAI o4-mini, Gemini 2.5 Pro, and DeepSeek Reasoner.
print(result)
```

# Dependencies and Interactions

-   **`smold.council.CouncilConsultation`**: This is the core dependency that provides the actual multi-LLM consultation logic. The tool will not function if `council.py` or its own dependencies (like `openai`, `google-generativeai`, `tiktoken`) are missing.
-   **`smold.tools.user_input_tool.user_input_tool`**: An optional dependency used to get explicit user confirmation before making potentially costly API calls.
-   **`smolagents.Tool`**: The base class from which `CouncilConsultationTool` inherits.
-   **Standard Libraries**:
    *   `os`: (Indirectly via `council.py`).
    *   `sys`: Used to modify `sys.path` to ensure `council.py` can be imported.
    *   `tempfile`: (Indirectly via `council.py` if it were to use temporary files, though the current `council.py` writes directly to a log).
    *   `pathlib.Path`: Used for path manipulation for the `sys.path` modification.
-   **External API Services**: The tool, through `council.py`, makes API calls to:
    *   OpenAI (for `o4-mini`)
    *   Google Cloud (for `gemini-2.5-pro`)
    *   DeepSeek (for `deepseek-reasoner`)
    This requires the respective API keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`) to be correctly configured in the environment (e.g., via a `.env` file).

This tool significantly enhances the agent's problem-solving capabilities by allowing it to tap into the collective intelligence of multiple advanced LLMs, providing more robust and well-rounded advice for complex technical queries. The user confirmation step is an important consideration for managing API costs.
