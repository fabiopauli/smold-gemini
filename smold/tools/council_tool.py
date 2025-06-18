"""
Council Tool - Integrate council.py functionality as a smolagents Tool.

This tool provides access to a council of AI specialists (OpenAI o4-mini, Gemini 2.5 Pro, 
and DeepSeek Reasoner) for expert technical consultation directly from within SmolD.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
from smolagents import Tool

# Add the smold directory to the path to import council
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from council import CouncilConsultation
except ImportError as e:
    print(f"Warning: Could not import council functionality: {e}")
    CouncilConsultation = None

# Import user input tool for confirmation
try:
    from .user_input_tool import user_input_tool
except ImportError:
    user_input_tool = None


def consult_council(prompt: str, context: str = "", context_file: str = "") -> str:
    """
    Consult the Council of AI Specialists for expert technical advice.
    
    Args:
        prompt: The main question or request for the council
        context: Additional context information (optional)
        context_file: Path to a file with context information (optional)
    
    Returns:
        Formatted response from all three AI specialists
    """
    if CouncilConsultation is None:
        return "Error: Council consultation is not available. Missing dependencies or import failed."
    
    try:
        # Initialize the council
        council = CouncilConsultation()
        council.initialize_clients()
        
        # Prepare consultation content
        content = council.prepare_consultation_content(
            prompt=prompt,
            context=context,
            context_file=context_file
        )
        
        # Run parallel consultation
        openai_response, gemini_response, deepseek_response = council.run_parallel_consultation(content)
        
        # Format and return results
        formatted_response = council.format_council_response(openai_response, gemini_response, deepseek_response)
        
        # Optionally save consultation log
        try:
            council.save_consultation_log(content, formatted_response)
        except Exception as log_error:
            print(f"Warning: Could not save consultation log: {log_error}")
        
        return formatted_response
        
    except Exception as e:
        return f"Error during council consultation: {str(e)}"


class CouncilConsultationTool(Tool):
    """
    Tool for consulting a council of AI specialists for expert technical advice.
    """
    name = "council_consultation"
    description = """Consult a council of AI specialists (OpenAI o4-mini, Gemini 2.5 Pro, and DeepSeek Reasoner) for expert technical advice and superior recommendations.

This tool provides access to three advanced AI models working in parallel to give comprehensive technical guidance, architectural insights, and best practices.

IMPORTANT: This tool requires user confirmation before proceeding, as it makes API calls to external services and consumes API credits.

Use this when you need:
- Expert technical advice on complex problems
- Architectural guidance and design reviews
- Advanced reasoning for algorithm design
- Multiple perspectives on technical decisions
- Best practices recommendations
- Code optimization strategies

The council provides superior advice through diverse expertise:
- OpenAI o4-mini: General software engineering expertise
- Gemini 2.5 Pro: Advanced reasoning with search capabilities  
- DeepSeek Reasoner: Deep analytical reasoning and problem solving"""
    
    inputs = {
        "prompt": {
            "type": "string", 
            "description": "The main question or request for the council of AI specialists"
        },
        "context": {
            "type": "string", 
            "description": "Additional context information to help the specialists understand the problem better (optional)",
            "nullable": True
        },
        "context_file": {
            "type": "string", 
            "description": "Path to a file containing context information (markdown, text, code, etc.) - optional",
            "nullable": True
        }
    }
    output_type = "string"

    def forward(self, prompt: str, context: str = "", context_file: str = "") -> str:
        """
        Consult the Council of AI Specialists for expert technical advice.
        
        Args:
            prompt: The main question or request for the council
            context: Additional context information (optional)
            context_file: Path to a file with context information (optional)
        
        Returns:
            Formatted response from all three AI specialists
        """
        # User confirmation for council consultation
        if user_input_tool is not None:
            confirmation = user_input_tool.forward(
                "Council Consultation Request: You are about to consult a council of AI specialists "
                "(OpenAI o4-mini, Gemini 2.5 Pro, and DeepSeek Reasoner) for expert technical advice. "
                "This will make API calls to external services and may consume API credits. "
                "Are you sure you want to proceed with the council consultation? (yes/no)"
            )
            if confirmation.lower() not in ['yes', 'y']:
                return "Council consultation cancelled by user. No API calls were made to external services."
        
        return consult_council(prompt, context, context_file)


# Create the tool instance
council_tool = CouncilConsultationTool()