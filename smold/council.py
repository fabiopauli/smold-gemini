#!/usr/bin/env python3
"""
Council of AI Specialists - Superior Advice Consultation Script

This script makes parallel API calls to OpenAI o4-mini and Google Gemini 2.5 Pro 
to provide superior advice to a code agent through a council of specialists.

Usage:
    python council.py --prompt "Your question here" --context "Additional context"
    python council.py --context-file "path/to/file.md" --prompt "Your question"
    python council.py --context-file "file.txt" --context "Extra context" --prompt "Question"
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, List
import concurrent.futures
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Resolve the path to the .env file at the root
try:
    dotenv_path = Path(__file__).resolve().parents[2] / '.env'
    if not dotenv_path.exists():
        # Fallback: use .env in the same directory as this file
        dotenv_path = Path(__file__).resolve().parent / '.env'
    load_dotenv(dotenv_path)
except Exception as e:
    print(f"Warning: Could not load .env from project root: {e}")
    # Fallback: try loading from current working directory
    try:
        load_dotenv()
        print("Loaded .env from current working directory as fallback.")
    except Exception as e2:
        print(f"Warning: Could not load .env from current working directory: {e2}")

# Third-party imports
try:
    import tiktoken
    from openai import OpenAI
    from google import genai
    from google.genai import types
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Please install required packages:")
    print("pip install openai google-genai tiktoken")
    sys.exit(1)


class CouncilConsultation:
    """Council of AI Specialists for superior advice consultation."""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.openai_client = None
        self.gemini_client = None
        self.deepseek_client = None

        # Use encoding_for_model for better model alignment
        # o4-mini uses the same encoding as gpt-4o-mini (o200k_base)
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        except KeyError:
            print("Warning: unknown model gpt-4o-mini. Using o200k_base encoding.")
            self.tokenizer = tiktoken.get_encoding("o200k_base")
        self.max_tokens = 60000
        
    def initialize_clients(self):
        """Initialize API clients with proper error handling."""
        try:
            # Initialize OpenAI client
            if not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.openai_client = OpenAI()
            
            # Initialize Gemini client
            if not os.environ.get("GEMINI_API_KEY"):
                raise ValueError("GEMINI_API_KEY environment variable not set")
            self.gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

            # Initialize DeepSeek client
            if not os.environ.get("DEEPSEEK_API_KEY"):
                raise ValueError("DEEPSEEK_API_KEY environment variable not set")
            self.deepseek_client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

            

            
        except Exception as e:
            print(f"Error initializing API clients: {e}")
            sys.exit(1)
    
    def read_context_file(self, file_path: str) -> str:
        """Read content from a context file."""
        try:
            # Check if file exists in current directory first
            if not os.path.isabs(file_path):
                current_dir_file = Path.cwd() / file_path
                if current_dir_file.exists():
                    file_path = str(current_dir_file)
            
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Context file not found: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"[OK] Loaded context file: {file_path} ({len(content)} characters)")
            return content
            
        except Exception as e:
            print(f"Error reading context file: {e}")
            sys.exit(1)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text using tiktoken."""
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            print(f"Error counting tokens: {e}")
            return 0
    
    def num_tokens_from_messages(self, messages, model="o4-mini"):
        """Return the number of tokens used by a list of messages."""
        # Map o4-mini to gpt-4o-mini for tiktoken compatibility
        tiktoken_model = "gpt-4o-mini" if model == "o4-mini" else model
        
        try:
            encoding = tiktoken.encoding_for_model(tiktoken_model)
        except KeyError:
            print(f"Warning: unknown model {model}. Using o200k_base encoding.")
            encoding = tiktoken.get_encoding("o200k_base")
        
        # Use known defaults matching OpenAI's published specs
        tokens_per_message = 3
        tokens_per_name = 1
        
        total = 0
        for msg in messages:
            total += tokens_per_message
            for k, v in msg.items():
                if isinstance(v, str):
                    total += len(encoding.encode(v))
                elif isinstance(v, list):
                    # Handle content arrays (like in o4-mini format)
                    for item in v:
                        if isinstance(item, dict) and 'text' in item:
                            total += len(encoding.encode(item['text']))
                if k == "name":
                    total += tokens_per_name
        total += 3  # assistant reply preamble
        return total
    
    def prepare_consultation_content(self, prompt: str, context: str = "", context_file: str = "") -> str:
        """Prepare and validate the consultation content."""
        content_parts = []
        
        # Add context from file if provided
        if context_file:
            file_content = self.read_context_file(context_file)
            content_parts.append(f"Context from file ({context_file}):\n{file_content}")
        
        # Add additional context if provided
        if context:
            content_parts.append(f"Additional context:\n{context}")
        
        # Add the main prompt
        content_parts.append(f"Question/Request:\n{prompt}")
        
        # Combine all content
        full_content = "\n\n" + "="*50 + "\n\n".join(content_parts)
        
        # Count tokens more accurately for message-based APIs
        # Create a sample message structure to get accurate token count
        sample_messages = [
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"""Act as a senior software engineer and technical architect.
                        
You are part of an elite council of AI specialists providing superior advice to a code agent.
Your role is to provide expert technical guidance, architectural insights, and best practices.
Be thorough, precise, and actionable in your recommendations.

{full_content}"""
                    }
                ]
            }
        ]
        
        token_count = self.num_tokens_from_messages(sample_messages, "o4-mini")
        print(f"Total token count (accurate): {token_count:,}")
        
        if token_count > self.max_tokens:
            print(f"Error: Content exceeds maximum token limit of {self.max_tokens:,} tokens")
            print(f"Current content has {token_count:,} tokens")
            sys.exit(1)
        
        return full_content
    
    def call_openai_o3(self, content: str) -> str:
        """Make API call to OpenAI o4-mini."""
        try:
            print("[AI] Consulting OpenAI o4-mini...")
            
            response = self.openai_client.responses.create(
                model="o4-mini",
                input=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "input_text",
                                "text": f"""Act as a senior software engineer and technical architect.
                                
You are part of an elite council of AI specialists providing superior advice to a code agent.
Your role is to provide expert technical guidance, architectural insights, and best practices.
Be thorough, precise, and actionable in your recommendations.

{content}"""
                            }
                        ]
                    }
                ],
                text={
                    "format": {
                        "type": "text"
                    }
                },
                reasoning={
                    "effort": "medium"
                },
                tools=[],
                store=True
            )
            
            # Extract the actual response content using output_text
            if hasattr(response, 'output_text') and response.output_text:
                return response.output_text
            elif hasattr(response, 'output') and response.output:
                # Fallback: extract from output array
                text_parts = []
                for item in response.output:
                    if hasattr(item, 'content') and item.content:
                        text_parts.append(item.content)
                return '\n'.join(text_parts) if text_parts else "No content in output"
            else:
                return f"Unable to extract response content. Status: {getattr(response, 'status', 'unknown')}"
            
        except Exception as e:
            return f"Error calling OpenAI o4-mini: {str(e)}"
    
    def call_gemini_pro(self, content: str) -> str:
        """Make API call to Gemini 2.5 Pro."""
        try:
            print("[GEMINI] Consulting Gemini 2.5 Pro...")
            
            model = "gemini-2.5-pro"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=content),
                    ],
                ),
            ]
            
            tools = [
                types.Tool(google_search=types.GoogleSearch()),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=0.65,
                tools=tools,
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text="""You are a senior software engineer and system architect.
                    
You are part of an elite council of AI specialists providing superior advice to a code agent.
Your expertise spans multiple programming languages, system design, performance optimization, 
and software engineering best practices. Provide detailed, actionable advice with code examples 
when appropriate."""),
                ],
            )
            
            # Collect streaming response
            response_text = ""
            for chunk in self.gemini_client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if hasattr(chunk, 'text') and chunk.text:
                    response_text += chunk.text
            
            return response_text if response_text else "No response received from Gemini"
            
        except Exception as e:
            return f"Error calling Gemini 2.5 Pro: {str(e)}"
    
    def call_deepseek_reasoner(self, content: str) -> str:
        """Make API call to DeepSeek Reasoner."""
        try:
            print("[DEEPSEEK] Consulting DeepSeek Reasoner...")
            
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a senior software engineer and system architect with deep reasoning capabilities.
                        
