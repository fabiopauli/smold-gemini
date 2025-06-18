#!/usr/bin/env python3
"""
Test suite for tiktoken functionality in council.py

Tests the token counting logic to ensure accurate token estimation
for various message formats and model types.
"""

import sys
from pathlib import Path

# Add the project root to path (go up 3 levels from tools/tests to project root)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from smold.council import CouncilConsultation


class TestCouncilTiktoken:
    """Test class for council.py tiktoken functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.council = CouncilConsultation()
    
    def test_tokenizer_initialization(self):
        """Test that tokenizer is properly initialized."""
        assert self.council.tokenizer is not None
        assert hasattr(self.council.tokenizer, 'encode')
        assert hasattr(self.council.tokenizer, 'decode')
    
    def test_count_tokens_simple_text(self):
        """Test basic token counting for simple text."""
        text = "Hello world"
        token_count = self.council.count_tokens(text)
        
        # Should be a positive integer
        assert isinstance(token_count, int)
        assert token_count > 0
        
        # Simple text should be relatively few tokens
        assert token_count < 10
    
    def test_count_tokens_empty_text(self):
        """Test token counting for empty text."""
        token_count = self.council.count_tokens("")
        assert token_count == 0
    
    def test_count_tokens_long_text(self):
        """Test token counting for longer text."""
        long_text = "This is a longer piece of text that should result in more tokens. " * 10
        token_count = self.council.count_tokens(long_text)
        
        # Should be significantly more tokens
        assert token_count > 50
    
    def test_num_tokens_from_messages_simple(self):
        """Test token counting for simple message format."""
        messages = [
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
        ]
        
        token_count = self.council.num_tokens_from_messages(messages)
        
        # Should include message overhead + content tokens
        assert isinstance(token_count, int)
        assert token_count > 6  # 3 (message overhead) + 3 (reply preamble) + content tokens
    
    def test_num_tokens_from_messages_with_name(self):
        """Test token counting with name field."""
        messages = [
            {
                "role": "user",
                "name": "TestUser",
                "content": "Hello"
            }
        ]
        
        token_count = self.council.num_tokens_from_messages(messages)
        
        # Should include extra token for name field
        messages_without_name = [
            {
                "role": "user", 
                "content": "Hello"
            }
        ]
        
        token_count_without_name = self.council.num_tokens_from_messages(messages_without_name)
        
        # Should be exactly 1 token more (for the name)
        # Note: tiktoken encoding may vary slightly, so allow for small differences
        assert token_count >= token_count_without_name + 1
    
    def test_num_tokens_from_messages_multiple(self):
        """Test token counting for multiple messages."""
        messages = [
            {
                "role": "user",
                "content": "First message"
            },
            {
                "role": "assistant", 
                "content": "Response to first message"
            },
            {
                "role": "user",
                "content": "Second message"
            }
        ]
        
        token_count = self.council.num_tokens_from_messages(messages)
        
        # Should include overhead for each message (3 * 3 = 9) + reply preamble (3) + content
        assert token_count > 12
    
    def test_num_tokens_from_messages_content_array(self):
        """Test token counting for o4-mini style content arrays."""
        messages = [
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": "This is a test message in array format"
                    }
                ]
            }
        ]
        
        token_count = self.council.num_tokens_from_messages(messages)
        
        # Should handle content arrays properly
        assert isinstance(token_count, int)
        assert token_count > 6
    
    def test_num_tokens_from_messages_different_models(self):
        """Test token counting with different model names."""
        messages = [
            {
                "role": "user",
                "content": "Test message"
            }
        ]
        
        # Test with o4-mini (default)
        tokens_o4 = self.council.num_tokens_from_messages(messages, "o4-mini")
        
        # Test with gpt-4o-mini
        tokens_gpt4o = self.council.num_tokens_from_messages(messages, "gpt-4o-mini")
        
        # Test with unknown model (should fallback)
        tokens_unknown = self.council.num_tokens_from_messages(messages, "unknown-model")
        
        # All should return reasonable token counts
        assert all(isinstance(t, int) and t > 0 for t in [tokens_o4, tokens_gpt4o, tokens_unknown])
    
    def test_prepare_consultation_content_token_counting(self):
        """Test token counting in prepare_consultation_content method."""
        prompt = "Test prompt"
        context = "Test context"
        
        # This should not raise an exception
        content = self.council.prepare_consultation_content(prompt, context)
        
        # Should return a string
        assert isinstance(content, str)
        assert len(content) > 0
        assert prompt in content
        assert context in content
    
    def test_token_count_consistency(self):
        """Test that token counting is consistent between methods."""
        text = "This is a test message for consistency checking"
        
        # Count using direct method
        direct_count = self.council.count_tokens(text)
        
        # Count using message format
        messages = [{"role": "user", "content": text}]
        message_count = self.council.num_tokens_from_messages(messages)
        
        # Message count should be higher due to overhead
        assert message_count > direct_count
        
        # The difference should be approximately the expected overhead (3 + 3 = 6)
        # Allow for slight variations in encoding
        overhead = message_count - direct_count
        assert 5 <= overhead <= 8, f"Expected overhead 5-8, got {overhead}"
    
    def test_token_limits(self):
        """Test token limit checking."""
        # Test that max_tokens is set properly
        assert self.council.max_tokens == 60000
        
        # Test with content that should be under limit
        short_content = "Short test content"
        try:
            self.council.prepare_consultation_content(short_content)
        except SystemExit:
            raise AssertionError("Short content should not exceed token limit")


def run_tests():
    """Run all tests and report results."""
    test_instance = TestCouncilTiktoken()
    test_instance.setup_method()
    
    tests = [
        test_instance.test_tokenizer_initialization,
        test_instance.test_count_tokens_simple_text,
        test_instance.test_count_tokens_empty_text,
        test_instance.test_count_tokens_long_text,
        test_instance.test_num_tokens_from_messages_simple,
        test_instance.test_num_tokens_from_messages_with_name,
        test_instance.test_num_tokens_from_messages_multiple,
        test_instance.test_num_tokens_from_messages_content_array,
        test_instance.test_num_tokens_from_messages_different_models,
        test_instance.test_prepare_consultation_content_token_counting,
        test_instance.test_token_count_consistency,
        test_instance.test_token_limits,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"Running {test.__name__}...", end=" ")
            test()
            print("✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)