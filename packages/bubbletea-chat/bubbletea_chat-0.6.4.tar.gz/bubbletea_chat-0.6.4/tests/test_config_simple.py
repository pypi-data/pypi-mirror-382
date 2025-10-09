#!/usr/bin/env python
"""
Pytest tests for simple config decorator verification

This module provides basic, easy-to-understand tests for the @config
decorator functionality. These tests are designed to be:
- Simple and readable for new contributors
- Quick to run (minimal setup/teardown)
- Focused on core configuration functionality
- Good examples for documentation

These tests complement the more comprehensive config decorator tests
by providing straightforward examples of basic usage patterns.
"""

import pytest
import bubbletea_chat as bt
from bubbletea_chat.decorators import _config_function


@pytest.fixture(autouse=True)
def reset_config_state():
    """
    Clean slate for each test
    
    This fixture ensures each test starts with a clean configuration state.
    Since the @config decorator uses global state, we need to reset it
    between tests to prevent interference.
    
    This is a simplified version of the fixture used in other config tests,
    focused on clarity and ease of understanding.
    """
    import bubbletea_chat.decorators
    
    # Clear any previous config registration
    bubbletea_chat.decorators._config_function = None
    
    # Let the test run
    yield
    
    # Clean up after test
    bubbletea_chat.decorators._config_function = None


def test_basic_config_decorator():
    """
    Test the most basic @config decorator usage
    
    This is the simplest possible test for the @config decorator.
    It demonstrates:
    - How to create a basic configuration function
    - Required configuration fields
    - How to test configuration creation
    - Basic assertion patterns
    
    Perfect for newcomers to understand the config system.
    """
    @bt.config()
    def get_config():
        """Simple configuration function"""
        return bt.BotConfig(
            name="test-bot",                    # Bot identifier (required)
            url="http://localhost:8000",        # Bot endpoint URL (required)
            is_streaming=True,                  # Streaming capability (required)
            icon_emoji="🧪",                   # Bot emoji icon
            initial_text="Test bot ready!",    # Welcome message
        )

    # Test that config creation works
    config = get_config()
    
    # Verify basic properties are set correctly
    assert config.name == "test-bot", "Bot name should be set"
    assert config.icon_emoji == "🧪", "Emoji should be preserved"
    assert config.initial_text == "Test bot ready!", "Initial text should be set"
    assert config.is_streaming is True, "Streaming flag should be preserved"


def test_decorator_registration():
    """
    Test that the @config decorator properly registers functions
    
    This test verifies the internal mechanics of the @config decorator:
    - Function registration in global state
    - Default endpoint path assignment
    - Proper function reference storage
    
    Understanding this test helps developers debug configuration issues
    and understand how the decorator system works internally.
    """
    @bt.config()
    def get_config():
        """Configuration for registration testing"""
        return bt.BotConfig(
            name="registration-test",
            url="http://localhost:8000",
            is_streaming=False
        )

    # Check that the decorator registered our function
    assert _config_function is not None, "Decorator should register the function"
    
    # Verify the registration details
    func, path = _config_function
    assert func == get_config, "Registered function should match our definition"
    assert path == "/config", "Default config path should be used"


def test_bot_with_config():
    """
    Test creating a complete bot with configuration
    
    This test demonstrates a complete, working bot setup:
    - Configuration definition with @config
    - Bot implementation with @chatbot  
    - Testing both components work together
    - Practical example of a full bot setup
    
    This is a great reference for developers building their first bot.
    """
    # Step 1: Define bot configuration
    @bt.config()
    def get_config():
        """Configuration for our test bot"""
        return bt.BotConfig(
            name="config-test-bot",
            url="http://localhost:8000", 
            is_streaming=False,
            icon_emoji="⚙️",
            initial_text="Bot with config!"
        )

    # Step 2: Define bot behavior
    @bt.chatbot(stream=False)
    def test_bot(message: str):
        """Simple echo bot for testing"""
        return [bt.Text(f"Echo: {message}")]

    # Step 3: Test that bot functionality works
    response = test_bot("test message")
    assert len(response) == 1, "Bot should return one component"
    assert isinstance(response[0], bt.Text), "Response should be Text component"
    assert response[0].text == "Echo: test message", "Should echo the input message"

    # Step 4: Test that configuration is accessible
    config = get_config()
    assert config.name == "config-test-bot", "Config should be accessible"
    assert config.icon_emoji == "⚙️", "Config properties should be preserved"


def test_config_with_all_defaults():
    """
    Test configuration using default values for optional fields
    
    This test shows:
    - Minimal required configuration (only name, url, is_streaming)
    - How BotConfig provides sensible defaults
    - What the default values actually are
    - How to create the simplest possible bot configuration
    
    Useful for understanding the minimal requirements for bot configuration.
    """
    @bt.config()
    def minimal_config():
        """Minimal configuration using defaults"""
        return bt.BotConfig(
            # Only specify required fields
            name="minimal-test",
            url="http://localhost:8000",
            is_streaming=False
            # All other fields will use their default values
        )
    
    # Test the config
    config = minimal_config()
    
    # Verify required fields are set
    assert config.name == "minimal-test", "Required name field should be set"
    assert config.is_streaming is False, "Required streaming field should be set"
    
    # Verify default values are applied correctly
    assert config.icon_emoji == "🤖", "Should use default robot emoji"
    assert config.initial_text == "Hi! How can I help you today?", "Should use default greeting"


def test_config_validation():
    """
    Test that configuration validation works correctly
    
    This test demonstrates:
    - BotConfig validation rules (e.g., no spaces in bot names)
    - How to test for validation errors
    - Using pytest.raises for exception testing
    - Understanding configuration constraints
    
    Important for developers to understand the limitations and rules
    for bot configuration to avoid runtime errors.
    """
    # Test that invalid configuration raises an error
    with pytest.raises(ValueError, match="Bot handle cannot contain spaces"):
        @bt.config()
        def invalid_config():
            """Configuration with invalid bot name (contains spaces)"""
            return bt.BotConfig(
                name="Invalid Bot Name",  # This should fail - spaces not allowed
                url="http://localhost:8000",
                is_streaming=False
            )
        
        # Attempting to create this config should raise a validation error
        invalid_config()


if __name__ == "__main__":
    """
    Run this test file directly for quick testing
    
    During development, you can run this file directly to quickly test
    the basic configuration functionality:
        python tests/test_config_simple.py
    
    For full pytest features (better output, fixtures, etc.), use:
        python -m pytest tests/test_config_simple.py -v
    
    These simple tests are perfect for:
    - Quick smoke testing during development
    - Understanding basic configuration concepts
    - Debugging configuration issues
    - Learning how BubbleTea configuration works
    """
    print("Test file converted to pytest format successfully!")
    print("Run with: python -m pytest tests/test_config_simple.py -v")