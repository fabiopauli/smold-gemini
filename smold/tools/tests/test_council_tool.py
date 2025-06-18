"""
Tests for the Council Tool.

Note: These tests mock the council functionality to avoid requiring API keys during testing.
"""

import unittest
import sys
from unittest.mock import Mock, patch
from pathlib import Path

# Add the parent directory to the path to import council_tool
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from smold.tools.council_tool import council_tool, consult_council, CouncilConsultationTool
except ImportError:
    council_tool = None
    consult_council = None
    CouncilConsultationTool = None


class TestCouncilTool(unittest.TestCase):
    """Test cases for the Council Tool."""
    
    def test_council_tool_exists(self):
        """Test that the council tool is properly defined."""
        self.assertIsNotNone(council_tool, "Council tool should be importable")
        self.assertEqual(council_tool.name, "council_consultation")
        self.assertIn("expert technical advice", council_tool.description.lower())
    
    def test_council_tool_inputs(self):
        """Test that the council tool has correct input specifications."""
        self.assertIn("prompt", council_tool.inputs)
        self.assertIn("context", council_tool.inputs)
        self.assertIn("context_file", council_tool.inputs)
        
        # Check input types
        self.assertEqual(council_tool.inputs["prompt"]["type"], "string")
        self.assertEqual(council_tool.inputs["context"]["type"], "string")
        self.assertEqual(council_tool.inputs["context_file"]["type"], "string")
    
    def test_council_tool_output_type(self):
        """Test that the council tool has correct output type."""
        self.assertEqual(council_tool.output_type, "string")
    
    @patch('smold.tools.council_tool.CouncilConsultation')
    def test_consult_council_success(self, mock_council_class):
        """Test successful council consultation with mocked responses."""
        # Setup mock council instance
        mock_council = Mock()
        mock_council_class.return_value = mock_council
        
        # Mock the consultation process
        mock_council.prepare_consultation_content.return_value = "test content"
        mock_council.run_parallel_consultation.return_value = (
            "OpenAI response", 
            "Gemini response", 
            "DeepSeek response"
        )
        mock_council.format_council_response.return_value = "Formatted council response"
        mock_council.save_consultation_log.return_value = None
        
        # Test the function
        result = consult_council("Test prompt", "Test context")
        
        # Verify the result
        self.assertEqual(result, "Formatted council response")
        
        # Verify the mocks were called correctly
        mock_council_class.assert_called_once()
        mock_council.initialize_clients.assert_called_once()
        mock_council.prepare_consultation_content.assert_called_once_with(
            prompt="Test prompt",
            context="Test context", 
            context_file=""
        )
        mock_council.run_parallel_consultation.assert_called_once_with("test content")
        mock_council.format_council_response.assert_called_once_with(
            "OpenAI response", 
            "Gemini response", 
            "DeepSeek response"
        )
    
    def test_consult_council_missing_dependencies(self):
        """Test council consultation when dependencies are missing."""
        # This test simulates the case where CouncilConsultation is None
        with patch('smold.tools.council_tool.CouncilConsultation', None):
            result = consult_council("Test prompt")
            self.assertIn("Council consultation is not available", result)
    
    @patch('smold.tools.council_tool.CouncilConsultation')
    def test_consult_council_error_handling(self, mock_council_class):
        """Test error handling in council consultation."""
        # Setup mock to raise an exception
        mock_council_class.side_effect = Exception("Test error")
        
        result = consult_council("Test prompt")
        
        self.assertIn("Error during council consultation", result)
        self.assertIn("Test error", result)
    
    @patch('smold.tools.council_tool.CouncilConsultation')
    def test_consult_council_with_context_file(self, mock_council_class):
        """Test council consultation with context file."""
        # Setup mock council instance
        mock_council = Mock()
        mock_council_class.return_value = mock_council
        
        mock_council.prepare_consultation_content.return_value = "content with file"
        mock_council.run_parallel_consultation.return_value = ("", "", "")
        mock_council.format_council_response.return_value = "Response with file context"
        
        result = consult_council("Test prompt", "Test context", "/path/to/file.md")
        
        # Verify context file was passed correctly
        mock_council.prepare_consultation_content.assert_called_once_with(
            prompt="Test prompt",
            context="Test context",
            context_file="/path/to/file.md"
        )
        
        self.assertEqual(result, "Response with file context")
    
    def test_council_tool_is_instance(self):
        """Test that the council tool is properly instantiated."""
        self.assertIsInstance(council_tool, CouncilConsultationTool)
        self.assertTrue(hasattr(council_tool, 'forward'))
        self.assertTrue(callable(council_tool.forward))


if __name__ == "__main__":
    # Run tests if this file is executed directly
    unittest.main()