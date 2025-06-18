import sys
import os
import argparse
import traceback
from smold import create_agent
from smold.agent import refresh_agent_context
from smold.tools.ls_tool import ls_tool

def print_welcome():
    """Print welcome message with usage information."""
    print("🤖 Welcome to SmolD - A Smart Code Assistant")
    print("=" * 50)
    print()
    print("SmolD is a lightweight code assistant powered by Google Gemini")
    print("with intelligent tool-using capabilities for file operations,")
    print("code analysis, and project management.")
    print()
    print("📋 USAGE:")
    print("  python main.py \"your question\"        # Ask a single question")
    print("  python main.py -i                      # Interactive mode")
    print("  python main.py --cwd /path \"question\"  # Set working directory")
    print()
    print("🛠️  AVAILABLE TOOLS:")
    print("  • File Operations: read, edit, create files")
    print("  • Directory Management: list, navigate, change working directory")
    print("  • Code Search: find files, search content with regex")
    print("  • Shell Commands: execute bash/PowerShell commands")
    print("  • Project Analysis: understand code structure and patterns")
    print("  • Council Consultation: get expert advice from AI specialists")
    print("  • Dual LLM Models: Flash (fast) and Pro (high-quality reasoning)")
    print()
    print("💡 EXAMPLE QUERIES:")
    print('  "What files are in the current directory?"')
    print('  "Find all Python files containing TODO comments"')
    print('  "Create a new README.md file for this project"')
    print('  "Change to the src directory and list its contents"')
    print('  "Run the tests and show me the results"')
    print()
    print("🤖 MODEL OPTIONS:")
    print("  python main.py \"query\"           # Use Gemini Flash (fast)")
    print("  python main.py --pro \"query\"     # Use Gemini Pro (higher quality)")
    print("  In interactive mode: type 'pro' to switch models")
    print()
    print("🔧 COMMAND LINE OPTIONS:")
    print("  -i, --interactive    Start interactive mode for multiple queries")
    print("  --cwd PATH          Set the working directory for the agent")
    print("  -d, --debug         Enable debug mode with API call logging")
    print("  --pro               Use Gemini 2.5 Pro model (higher quality, slower)")
    print("  -h, --help          Show detailed help message")
    print()
    print("🚀 To get started, try: python main.py -i")
    print("=" * 50)