You are part of an elite council of AI specialists providing superior advice to a code agent.
Your expertise spans algorithm design, system optimization, mathematical modeling, and complex problem-solving.
Use your reasoning capabilities to provide thorough analysis, consider edge cases, and offer innovative solutions.
Be methodical, analytical, and provide step-by-step reasoning when appropriate."""
                    },
                    {
                        "role": "user", 
                        "content": content
                    }
                ],
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error calling DeepSeek Reasoner: {str(e)}"
    
    def run_parallel_consultation(self, content: str) -> Tuple[str, str, str]:
        """Run all three API calls in parallel."""
        print("\n[COUNCIL] Convening the Council of AI Specialists...\n")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all three API calls
            openai_future = executor.submit(self.call_openai_o3, content)
            gemini_future = executor.submit(self.call_gemini_pro, content)
            deepseek_future = executor.submit(self.call_deepseek_reasoner, content)
            
            # Wait for all to complete
            openai_response = openai_future.result()
            gemini_response = gemini_future.result()
            deepseek_response = deepseek_future.result()
        
        return openai_response, gemini_response, deepseek_response
    
    def format_council_response(self, openai_response: str, gemini_response: str, deepseek_response: str) -> str:
        """Format the council's collective response."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        formatted_response = f"""
{'='*80}
[COUNCIL] AI SPECIALISTS - CONSULTATION REPORT
{'='*80}
Timestamp: {timestamp}

