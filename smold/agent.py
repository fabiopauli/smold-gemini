import os
import platform
import importlib.util
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel


# Import system prompt utilities
from smold.system_prompt import get_system_prompt
from smold.context_manager import ContextManager
from smold.debug_logger import get_debug_logger

# Initialize environment variables
load_dotenv()

def import_tool_safely(module_path, tool_name):
    """Safely import a tool from a specific file path."""
    try:
        spec = importlib.util.spec_from_file_location(f"smold.tools.{tool_name}", module_path)
        if spec is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, tool_name, None)
    except Exception as e:
        print(f"Warning: Could not import {tool_name} from {module_path}: {e}")
        return None

def get_available_tools():
    """Get all available tools for the current platform."""
    tools = []
    
    # Get the tools directory path
    tools_dir = os.path.join(os.path.dirname(__file__), "tools")
    
    # List of tools to try importing (filename, tool_instance_name)
    tool_configs = [
        ("cd_tool.py", "cd_tool"),
        ("edit_tool.py", "file_edit_tool"),
        ("glob_tool.py", "glob_tool"),
        ("grep_tool.py", "grep_tool"),
        ("ls_tool.py", "ls_tool"),
        ("replace_tool.py", "write_tool"),
        ("view_tool.py", "view_tool"),
        ("user_input_tool.py", "user_input_tool"),
        ("council_tool.py", "council_tool"),
    ]
    
    # Add platform-specific shell tools
    if platform.system() == 'Windows':
        # On Windows, use PowerShell tool
        tool_configs.append(("powershell_tool.py", "powershell_tool"))
        print("Note: Using PowerShell tool on Windows")
    else:
        # On Unix-like systems, use bash tool
        tool_configs.append(("bash_tool.py", "bash_tool"))
        print("Note: Using Bash tool on Unix-like system")
    
    for filename, tool_name in tool_configs:
        tool_path = os.path.join(tools_dir, filename)
        if os.path.exists(tool_path):
            tool = import_tool_safely(tool_path, tool_name)
            if tool is not None:
                tools.append(tool)
                print(f"✓ Loaded {tool_name}")
            else:
                print(f"✗ Failed to load {tool_name}")
        else:
            print(f"✗ Tool file not found: {tool_path}")
    
    return tools

def refresh_agent_context(agent, new_cwd=None):
    """Refresh the agent's system prompt with updated directory context without full recreation."""
    if new_cwd is None:
        new_cwd = os.getcwd()
    
    # Generate new system prompt with updated context
    new_system_prompt = get_system_prompt(new_cwd)
    
    # Update the model's system prompt (overrides any smolagents default)
    agent.model.system = new_system_prompt
    
    # If agent has a context manager, update it too
    if hasattr(agent, 'context_manager'):
        agent.context_manager.refresh_with_system_prompt(new_system_prompt)
    
    # Log the updated system prompt if debug is enabled
    if hasattr(agent, 'debug_logger'):
        agent.debug_logger.log_system_prompt(new_system_prompt)
    
    return agent

