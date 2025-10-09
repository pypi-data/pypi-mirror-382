"""
Pytest test cases for the @config decorator functionality

This module tests the @config decorator which allows bots to provide
configuration metadata for the BubbleTea platform. The configuration
includes bot metadata, display settings, CORS options, and more.

Key areas tested:
- @config decorator syntax variations (with/without parentheses, custom paths)
- BotConfig object creation and validation
- Server integration of config endpoints
- All available configuration options
- Async configuration functions
- Error handling and validation

The @config decorator is essential for bot discovery, display in the
BubbleTea directory, and proper platform integration.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import bubbletea_chat as bt
from bubbletea_chat.decorators import _config_function
from bubbletea_chat.server import BubbleTeaServer


@pytest.fixture(autouse=True)
def reset_config_state():
    """
    Reset module-level config state before each test
    
    The @config decorator stores state globally, so we need to clear it
    between tests to ensure test isolation. This fixture automatically
    runs before each test to provide a clean state.
    
    Yields control to the test, then cleans up after the test completes.
    """
    # Store reference to the global config state
    global _config_function
    import bubbletea_chat.decorators
    
    # Clear any existing config registration
    bubbletea_chat.decorators._config_function = None
    
    # Yield control to the test
    yield
    
    # Clean up after test (ensures no state leaks between tests)
    bubbletea_chat.decorators._config_function = None


def test_config_decorator_with_parentheses():
    """
    Test @config() decorator with parentheses (recommended syntax)
    
    This test verifies:
    - The @config() syntax (with parentheses) works correctly
    - The decorator properly registers the config function
    - The default config endpoint path is set correctly
    - The registered function is the one we defined
    """
    @bt.config()  # Note: parentheses are present
    def get_config():
        """Configuration function using parentheses syntax"""
        return bt.BotConfig(
            name="test-bot", 
            url="http://localhost:8000", 
            is_streaming=True
        )

    # Verify the decorator registered our function
    assert _config_function is not None, "Config function should be registered"
    
    # Unpack the registered function and path
    func, path = _config_function
    assert func == get_config, "Registered function should match our definition"
    assert path == "/config", "Default config path should be '/config'"


def test_config_decorator_without_parentheses():
    """
    Test @config decorator without parentheses (alternative syntax)
    
    This test verifies:
    - The @config syntax (without parentheses) also works
    - Both syntax forms are equivalent in functionality
    - The registration works the same way
    """
    @bt.config  # Note: no parentheses
    def get_config():
        """Configuration function using no-parentheses syntax"""
        return bt.BotConfig(
            name="test-bot", 
            url="http://localhost:8000", 
            is_streaming=False
        )

    # Verify registration works identically
    assert _config_function is not None, "Config should be registered without parentheses"
    func, path = _config_function
    assert func == get_config, "Function should be registered correctly"
    assert path == "/config", "Default path should still be used"


def test_config_decorator_custom_path():
    """
    Test @config decorator with custom endpoint path
    
    This test demonstrates:
    - How to specify a custom config endpoint path
    - Useful for API versioning or custom routing schemes
    - Path parameter is properly stored and used
    """
    @bt.config("/bot/info")  # Custom path instead of default /config
    def get_config():
        """Configuration with custom endpoint path"""
        return bt.BotConfig(
            name="custom-path-bot", 
            url="http://localhost:8000", 
            is_streaming=True
        )

    # Verify custom path is registered
    assert _config_function is not None, "Custom path config should be registered"
    func, path = _config_function
    assert func == get_config, "Function should be registered"
    assert path == "/bot/info", "Custom path should be preserved"


def test_config_returns_dict():
    """
    Test config function returning dict instead of BotConfig object
    
    This test demonstrates:
    - Alternative way to define configuration using plain dictionaries
    - Server properly converts dict to JSON response
    - All config fields are accessible via HTTP endpoint
    - Useful for dynamic configuration or simpler syntax
    """
    @bt.config()
    def get_config():
        """Configuration function returning a dictionary"""
        return {
            "name": "dict-bot",
            "url": "http://localhost:8000",
            "is_streaming": True,
            "icon_emoji": "🤖",
            "initial_text": "Hello from dict!",
        }

    # Create a bot and server to test the config endpoint
    @bt.chatbot(stream=False)
    def test_bot(message: str):
        """Simple test bot for config endpoint testing"""
        return [bt.Text("Response")]

    # Create server instance
    server = BubbleTeaServer(test_bot, port=8001)

    # Test the HTTP config endpoint
    with TestClient(server.app) as client:
        response = client.get("/config")
        assert response.status_code == 200, "Config endpoint should be accessible"
        
        # Verify dictionary data is properly served
        data = response.json()
        assert data["name"] == "dict-bot", "Dict name should be preserved"
        assert data["icon_emoji"] == "🤖", "Dict emoji should be preserved"


def test_config_with_optional_fields():
    """
    Test config with optional fields using default values
    
    This test verifies:
    - BotConfig provides sensible defaults for optional fields
    - Only required fields (name, url, is_streaming) need to be specified
    - Default values are appropriate for basic bot functionality
    """
    @bt.config()
    def get_config():
        """Minimal configuration with defaults"""
        return bt.BotConfig(
            name="minimal-bot",
            url="http://localhost:8000",
            is_streaming=False,
            # Intentionally omitting optional fields to test defaults
        )

    # Test the config function directly
    config = get_config()
    
    # Verify default values are applied
    assert config.icon_emoji == "🤖", "Should use default emoji"
    assert config.initial_text == "Hi! How can I help you today?", "Should use default greeting"


@pytest.mark.asyncio
async def test_config_async_function():
    """
    Test config decorator with async configuration function
    
    This test demonstrates:
    - Config functions can be async (useful for database lookups, etc.)
    - Async config functions work correctly with the decorator
    - Proper async/await usage in configuration context
    """
    @bt.config()
    async def get_config():
        """Async configuration function"""
        # Simulate async operation (e.g., database lookup, API call)
        await asyncio.sleep(0.001)
        
        return bt.BotConfig(
            name="async-bot",
            url="http://localhost:8000",
            is_streaming=True,
            icon_emoji="⚡",
            initial_text="Async bot ready!",
        )

    # Test async config function
    config = await get_config()
    assert config.name == "async-bot", "Async config should work"
    assert config.icon_emoji == "⚡", "Async config should preserve data"


def test_server_with_config():
    """
    Test server creates config endpoint when @config decorator is used
    
    This test verifies:
    - Servers automatically expose config endpoints when @config is present
    - HTTP endpoint returns proper JSON configuration
    - All configuration fields are accessible via API
    - Config endpoint integrates properly with FastAPI server
    """
    @bt.config()
    def get_config():
        """Test configuration for server integration"""
        return bt.BotConfig(
            name="endpoint-test-bot",
            url="http://localhost:8000",
            is_streaming=True,
            icon_emoji="🧪",
            initial_text="Testing endpoint",
        )

    @bt.chatbot(stream=False)
    def test_bot(message: str):
        """Simple test bot"""
        return [bt.Text("Test response")]

    # Create server with config
    server = BubbleTeaServer(test_bot, port=8002)

    with TestClient(server.app) as client:
        # Test config endpoint exists and returns correct data
        response = client.get("/config")
        assert response.status_code == 200, "Config endpoint should exist"

        # Verify all config data is properly serialized
        data = response.json()
        assert data["name"] == "endpoint-test-bot", "Config name should be correct"
        assert data["url"] == "http://localhost:8000", "Config URL should be preserved"
        assert data["is_streaming"] is True, "Streaming flag should be preserved"
        assert data["icon_emoji"] == "🧪", "Icon emoji should be included"
        assert data["initial_text"] == "Testing endpoint", "Initial text should be included"


def test_server_without_config():
    """
    Test server works correctly without @config decorator
    
    This test ensures:
    - Bots can function without configuration metadata
    - Config endpoint returns 404 when no @config decorator is present
    - Chat functionality still works normally
    - Graceful handling of missing configuration
    """
    @bt.chatbot(stream=False)
    def test_bot(message: str):
        """Bot without any configuration"""
        return [bt.Text("No config bot")]

    # Create server without config decorator
    server = BubbleTeaServer(test_bot, port=8003)

    with TestClient(server.app) as client:
        # Config endpoint should not exist
        response = client.get("/config")
        assert response.status_code == 404, "Config endpoint should not exist without @config"

        # But chat endpoint should still work normally
        response = client.post("/chat", json={"type": "user", "message": "Hello"})
        assert response.status_code == 200, "Chat should work without config"


def test_custom_config_path():
    """
    Test server respects custom config endpoint paths
    
    This test verifies:
    - Custom config paths are properly registered
    - Default config path is not accessible when custom path is used
    - Custom path serves the configuration correctly
    - Useful for API versioning and custom routing
    """
    @bt.config("/api/bot-info")  # Custom config path
    def get_config():
        """Configuration with custom endpoint"""
        return bt.BotConfig(
            name="custom-path-bot", 
            url="http://localhost:8000", 
            is_streaming=False
        )

    @bt.chatbot(stream=False)
    def test_bot(message: str):
        """Test bot for custom path testing"""
        return [bt.Text("Custom path response")]

    server = BubbleTeaServer(test_bot, port=8004)

    with TestClient(server.app) as client:
        # Default config path should not exist
        response = client.get("/config")
        assert response.status_code == 404, "Default path should not work with custom path"

        # Custom path should work correctly
        response = client.get("/api/bot-info")
        assert response.status_code == 200, "Custom path should be accessible"
        
        data = response.json()
        assert data["name"] == "custom-path-bot", "Custom path should serve correct config"


def test_comprehensive_config():
    """
    Test configuration with all available options
    
    This test demonstrates:
    - Complete BotConfig with all possible fields
    - App Store-like metadata for bot discovery
    - Advanced configuration options (CORS, pricing, etc.)
    - Comprehensive example for documentation purposes
    """
    @bt.config()
    def get_comprehensive_config():
        """Comprehensive configuration demonstrating all available options"""
        return bt.BotConfig(
            # Required fields - must be provided
            name="comprehensive-bot",
            url="http://localhost:8000",
            is_streaming=False,
            
            # App Store-like metadata for bot discovery
            display_name="Comprehensive Bot",          # Display name in UI
            subtitle="Testing all options",           # Short description
            icon_url="https://picsum.photos/1024/1024", # Bot icon (1024x1024 PNG)
            icon_emoji="🔧",                          # Emoji alternative to icon
            preview_video_url="https://example.com/preview.mp4", # Demo video
            description="**Testing bot** with all configuration options", # Markdown description
            visibility="public",                       # "public" or "private"
            discoverable=True,                        # Show in bot directory
            entrypoint="start",                       # Initial action/page
            
            # Legacy fields (for backward compatibility)
            initial_text="Welcome to comprehensive bot!",
            authorized_emails=["test@example.com"],   # Email whitelist for private bots
            subscription_monthly_price=500,           # Monthly price in cents ($5.00)
            
            # Advanced configuration
            cors_config={
                "allow_origins": ["https://example.com"],
                "allow_credentials": True
            },
            
            # Example chats for user guidance
            example_chats=["Hello", "Help me", "Show features"]
        )

    @bt.chatbot(stream=False)
    def comprehensive_bot(message: str):
        """Bot with comprehensive configuration"""
        return [bt.Text(f"Comprehensive response: {message}")]

    # Test server with comprehensive config
    server = BubbleTeaServer(comprehensive_bot, port=8005)

    with TestClient(server.app) as client:
        response = client.get("/config")
        assert response.status_code == 200, "Comprehensive config should be accessible"
        
        # Verify all configuration fields are present
        data = response.json()
        assert data["name"] == "comprehensive-bot"
        assert data["display_name"] == "Comprehensive Bot"
        assert data["subtitle"] == "Testing all options"
        assert data["icon_emoji"] == "🔧"
        assert data["visibility"] == "public"
        assert data["discoverable"] is True
        assert data["subscription_monthly_price"] == 500
        assert len(data["example_chats"]) == 3, "Should have example chats"


if __name__ == "__main__":
    """
    Direct execution for development and debugging
    
    This allows developers to run individual test files during development:
        python tests/test_config_decorator.py
    
    For full pytest integration with better output and features:
        python -m pytest tests/test_config_decorator.py -v
    """
    print("Test file converted to pytest format successfully!")
    print("Run with: python -m pytest tests/test_config_decorator.py -v")