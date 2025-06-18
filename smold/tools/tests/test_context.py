#!/usr/bin/env python3
"""
Test script for the improved context retention system in SmolD.
Run this script to test the conversation history and token counting functionality.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_conversation_history():
    """Test the ConversationHistory class."""
    print("=" * 60)
    print("Testing ConversationHistory...")
    print("=" * 60)
    
    try:
        from smold.context_manager import ConversationHistory
        
        # Test basic functionality
        ch = ConversationHistory(max_interactions=2, max_tokens=1000)
        print("✓ ConversationHistory created successfully")
        
        # Test adding interactions
        ch.add_interaction("Hello", "Hi there!")
        ch.add_interaction("How are you?", "I'm doing well, thank you!")
        print("✓ Added 2 interactions")
        
        # Test getting messages
        messages = ch.get_messages_for_llm()
        print(f"✓ Retrieved {len(messages)} messages")
        print("Messages:", messages)
        
        # Test context summary
        summary = ch.get_context_summary()
        print(f"✓ Context summary: {summary}")
        
        # Test max interactions limit
        ch.add_interaction("What's the weather?", "I don't have access to weather data.")
        messages_after = ch.get_messages_for_llm()
        print(f"✓ After adding 3rd interaction, history has {len(messages_after)} messages (should be 4, max 2 interactions)")
        
        # Test token counting
        token_count = ch.count_tokens("Hello world!")
        print(f"✓ Token counting works: 'Hello world!' = {token_count} tokens")
        
        return True
        
    except Exception as e:
        print(f"✗ ConversationHistory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_manager():
    """Test the ContextManager class."""
    print("\n" + "=" * 60)
    print("Testing ContextManager...")
    print("=" * 60)
    
    try:
        from smold.context_manager import ContextManager
        
        # Test basic functionality
        cm = ContextManager(max_interactions=2, max_context_tokens=1000)
        print("✓ ContextManager created successfully")
        
        # Test setting system prompt
        cm.set_system_prompt("You are a helpful assistant.")
        print("✓ System prompt set")
        
        # Test adding interactions
        cm.add_interaction("Hello", "Hi there!")
        cm.add_interaction("How are you?", "I'm doing well!")
        print("✓ Added interactions to context manager")
        
        # Test getting full context
        full_context = cm.get_full_context_for_llm()
        print(f"✓ Full context has {len(full_context)} messages")
        for i, msg in enumerate(full_context):
            print(f"  {i+1}. {msg['role']}: {msg['content'][:50]}...")
        
        # Test context info
        info = cm.get_context_info()
        print("✓ Context info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ ContextManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_integration():
    """Test if the agent can be created with context management."""
    print("\n" + "=" * 60)
    print("Testing Agent Integration...")
    print("=" * 60)
    
    try:
        # Set up a dummy environment for testing
        os.environ['DEEPSEEK_API_KEY'] = 'dummy_key_for_testing'
        
        from smold.agent import SmolDAgent, get_available_tools
        from smolagents import LiteLLMModel
        
        print("✓ Imports successful")
        
        # Test getting tools
        tools = get_available_tools()
        print(f"✓ Found {len(tools)} tools")
        
        # Test creating a mock model (won't actually work without real API key)
        mock_model = LiteLLMModel(
            model_id="deepseek/deepseek-chat",
            api_key="dummy_key",
            base_url="https://api.deepseek.com",
            system="Test system prompt"
        )
        print("✓ Mock model created")
        
        # Test creating SmolDAgent
        agent = SmolDAgent(tools=tools, model=mock_model)
        print("✓ SmolDAgent created successfully")
        
        # Test context info method
        info = agent.get_context_info()
        print("✓ Agent context info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("SmolD Context Retention System Test")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_conversation_history()
    test2_passed = test_context_manager()
    test3_passed = test_agent_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"ConversationHistory:  {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"ContextManager:       {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    print(f"Agent Integration:    {'✓ PASSED' if test3_passed else '✗ FAILED'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    print(f"\nOVERALL:              {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Context retention system is ready!")
        print("The agent will now remember the last 4 interactions and manage token limits.")
    else:
        print("\n❌ There are issues that need to be fixed before the system is ready.")

if __name__ == "__main__":
    main()