# Overview

The `smold/tools/user_input_tool.py` file defines the `UserInputTool`. This simple but crucial tool allows the SmolD agent to pause its execution and request direct input from the human user. It's a fundamental component for enabling human-in-the-loop interactions, allowing the agent to ask clarifying questions, seek confirmation, or request information it cannot obtain otherwise.

# Key Components

-   **`UserInputTool` class (inherits from `smolagents.Tool`)**:
    *   **`name`**: "UserInput"
    *   **`description`**: "Ask the user a question and get their response. Use this when you need information from the user to proceed." This clearly states the tool's purpose to the LLM.
    *   **`inputs`**:
        *   `question` (string, required): The question that the agent wants to ask the user.
    *   **`output_type`**: "string" (The user's textual response).
    *   **`forward(self, question: str) -> str` method**:
        *   This is the core method called by the agent.
        *   It takes the `question` string as input.
        *   It prints the question to the console, prefixed with `\n[USER INPUT REQUESTED]`, to clearly indicate to the user that their input is needed.
        *   It then uses the built-in `input("> ")` function to capture the user's typed response from the command line.
        *   It returns the user's response as a string.

-   **`user_input_tool = UserInputTool()`**: A global instance of the tool is created, making it readily available for the agent to use.

# Important Variables/Constants

-   None specific to this tool beyond standard tool attributes.

# Usage Examples

The agent would use this tool whenever it encounters ambiguity, needs a decision, or requires data it cannot access through other tools.

**Agent asking for clarification:**

```python
# Agent's thought process: "The user asked to 'delete the file', but there are two files named 'output.txt' in different subdirectories. I need to ask which one."
# Agent calls UserInputTool:
question_to_user = "There are two files named 'output.txt': './src/output.txt' and './data/output.txt'. Which one do you want to delete?"
user_response = user_input_tool.forward(question=question_to_user)

# Console output seen by user:
# [USER INPUT REQUESTED] There are two files named 'output.txt': './src/output.txt' and './data/output.txt'. Which one do you want to delete?
# >

# User types: ./src/output.txt
# 'user_response' variable now holds "./src/output.txt"
# Agent can now proceed with deleting the specified file.
```

**Agent asking for confirmation before a destructive action:**

```python
# Agent is about to use PowerShellTool to run 'Remove-Item -Recurse -Force ./temp_folder'
# Agent's thought process: "This is a destructive command. I should confirm with the user."
confirmation_question = "You asked to delete the './temp_folder' and all its contents. This action is irreversible. Are you sure you want to proceed? (yes/no)"
user_confirmation = user_input_tool.forward(question=confirmation_question)

# Console output seen by user:
# [USER INPUT REQUESTED] You asked to delete the './temp_folder' and all its contents. This action is irreversible. Are you sure you want to proceed? (yes/no)
# >

# User types: yes
# Agent checks if user_confirmation.lower() == 'yes' and proceeds if true.
```
This tool is also used by `smold.tools.council_tool.py` to ask for user confirmation before making external API calls.

# Dependencies and Interactions

-   **Standard Libraries**:
    *   None beyond built-in `input()`.
-   **`smolagents.Tool`**: The base class from which `UserInputTool` inherits.
-   **Agent Core Logic**: The SmolD agent's decision-making process determines when to invoke this tool. The agent must be able to parse the user's string response and use it to continue its task.
-   **Other Tools**:
    *   `CouncilConsultationTool`: Uses `UserInputTool` to ask for confirmation before proceeding with potentially costly API calls.
    *   `LSTool`: Uses `UserInputTool` to ask for confirmation before listing the contents of the root directory.

The `UserInputTool` is essential for making the agent more interactive, safer, and robust by allowing it to resolve ambiguities or get necessary permissions directly from the user. It bridges the gap between autonomous operation and user guidance.