def main():
    """
    Main entry point for SmolD.
    Handles command line arguments and runs the agent.
    """
    parser = argparse.ArgumentParser(
        description="SmolD - A lightweight code assistant with tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "What files are in this directory?"
  python main.py -i
  python main.py --cwd /path/to/project "analyze this codebase"
  
For more information, visit: https://github.com/aniemerg/smold
        """
    )
    parser.add_argument("query", nargs="*", help="Query to send to the assistant")
    parser.add_argument("-i", "--interactive", action="store_true", 
                        help="Run in interactive mode (prompt for queries)")
    parser.add_argument("--cwd", help="Set the working directory for the agent")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose error reporting with full tracebacks")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug mode with detailed error information and API call logging")
    parser.add_argument("--pro", action="store_true",
                        help="Use Gemini 2.5 Pro model instead of Flash (higher quality, slower)")
    
    args = parser.parse_args()
    
    # Show welcome message if no arguments are provided at all
    if len(sys.argv) == 1:
        print_welcome()
        return
    
    # Set the working directory if provided
    working_dir = args.cwd if args.cwd else os.getcwd()
    
    # Actually change to the working directory if specified
    if args.cwd:
        try:
            os.chdir(working_dir)
            print(f"📁 Changed to working directory: {working_dir}")
        except (FileNotFoundError, PermissionError) as e:
            print(f"❌ Error: Cannot change to directory '{working_dir}': {e}")
            return
    
    try:
        # Create the agent with the appropriate working directory
        print("🔧 Initializing SmolD agent...")
        agent = create_agent(os.getcwd(), debug=args.debug, use_pro=args.pro) # Use os.getcwd() as we've already chdir'd
        print(f"📁 You are in the {os.getcwd()} working directory")
        if args.debug:
            print("🐛 Debug mode enabled - API calls will be saved to debug-logs/")
        print()
        
        # Handle the query based on arguments
        if args.query:
            query = " ".join(args.query)
            print(f"❓ Query: {query}")
            
            # Handle ls command locally without API call
            if query.strip().lower() in ("ls", "dir"):
                try:
                    result = ls_tool.forward(os.getcwd())
                    print("📋 Directory contents:")
                    print(result)
                except Exception as e:
                    print(f"❌ Error listing directory: {e}")
            else:
                print("🤔 Processing...")
                print()
                result = agent.run(query)
                print("📋 Response:")
                print(result)
        else:
            # If no query is provided, default to interactive mode.
            # This covers `main.py -i` and `main.py --cwd /some/path`.
            initial_model = "Pro" if args.pro else "Flash"
            run_interactive_mode(agent, args.verbose or args.debug, args.debug, initial_model)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        
        if args.verbose or args.debug:
            print("\n📋 Full traceback:")
            traceback.print_exc()
        
        if args.debug:
            print(f"\n🔍 Debug info:")
            print(f"  Python version: {sys.version}")
            print(f"  Working directory: {os.getcwd()}")
            print(f"  Command line args: {sys.argv}")
        
        sys.exit(1)

def recreate_agent_with_cwd(new_cwd, current_agent=None, debug_mode=False):
    """Recreate the agent with a new working directory and updated context."""
    try:
        os.chdir(new_cwd)
        print(f"📁 Changed to working directory: {os.getcwd()}")
        
        # Try to use the more efficient refresh method if agent is provided
        if current_agent is not None:
            print("🔄 Refreshing agent context...")
            updated_agent = refresh_agent_context(current_agent, os.getcwd())
            print("✅ Agent context refreshed successfully")
            return updated_agent
        else:
            # Fallback to full recreation
            print("🔄 Creating new agent with directory context...")
            agent = create_agent(os.getcwd(), debug=debug_mode)
            print("✅ Agent context updated successfully")
            return agent
    except (FileNotFoundError, PermissionError) as e:
        print(f"❌ Error: Cannot change to directory '{new_cwd}': {e}")
        return None

def run_interactive_mode(agent, verbose_errors=False, debug_mode=False, current_model="Flash"):
    """Run SmolD in interactive mode, prompting for queries."""
    print("🚀 SmolD Interactive Mode")
    print("=" * 40)
    print("💬 Enter your queries and I'll help you with:")
    print("   • File operations and code analysis")
    print("   • Directory navigation and management") 
    print("   • Shell commands and project tasks")
    print()
    print("💡 Useful commands:")
    print('   "help" - Show available tools and capabilities')
    print('   "cd <path>" - Change working directory (updates agent context)')
    print('   "ls" or "dir" - List current directory contents (fast, no API call)')
    print('   "clear" - Clear conversation history')
    print('   "context" - Show conversation context and token usage')
    print('   "pro" - Switch between Flash and Pro models')
    print()
    print("🔚 Type 'exit', 'quit', or press Ctrl+C to end")
    if debug_mode:
        print("🐛 Debug mode is active - all API calls are being logged")
    print(f"🤖 Current model: Gemini 2.5 {current_model}")
    print("=" * 40)
    
    while True:
        try:
            query = input("\n🤖 SmolD> ")
            if query.lower() in ("exit", "quit"):
                print("👋 Goodbye! Thanks for using SmolD!")
                break
            
            if not query.strip():
                continue
            
            # Handle special built-in commands
            if query.lower() == "help":
                print_help_commands()
                continue
            
            # Handle context management commands
            if query.lower() == "clear":
                agent.clear_conversation()
                continue
            
            if query.lower() == "context":
                context_info = agent.get_context_info()
                print(f"[CONTEXT INFO]")
                print(f"  Total messages: {context_info['total_messages']}")
                print(f"  Conversation interactions: {context_info['conversation_interactions']}")
                print(f"  Total tokens: {context_info['total_tokens']:,}")
                print(f"  System prompt tokens: {context_info['system_prompt_tokens']:,}")
                print(f"  Conversation tokens: {context_info['conversation_tokens']:,}")
                print(f"  Under token limit: {context_info['under_limit']}")
                continue
            
            # Handle pro command to switch models
            if query.lower() == "pro":
                current_is_pro = "pro" in agent.model.model_id.lower()
                new_use_pro = not current_is_pro
                new_model_name = "Pro" if new_use_pro else "Flash"
                
                print(f"🔄 Switching from Gemini 2.5 {current_model} to Gemini 2.5 {new_model_name}...")
                try:
                    # Create new agent with switched model
                    new_agent = create_agent(os.getcwd(), debug=debug_mode, use_pro=new_use_pro)
                    agent = new_agent
                    current_model = new_model_name
                    print(f"✅ Successfully switched to Gemini 2.5 {current_model}")
                except Exception as e:
                    print(f"❌ Error switching models: {e}")
                continue
            
            # Handle cd command to change working directory
            if query.strip().lower().startswith("cd "):
                new_path = query.strip()[3:].strip()
                if new_path:
                    # Handle relative paths and expand ~
                    new_path = os.path.expanduser(new_path)
                    if not os.path.isabs(new_path):
                        new_path = os.path.join(os.getcwd(), new_path)
                    new_path = os.path.normpath(new_path)
                    
                    new_agent = recreate_agent_with_cwd(new_path, agent, debug_mode)
                    if new_agent is not None:
                        agent = new_agent
                else:
                    print("❌ Usage: cd <directory_path>")
                continue
            
            # Handle ls command locally without API call
            if query.strip().lower() in ("ls", "dir"):
                try:
                    result = ls_tool.forward(os.getcwd())
                    print("📋 Directory contents:")
                    print(result)
                except Exception as e:
                    print(f"❌ Error listing directory: {e}")
                continue
                
            print("🤔 Processing...")
            result = agent.run(query)
            print("📋 Response:")
            print(result)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for using SmolD!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            
            if verbose_errors:
                print("\n📋 Full traceback:")
                traceback.print_exc()
                print("💡 If this error persists, try restarting SmolD or clearing conversation history with 'clear'")

def print_help_commands():
    """Print help information for interactive mode."""
    print("🛠️  Available Tools & Capabilities:")
    print("   📁 File Operations:")
    print("      • Read files: 'show me the contents of main.py'")
    print("      • Edit files: 'add a comment to line 10 in main.py'")
    print("      • Create files: 'create a new config.json file'")
    print()
    print("   📂 Directory Management:")
    print("      • List contents: 'what files are here?'")
    print("      • Change directory: 'cd /path/to/directory' or 'cd to the src folder'")
    print("      • Navigate: 'go to the parent directory'")
    print("      • Note: Use 'cd <path>' for direct directory changes that update agent context")
    print()
    print("   🧠 Context Management:")
    print("      • Clear history: 'clear' - Remove conversation history")
    print("      • View context: 'context' - Show token usage and conversation state")
    print("      • Switch models: 'pro' - Toggle between Flash (fast) and Pro (quality)")
    print("      • The agent now remembers the last 10 interactions for better context")
    print()
    print("   🔍 Code Search & Analysis:")
    print("      • Find files: 'find all Python files'")
    print("      • Search content: 'find TODO comments in the code'")
    print("      • Analyze structure: 'explain this project structure'")
    print()
    print("   ⚡ Shell Commands:")
    print("      • Run tests: 'run the test suite'")
    print("      • Git operations: 'show git status'")
    print("      • Build tools: 'run npm install'")
    print()
    print("   🎓 Council Consultation:")
    print("      • Expert advice: 'consult the council about optimization strategies'")
    print("      • Architecture guidance: 'get council advice on microservices design'")
    print("      • Best practices: 'ask the council for code review recommendations'")
    print()
    print("   🎯 Natural Language:")
    print("      Just ask naturally! 'How many Python files are in this project?'")
    print("      'Create a simple HTTP server script'")
    print("      'Fix the syntax error in utils.py'")

if __name__ == "__main__":
    main()