class SmolDAgent:
    """Enhanced ToolCallingAgent with conversation history and context management."""
    
    def __init__(self, tools, model, max_interactions=10, max_context_tokens=100000, system_prompt=None, base_agent=None):
        # Use provided base_agent or create a new one
        if base_agent:
            self.base_agent = base_agent
        else:
            self.base_agent = ToolCallingAgent(tools=tools, model=model)
        
        self.context_manager = ContextManager(max_interactions, max_context_tokens)
        self.model = model  # Keep reference for compatibility
        self.debug_logger = get_debug_logger()
        self.call_counter = 0
        
        # Set custom system prompt if provided (overrides smolagents default)
        if system_prompt:
            # Set the system prompt on LiteLLMModel
            if hasattr(self.model, 'system_prompt'):
                self.model.system_prompt = system_prompt
            if hasattr(self.model, 'system'):
                self.model.system = system_prompt
            
            if hasattr(self.base_agent, 'system_prompt'):
                self.base_agent.system_prompt = system_prompt
            
            self.context_manager.set_system_prompt(system_prompt)
            # Log system prompt if debug is enabled
            self.debug_logger.log_system_prompt(system_prompt)
        elif hasattr(model, 'system') and model.system:
            self.context_manager.set_system_prompt(model.system)
            # Log system prompt if debug is enabled
            self.debug_logger.log_system_prompt(model.system)
    
    def run(self, query: str, **kwargs) -> str:
        """
        Run a query with conversation history context.
        
        Args:
            query: User query to process
            **kwargs: Additional arguments passed to base agent
            
        Returns:
            Assistant response
        """
        try:
            # Increment call counter for debug logging
            self.call_counter += 1
            
            # Set reset=False to maintain conversation state in the base agent
            # The base agent will use its internal history since reset=False.
            # No need to manually build an enhanced_query with past context.
            kwargs.setdefault('reset', False)
            
            # Show context info for debugging if we have history
            if not self.context_manager.conversation.is_empty():
                print(f"[CONTEXT] {self.context_manager.conversation.get_context_summary()}")
            
            # The base_agent's history is implicitly managed by its own run method calls.
            # Your context manager's role is to keep track of token counts and decide when to clear.
            
            response = self.base_agent.run(query, **kwargs)
            
            # Log the API call if debug is enabled
            self.debug_logger.log_api_call(query, response, self.call_counter)
            
            # Log tool calls if available and debug is enabled
            if hasattr(self.base_agent, 'tool_calls') and self.base_agent.tool_calls:
                self.debug_logger.log_tool_calls(self.base_agent.tool_calls, self.call_counter)
            
            # Add the interaction to your context manager for token tracking.
            self.context_manager.add_interaction(query, response)
            
            return response
            
        except Exception as e:
            print(f"Error in SmolDAgent.run: {e}")
            # Fallback to basic agent run
            response = self.base_agent.run(query, **kwargs)
            self.context_manager.add_interaction(query, response)
            # Still log the API call even if there was an error
            self.debug_logger.log_api_call(query, response, self.call_counter)
            return response
    
    
    def clear_conversation(self):
        """Clear conversation history in both the context manager and the base agent."""
        self.context_manager.clear_conversation()
        # Also reset the history of the underlying agent.
        if hasattr(self.base_agent, 'history'):
            self.base_agent.history = []
        # Some agents might store history differently, try common attributes
        if hasattr(self.base_agent, 'chat_history'):
            self.base_agent.chat_history = []
        if hasattr(self.base_agent, 'messages'):
            self.base_agent.messages = []
        print("[CONTEXT] Conversation history cleared")
    
    def get_context_info(self) -> Dict[str, Any]:
        """Get information about current context state."""
        context_info = self.context_manager.get_context_info()
        # Log context info if debug is enabled
        self.debug_logger.log_context_info(context_info)
        return context_info
    
    # Delegate other methods to base agent for compatibility
    def __getattr__(self, name):
        return getattr(self.base_agent, name)


