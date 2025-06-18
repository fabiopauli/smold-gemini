"""
Google GenAI model wrapper that implements the smolagents model interface.
This provides better performance and official API support for Gemini models.
"""

import os
from typing import List, Dict, Any, Optional, Iterator
from google import genai
from google.genai import types
from smolagents.models import Model, ChatMessage, TokenUsage


class GoogleGenAIModel(Model):
    """Google GenAI model implementation that integrates with smolagents."""
    
    def __init__(
        self,
        model_id: str = "gemini-2.5-pro",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        thinking_budget: int = -1,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Google GenAI model.
        
        Args:
            model_id: Model identifier (e.g., "gemini-2.5-pro", "gemini-2.5-flash")
            api_key: Google GenAI API key (defaults to GEMINI_API_KEY env var)
            temperature: Sampling temperature
            thinking_budget: Thinking budget for reasoning (-1 for unlimited)
            system_prompt: System prompt to use
            **kwargs: Additional arguments
        """
        self.model_id = model_id
        self.temperature = temperature
        self.thinking_budget = thinking_budget
        self.system_prompt = system_prompt
        self.system = system_prompt  # Alias for compatibility
        
        # Initialize the Google GenAI client
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable or api_key parameter is required")
        
        self.client = genai.Client(api_key=api_key)
        
        # Store additional config for generate_content
        self.extra_kwargs = kwargs
        
        # Required attributes for smolagents tool calling
        self.tool_name_key = "name"
        self.tool_arguments_key = "arguments"
    
    def generate(
        self,
        messages: List[Dict[str, Any]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        **kwargs
    ) -> ChatMessage:
        """
        Generate a response from the model (required by smolagents).
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            stop_sequences: Stop sequences (not supported by Google GenAI)
            grammar: Grammar specification (not supported by Google GenAI)
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response text
        """
        # Convert messages to Google GenAI format
        contents = self._convert_messages_to_contents(messages)
        
        # Ensure we have at least one content message
        if not contents:
            # Create a default user message if no valid contents
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text="Hello, please respond.")]
            )]
        
        # Create generation config
        config = self._create_generation_config(**kwargs)
        
        try:
            # Use non-streaming API for better reliability initially
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=config
            )
            
            # Extract text from response and convert to ChatMessage
            response_text = ""
            token_usage = None
            
            if hasattr(response, 'text') and response.text:
                response_text = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                # Handle structured response
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    parts = candidate.content.parts if hasattr(candidate.content, 'parts') else [candidate.content]
                    text_parts = []
                    for part in parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    response_text = "\n".join(text_parts).strip()
            
            # Extract token usage if available
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                token_usage = TokenUsage(
                    input_tokens=getattr(usage, 'prompt_token_count', 0),
                    output_tokens=getattr(usage, 'candidates_token_count', 0)
                )
            
            # Fallback if no text found
            if not response_text:
                response_text = "No response generated"
            
            # Return ChatMessage object
            return ChatMessage(
                role="assistant",
                content=response_text,
                raw=response,
                token_usage=token_usage
            )
            
        except Exception as e:
            # Add more detailed error information
            error_msg = f"Google GenAI API error: {str(e)}"
            if "json" in str(e).lower() or "expecting property name" in str(e).lower():
                error_msg += "\n(This might be a temporary API issue - try again)"
            raise RuntimeError(error_msg)
    
    def __call__(
        self,
        messages: List[Dict[str, Any]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        **kwargs
    ) -> ChatMessage:
        """
        Compatibility method that calls generate().
        """
        return self.generate(messages, stop_sequences, grammar, **kwargs)
    
    def _convert_messages_to_contents(self, messages: List[Dict[str, Any]]) -> List[types.Content]:
        """Convert smolagents message format to Google GenAI contents format."""
        contents = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            # Skip system messages - they'll be handled in system_instruction
            if role == "system":
                continue
            
            # Skip empty messages
            if not content or (isinstance(content, str) and not content.strip()):
                continue
            
            # Map roles to Google GenAI format
            if role == "assistant":
                genai_role = "model"
            else:  # user, tool, etc.
                genai_role = "user"
            
            # Handle different content formats
            if isinstance(content, str):
                if content.strip():  # Only add non-empty content
                    parts = [types.Part.from_text(text=content.strip())]
                else:
                    continue
            elif isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text" and item.get("text", "").strip():
                            parts.append(types.Part.from_text(text=item.get("text", "").strip()))
                        # Add support for other content types as needed
                    elif str(item).strip():
                        parts.append(types.Part.from_text(text=str(item).strip()))
                
                if not parts:  # Skip if no valid parts
                    continue
            else:
                content_str = str(content).strip()
                if content_str:
                    parts = [types.Part.from_text(text=content_str)]
                else:
                    continue
            
            contents.append(types.Content(role=genai_role, parts=parts))
        
        return contents
    
    def _create_generation_config(self, **kwargs) -> types.GenerateContentConfig:
        """Create Google GenAI generation configuration."""
        # Use provided temperature or default
        temperature = kwargs.get("temperature", self.temperature)
        
        # Create system instruction from system prompt
        system_instruction = None
        if self.system_prompt and self.system_prompt.strip():
            system_instruction = [types.Part.from_text(text=self.system_prompt.strip())]
        
        # Build config with only valid parameters
        config_params = {
            "temperature": temperature,
            "response_mime_type": "text/plain",
        }
        
        # Only add system instruction if we have one
        if system_instruction:
            config_params["system_instruction"] = system_instruction
        
        # Only add thinking config if we have a valid budget
        if self.thinking_budget is not None and self.thinking_budget != 0:
            config_params["thinking_config"] = types.ThinkingConfig(
                thinking_budget=self.thinking_budget,
            )
        
        config = types.GenerateContentConfig(**config_params)
        
        return config
    
    def set_system_prompt(self, system_prompt: str):
        """Set the system prompt for the model."""
        self.system_prompt = system_prompt
        self.system = system_prompt  # Alias for compatibility
    
    def get_system_prompt(self) -> Optional[str]:
        """Get the current system prompt."""
        return self.system_prompt
    
    @property
    def model_name(self) -> str:
        """Get the model name for compatibility."""
        return self.model_id