{'='*35} SPECIALIST 1: OpenAI o4-mini {'='*30}
{openai_response}

{'='*35} SPECIALIST 2: Gemini 2.5 Pro {'='*30}
{gemini_response}

{'='*35} SPECIALIST 3: DeepSeek Reasoner {'='*28}
{deepseek_response}

{'='*80}
[SUMMARY] COUNCIL SUMMARY:
Three specialists have provided their expert analysis above. Consider synthesizing 
their recommendations to make the most informed decision for your code agent.
- OpenAI o4-mini: General software engineering expertise
- Gemini 2.5 Pro: Advanced reasoning with search capabilities  
- DeepSeek Reasoner: Deep analytical reasoning and problem solving
{'='*80}
"""
        return formatted_response
    
    def save_consultation_log(self, consultation_content: str, responses: str):
        """Save consultation to a log file."""
        try:
            log_dir = Path(__file__).resolve().parent / "consultation"
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"council_consultation_{timestamp}.md"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("# Council Consultation Log\n\n")
                f.write("## Original Request\n\n")
                f.write(f"```\n{consultation_content}\n```\n\n")
                f.write("## Council Responses\n\n")
                f.write(responses)
            
            print(f"\n[SAVED] Consultation saved to: {log_file}")
            
        except Exception as e:
            print(f"Warning: Could not save consultation log: {e}")


def main():
    """Main function to handle command line arguments and run consultation."""
    parser = argparse.ArgumentParser(
        description="Council of AI Specialists - Superior Advice Consultation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python council.py --prompt "How can I optimize this database query?"
  python council.py --prompt "Review my architecture" --context "Using microservices"
  python council.py --context-file "code.py" --prompt "How can I improve this code?"
  python council.py --context-file "docs/design.md" --context "Legacy system" --prompt "Migration strategy?"
        """
    )
    
    parser.add_argument(
        "--prompt",
        required=True,
        help="The main question or request for the council"
    )
    
    parser.add_argument(
        "--context",
        default="",
        help="Additional context information"
    )
    
    parser.add_argument(
        "--context-file",
        default="",
        help="Path to a markdown or text file with context (can be in current directory)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.prompt.strip():
        print("Error: --prompt cannot be empty")
        sys.exit(1)
    
    # Initialize and run consultation
    council = CouncilConsultation()
    council.initialize_clients()
    
    try:
        # Prepare consultation content
        content = council.prepare_consultation_content(
            prompt=args.prompt,
            context=args.context,
            context_file=args.context_file
        )
        
        # Run parallel consultation
        openai_response, gemini_response, deepseek_response = council.run_parallel_consultation(content)
        
        # Format and display results
        formatted_response = council.format_council_response(openai_response, gemini_response, deepseek_response)
        print(formatted_response)
        
        # Save consultation log
        council.save_consultation_log(content, formatted_response)
        
        print("\n[SUCCESS] Council consultation completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Consultation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Consultation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()