def create_agent(cwd=None, debug=False, use_pro=False):
    """Create a tool-calling agent with conversation history and context management."""
    if cwd is None:
        cwd = os.getcwd()
    
    # Initialize debug logger if debug mode is enabled
    if debug:
        from smold.debug_logger import initialize_debug_logger
        initialize_debug_logger(enabled=True)
    
    # Get the dynamic system prompt
    system_prompt = get_system_prompt(cwd)
    
    # Select model based on pro flag
    max_tokens = 600000  # Both models get same context limit
    
    if use_pro:
        print("🚀 Using Gemini 2.5 Pro model (LiteLLM, higher quality, slower)")
        model_id = "gemini/gemini-2.5-pro"
    else:
        print("⚡ Using Gemini 2.5 Flash model (LiteLLM, faster)")
        model_id = "gemini/gemini-2.5-flash"
    
    # Use LiteLLM for both models
    agent_model = LiteLLMModel(
        model_id=model_id,  # LiteLLM format for Gemini
        api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Set system prompt on the LiteLLM model
    agent_model.system_prompt = system_prompt
    agent_model.system = system_prompt
    if hasattr(agent_model, '_system_prompt'):
        agent_model._system_prompt = system_prompt
    
    # Also monkey patch the model's get_system_prompt method if it exists
    if hasattr(agent_model, 'get_system_prompt'):
        agent_model.get_system_prompt = lambda: system_prompt
    
    # Patch litellm.completion for all models (now using LiteLLM for both)
    try:
        import litellm
        original_completion = litellm.completion
        call_counter = 0
        
        def smart_completion_wrapper(*args, **kwargs):
            nonlocal call_counter
            call_counter += 1
            
            # FORCE: Override ALL system messages with our single custom system prompt
            messages = kwargs.get('messages', [])
            if messages and system_prompt:
                # Remove ALL existing system messages and add only our custom one
                new_messages = []
                system_msg_count = 0
                
                # Count existing system messages before removal
                for msg in messages:
                    if msg.get('role') == 'system':
                        system_msg_count += 1
                
                # Add our custom system message first
                new_messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
                
                # Add all non-system messages, preserving their content structure
                for msg in messages:
                    if msg.get('role') != 'system':
                        new_messages.append(msg)
                    elif debug:
                        # Log the system messages we're removing for debugging
                        removed_content = msg.get('content', '')
                        if isinstance(removed_content, list) and removed_content:
                            removed_content = str(removed_content[0].get('text', ''))
                        elif isinstance(removed_content, str):
                            removed_content = removed_content
                        print(f"🐛 Debug: Removed system message: {removed_content[:100]}...")
                
                kwargs['messages'] = new_messages
                
                if debug:
                    print(f"🐛 Debug: Removed {system_msg_count} existing system messages")
                    print(f"🐛 Debug: Added 1 custom system message ({len(system_prompt)} chars)")
                    print(f"🐛 Debug: Final message count: {len(new_messages)}")
            
            # Also check if there's a separate 'system' parameter and override it
            if 'system' in kwargs and system_prompt:
                kwargs['system'] = system_prompt
                if debug:
                    print(f"🐛 Debug: Also overrode 'system' parameter in kwargs")
            
            # If debug mode is enabled, add logging
            if debug:
                debug_logger = get_debug_logger()
                model = kwargs.get('model', 'unknown')
                print(f"🐛 Debug: Intercepted litellm.completion call #{call_counter}")
                print(f"🐛 Debug: Model: {model}")
                
                # Get messages for logging (after system prompt override)
                current_messages = kwargs.get('messages', [])
                print(f"🐛 Debug: Messages count: {len(current_messages)}")
                system_count = len([msg for msg in current_messages if msg.get('role') == 'system'])
                print(f"🐛 Debug: {system_count} system messages in kwargs")
                
                # Log the raw API request (after override)
                debug_logger.log_raw_api_request(current_messages, call_counter, kwargs)
                
                # Also log the complete conversation context with CORRECTED system prompt
                debug_logger.log_full_conversation_context(current_messages, call_counter)
            
            # Call the original completion function
            response = original_completion(*args, **kwargs)
            
            # If debug mode is enabled, log response
            if debug:
                debug_logger.log_raw_api_response(response, call_counter)
            
            return response
        
        # Monkey patch litellm.completion
        litellm.completion = smart_completion_wrapper
        if debug:
            print("🐛 Debug: Successfully patched litellm.completion for API call logging and deduplication")
        
    except ImportError:
        if debug:
            print("🐛 Debug: Warning - Could not import litellm for API call patching")
    except Exception as e:
        if debug:
            print(f"🐛 Debug: Error setting up litellm patch: {e}")
    
    # Get available tools for this platform
    tools = get_available_tools()
    
    if not tools:
        raise RuntimeError("No tools available! Check your tool imports.")
    
    print(f"\nLoaded {len(tools)} tools successfully")
    
    # Create the base ToolCallingAgent (system prompt will be handled via model and wrapper)
    base_agent = ToolCallingAgent(
        tools=tools, 
        model=agent_model
    )
    
    # Override the system prompt in the base agent after creation
    if hasattr(base_agent, 'system_prompt'):
        base_agent.system_prompt = system_prompt
    if hasattr(base_agent, '_system_prompt'):
        base_agent._system_prompt = system_prompt
    
    # Also try to override any system prompt generation methods
    if hasattr(base_agent, 'get_system_prompt'):
        base_agent.get_system_prompt = lambda: system_prompt
    
    # Create enhanced agent with conversation history, wrapping the base agent
    agent = SmolDAgent(
        tools=tools,
        model=agent_model,
        max_interactions=10,
        max_context_tokens=max_tokens,
        system_prompt=system_prompt,  # Pass custom system prompt
        base_agent=base_agent  # Pass the pre-configured base agent
    )
    
    return agent

def main():
    """Run the SmolD agent with a sample query."""
    # Example query - can be changed as needed
    query = "What files are in the current directory?"
    
    # Create the agent with the current working directory
    agent = create_agent()
    
    print(f"\nQuery: {query}\n")
    answer = agent.run(query)
    print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    main()