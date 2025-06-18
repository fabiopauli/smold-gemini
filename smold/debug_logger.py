"""
Debug logging module for SmolD
Handles saving API calls and system prompts for debugging purposes.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any


class DebugLogger:
    """Handles debug logging for API calls and system prompts."""
    
    def __init__(self, enabled: bool = False, debug_dir: str = "debug-logs"):
        self.enabled = enabled
        self.debug_dir = Path(debug_dir)
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.enabled:
            self._setup_debug_directory()
    
    def _setup_debug_directory(self):
        """Create the debug directory if it doesn't exist."""
        try:
            self.debug_dir.mkdir(exist_ok=True)
            print(f"📁 Debug logging enabled. Logs will be saved to: {self.debug_dir}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create debug directory {self.debug_dir}: {e}")
            self.enabled = False
    
    def log_system_prompt(self, system_prompt: str):
        """Save the system prompt to a file."""
        if not self.enabled:
            return
        
        try:
            filename = f"system_prompt_{self.session_id}.txt"
            filepath = self.debug_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"SMOLD SYSTEM PROMPT - {datetime.datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                f.write(system_prompt)
                f.write("\n\n" + "=" * 80 + "\n")
                f.write("END OF SYSTEM PROMPT\n")
                f.write("=" * 80 + "\n")
            
            print(f"🐛 System prompt saved to: {filepath}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save system prompt: {e}")
    
    def log_api_call(self, query: str, response: str, call_number: int = 1, full_context: str = None):
        """Save an API call (query and response) to a file."""
        if not self.enabled:
            return
        
        try:
            filename = f"api_call_{self.session_id}_{call_number:03d}.txt"
            filepath = self.debug_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"SMOLD API CALL #{call_number} - {datetime.datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("USER QUERY:\n")
                f.write("-" * 40 + "\n")
                f.write(query)
                f.write("\n\n")
                
                if full_context:
                    f.write("COMPLETE API REQUEST CONTEXT:\n")
                    f.write("-" * 40 + "\n")
                    f.write(full_context)
                    f.write("\n\n")
                
                f.write("ASSISTANT RESPONSE:\n")
                f.write("-" * 40 + "\n")
                f.write(response)
                f.write("\n\n")
                
                f.write("=" * 80 + "\n")
                f.write(f"END OF API CALL #{call_number}\n")
                f.write("=" * 80 + "\n")
            
            print(f"🐛 API call #{call_number} saved to: {filepath}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save API call: {e}")
    
    def log_full_conversation_context(self, messages: list, call_number: int = 1):
        """Save the complete conversation context (messages) sent to the API."""
        if not self.enabled:
            return
        
        try:
            filename = f"full_context_{self.session_id}_{call_number:03d}.json"
            filepath = self.debug_dir / filename
            
            debug_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "call_number": call_number,
                "complete_conversation_context": messages
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False)
            
            # Also create a human-readable text version
            txt_filename = f"full_context_{self.session_id}_{call_number:03d}.txt"
            txt_filepath = self.debug_dir / txt_filename
            
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"COMPLETE API CONTEXT #{call_number} - {datetime.datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, message in enumerate(messages):
                    f.write(f"MESSAGE {i+1} ({message.get('role', 'unknown')}):\n")
                    f.write("-" * 50 + "\n")
                    content = message.get('content', '')
                    if isinstance(content, list):
                        # Handle cases where content is a list of parts
                        for part in content:
                            if isinstance(part, dict) and 'text' in part:
                                f.write(part['text'])
                            else:
                                f.write(str(part))
                    else:
                        f.write(str(content))
                    f.write("\n\n")
                
                f.write("=" * 80 + "\n")
                f.write(f"END OF COMPLETE CONTEXT #{call_number}\n")
                f.write("=" * 80 + "\n")
            
            print(f"🐛 Full context #{call_number} saved to: {filepath} and {txt_filepath}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save full context: {e}")
    
    
    def log_raw_api_request(self, messages: list, call_number: int, kwargs: dict = None):
        """Log the raw API request that gets sent to the model."""
        if not self.enabled:
            return
        
        try:
            filename = f"raw_api_request_{self.session_id}_{call_number:03d}.json"
            filepath = self.debug_dir / filename
            
            debug_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "call_number": call_number,
                "messages": messages,
                "kwargs": kwargs or {}
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Also create a human-readable text version
            txt_filename = f"raw_api_request_{self.session_id}_{call_number:03d}.txt"
            txt_filepath = self.debug_dir / txt_filename
            
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"RAW API REQUEST #{call_number} - {datetime.datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("ADDITIONAL PARAMETERS:\n")
                f.write("-" * 40 + "\n")
                f.write(json.dumps(kwargs or {}, indent=2))
                f.write("\n\n")
                
                f.write("MESSAGES SENT TO API:\n")
                f.write("-" * 40 + "\n")
                
                for i, message in enumerate(messages):
                    role = message.get('role', 'unknown')
                    content = message.get('content', '')
                    
                    f.write(f"\n[MESSAGE {i+1}] ROLE: {role.upper()}\n")
                    f.write("-" * 30 + "\n")
                    
                    if isinstance(content, list):
                        # Handle cases where content is a list of parts
                        for j, part in enumerate(content):
                            f.write(f"[PART {j+1}]\n")
                            if isinstance(part, dict) and 'text' in part:
                                f.write(part['text'])
                            else:
                                f.write(str(part))
                            f.write("\n")
                    else:
                        f.write(str(content))
                    f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"END OF RAW API REQUEST #{call_number}\n")
                f.write("=" * 80 + "\n")
            
            print(f"🐛 Raw API request #{call_number} saved to: {filepath} and {txt_filepath}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save raw API request: {e}")
    
    def log_raw_api_response(self, response, call_number: int):
        """Log the raw API response from the model."""
        if not self.enabled:
            return
        
        try:
            filename = f"raw_api_response_{self.session_id}_{call_number:03d}.json"
            filepath = self.debug_dir / filename
            
            debug_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "call_number": call_number,
                "response": response
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"🐛 Raw API response #{call_number} saved to: {filepath}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save raw API response: {e}")
    
    def log_tool_calls(self, tool_calls: list, call_number: int = 1):
        """Save tool calls information to a JSON file."""
        if not self.enabled or not tool_calls:
            return
        
        try:
            filename = f"tool_calls_{self.session_id}_{call_number:03d}.json"
            filepath = self.debug_dir / filename
            
            debug_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "call_number": call_number,
                "tool_calls": tool_calls
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False)
            
            print(f"🐛 Tool calls #{call_number} saved to: {filepath}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save tool calls: {e}")
    
    def log_context_info(self, context_info: Dict[str, Any]):
        """Save context manager information."""
        if not self.enabled:
            return
        
        try:
            filename = f"context_info_{self.session_id}.json"
            filepath = self.debug_dir / filename
            
            debug_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "context_info": context_info
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False)
            
            print(f"🐛 Context info saved to: {filepath}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save context info: {e}")


# Global debug logger instance
_debug_logger = None


def get_debug_logger() -> DebugLogger:
    """Get the global debug logger instance."""
    global _debug_logger
    if _debug_logger is None:
        _debug_logger = DebugLogger()
    return _debug_logger


def initialize_debug_logger(enabled: bool = False, debug_dir: str = "debug-logs") -> DebugLogger:
    """Initialize the global debug logger."""
    global _debug_logger
    _debug_logger = DebugLogger(enabled=enabled, debug_dir=debug_dir)
    return _debug_logger