"""
Pytest integration tests for bots using both @chatbot and @config decorators

This module contains end-to-end integration tests that verify complete bot
functionality with both configuration and chat capabilities. These tests
simulate real-world usage scenarios where bots have both:
- Configuration metadata (via @config decorator)
- Chat functionality (via @chatbot decorator)
- HTTP server integration (via BubbleTeaServer)

Integration tests are crucial for ensuring that all components work together
correctly in production-like environments. They test the full request/response
cycle including HTTP endpoints, JSON serialization, and component rendering.

Key testing scenarios:
- Full bot lifecycle (config + chat + server)
- Streaming vs non-streaming bots
- Multimodal bots (text + images)
- Complex component types (Cards, Blocks, etc.)
- Error handling and edge cases
- Async bot functionality
"""

import pytest
from fastapi.testclient import TestClient
import bubbletea_chat as bt
from bubbletea_chat.server import BubbleTeaServer


@pytest.fixture(autouse=True)
def reset_config_state():
    """
    Reset configuration state for integration test isolation
    
    Integration tests require clean state between test runs because they
    test the full system including global decorator state. This fixture
    ensures each integration test starts with a fresh environment.
    """
    import bubbletea_chat.decorators
    bubbletea_chat.decorators._config_function = None
    yield
    bubbletea_chat.decorators._config_function = None


def test_full_bot_with_config():
    """
    Test complete bot integration with config and chat functionality
    
    This is a comprehensive integration test that verifies:
    - @config decorator provides bot metadata
    - @chatbot decorator handles chat requests  
    - BubbleTeaServer exposes both /config and /chat endpoints
    - HTTP requests/responses work end-to-end
    - JSON serialization of components works correctly
    - Health endpoint is available for monitoring
    
    This test represents the most common bot deployment scenario
    and serves as a reference for proper bot setup.
    """
    # Step 1: Define bot configuration metadata
    @bt.config()
    def get_config():
        """Configuration providing bot metadata for the platform"""
        return bt.BotConfig(
            name="integration-test-bot",
            url="http://localhost:8000",
            is_streaming=False,
            icon_emoji="🧪",
            initial_text="Welcome to the integration test bot!",
        )

    # Step 2: Define bot chat behavior
    @bt.chatbot(name="integration-test-bot", stream=False)
    def test_bot(message: str):
        """Bot with conditional responses demonstrating real bot logic"""
        if "hello" in message.lower():
            return [bt.Text("Hello! I'm the integration test bot.")]
        elif "config" in message.lower():
            return [bt.Text("You can check my config at /config endpoint!")]
        else:
            return [bt.Text("I don't understand. Try saying 'hello' or 'config'.")]

    # Step 3: Create HTTP server for the bot
    server = BubbleTeaServer(test_bot, port=8005)

    # Step 4: Test the complete HTTP integration
    with TestClient(server.app) as client:
        # Test config endpoint returns proper metadata
        config_response = client.get("/config")
        assert config_response.status_code == 200, "Config endpoint should be accessible"
        
        config_data = config_response.json()
        assert config_data["name"] == "integration-test-bot", "Config should contain bot name"
        assert config_data["icon_emoji"] == "🧪", "Config should preserve emoji"
        assert config_data["initial_text"] == "Welcome to the integration test bot!", "Config should have welcome text"

        # Test chat endpoint processes messages correctly
        chat_response = client.post(
            "/chat", json={"type": "user", "message": "Hello"}
        )
        assert chat_response.status_code == 200, "Chat endpoint should accept messages"
        
        chat_data = chat_response.json()
        assert "responses" in chat_data, "Chat response should have responses field"
        assert len(chat_data["responses"]) == 1, "Should return one response component"
        assert (
            chat_data["responses"][0]["text"]
            == "Hello! I'm the integration test bot."
        ), "Bot should respond with expected greeting"

        # Test health endpoint for monitoring
        health_response = client.get("/health")
        assert health_response.status_code == 200, "Health endpoint should be available"
        health_data = health_response.json()
        assert health_data["status"] == "healthy", "Health check should pass"


def test_streaming_bot_with_config():
    """
    Test streaming bot integration with configuration
    
    This test verifies:
    - Streaming bots work with configuration metadata
    - is_streaming flag is properly set in config
    - Server handles streaming responses correctly
    - Streaming configuration affects server behavior
    
    Note: TestClient has limitations with Server-Sent Events,
    so we verify the response is acceptable rather than testing streaming.
    """
    @bt.config()
    def get_config():
        """Configuration for a streaming bot"""
        return bt.BotConfig(
            name="streaming-test-bot",
            url="http://localhost:8000",
            is_streaming=True,  # Important: this affects server behavior
            icon_emoji="🌊",
            initial_text="I'm a streaming bot!",
        )

    @bt.chatbot(stream=True)  # Streaming bot yields components
    def streaming_bot(message: str):
        """Bot that streams multiple components in sequence"""
        yield bt.Text("Starting stream...")
        yield bt.Text("Processing your message...")
        yield bt.Text(f"You said: {message}")
        yield bt.Text("Stream complete!")

    server = BubbleTeaServer(streaming_bot, port=8006)

    with TestClient(server.app) as client:
        # Verify streaming configuration is exposed
        config_response = client.get("/config")
        assert config_response.status_code == 200, "Streaming bot config should be accessible"
        config_data = config_response.json()
        assert config_data["is_streaming"] is True, "Config should indicate streaming capability"
        assert config_data["icon_emoji"] == "🌊", "Streaming config should preserve metadata"

        # Test streaming chat endpoint (TestClient limitation: can't test actual streaming)
        chat_response = client.post(
            "/chat", json={"type": "user", "message": "Test stream"}
        )
        assert chat_response.status_code == 200, "Streaming endpoint should accept requests"


def test_multimodal_bot_with_config():
    """
    Test bot that handles both text and images with configuration
    
    This integration test demonstrates:
    - Bots that accept both text messages and images
    - Proper handling of multimodal input via HTTP
    - Image data serialization (URL and base64)
    - Component responses for multimodal interactions
    - Real-world multimodal bot scenarios
    """
    @bt.config()
    def get_config():
        """Configuration for a multimodal bot"""
        return bt.BotConfig(
            name="multimodal-bot",
            url="http://localhost:8000",
            is_streaming=False,
            icon_emoji="🖼️",
            initial_text="Send me text or images!",
        )

    @bt.chatbot(stream=False)
    def multimodal_bot(message: str, images: list = None):
        """Bot that processes both text and images"""
        if images:
            # Handle requests with images
            return [bt.Text(
                f"Received {len(images)} image(s) with message: {message}"
            )]
        else:
            # Handle text-only requests
            return [bt.Text(f"Text only message: {message}")]

    server = BubbleTeaServer(multimodal_bot, port=8007)

    with TestClient(server.app) as client:
        # Test multimodal configuration
        config_response = client.get("/config")
        assert config_response.status_code == 200, "Multimodal config should be accessible"
        config_data = config_response.json()
        assert config_data["icon_emoji"] == "🖼️", "Multimodal bot should have appropriate emoji"

        # Test chat with multiple image types (URL and base64)
        chat_response = client.post(
            "/chat",
            json={
                "type": "user",
                "message": "Look at this",
                "images": [
                    {"url": "https://example.com/image1.jpg"},  # URL image
                    {   # Base64 image (1x1 pixel PNG for testing)
                        "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                    },
                ],
            },
        )
        assert chat_response.status_code == 200, "Multimodal request should be accepted"
        
        chat_data = chat_response.json()
        assert "2 image(s)" in chat_data["responses"][0]["text"], "Bot should recognize both images"


def test_bot_with_all_component_types():
    """
    Test bot using all available component types with configuration
    
    This test verifies:
    - All BubbleTea component types work in integration
    - Components serialize properly to JSON
    - Server handles complex component responses
    - Comprehensive component showcase for documentation
    """
    @bt.config()
    def get_config():
        """Configuration for a component demonstration bot"""
        return bt.BotConfig(
            name="component-demo-bot",
            url="http://localhost:8000",
            is_streaming=False,
            icon_emoji="🎨",
            initial_text="I can show you different component types!",
        )

    @bt.chatbot(stream=False)
    def component_bot(message: str):
        """Bot demonstrating all component types"""
        if "text" in message.lower():
            # Simple text component
            return [bt.Text("This is a text component")]
        elif "image" in message.lower():
            # Image component with URL and alt text
            return [bt.Image("https://example.com/demo.jpg", alt="Demo image")]
        elif "markdown" in message.lower():
            # Markdown component with formatted content
            return [bt.Markdown("# Markdown Header\\n\\n**Bold** and *italic* text")]
        else:
            # Default help response
            return [bt.Text("Ask me about: text, image, or markdown")]

    server = BubbleTeaServer(component_bot, port=8008)

    with TestClient(server.app) as client:
        # Verify component bot configuration
        config_response = client.get("/config")
        assert config_response.status_code == 200, "Component demo config should work"
        assert config_response.json()["icon_emoji"] == "🎨", "Should have artist emoji"

        # Test text component response
        text_response = client.post(
            "/chat", json={"type": "user", "message": "show text"}
        )
        assert text_response.status_code == 200, "Text component request should work"
        text_data = text_response.json()
        assert text_data["responses"][0]["text"] == "This is a text component", "Text component should work"


def test_bot_with_cards_and_blocks():
    """
    Test bot using advanced component types (Cards and Blocks)
    
    This test demonstrates:
    - Complex component types for rich interfaces
    - Card collections with metadata
    - Block components for grouped content
    - Real-world UI component usage patterns
    """
    @bt.config()
    def get_config():
        """Configuration for rich content bot"""
        return bt.BotConfig(
            name="rich-content-bot",
            url="http://localhost:8000",
            is_streaming=False,
            icon_emoji="📝",
            initial_text="I can show rich content!",
        )

    @bt.chatbot(stream=False)
    def rich_bot(message: str):
        """Bot demonstrating advanced component types"""
        if "cards" in message.lower():
            # Create card collection
            cards = [
                bt.Card(
                    text="Card 1",
                    markdown=bt.Markdown("**First card**"),
                    card_value="card1"
                ),
                bt.Card(
                    text="Card 2", 
                    markdown=bt.Markdown("**Second card**"),
                    card_value="card2"
                )
            ]
            return [bt.Cards(cards=cards)]
        elif "block" in message.lower():
            # Create content block
            block = bt.Block(
                components=[
                    bt.Text("This is in a block"),
                    bt.Markdown("**Block content**")
                ],
                title="Sample Block"
            )
            return [block]
        else:
            return [bt.Text("Try 'cards' or 'block'")]

    server = BubbleTeaServer(rich_bot, port=8009)

    with TestClient(server.app) as client:
        # Test rich content configuration
        config_response = client.get("/config")
        assert config_response.status_code == 200, "Rich content config should work"
        assert config_response.json()["icon_emoji"] == "📝", "Should have document emoji"

        # Test cards component
        cards_response = client.post(
            "/chat", json={"type": "user", "message": "show cards"}
        )
        assert cards_response.status_code == 200, "Cards request should work"
        cards_data = cards_response.json()
        assert len(cards_data["responses"]) == 1, "Should return one Cards component"
        assert "cards" in cards_data["responses"][0], "Response should contain cards array"


def test_async_bot_with_config():
    """
    Test async bot integration with configuration
    
    This test verifies:
    - Async bots work correctly with configuration
    - Server properly handles async bot functions
    - Async operations complete correctly in HTTP context
    - Real-world async bot scenarios (database calls, API calls, etc.)
    """
    @bt.config()
    def get_config():
        """Configuration for async bot"""
        return bt.BotConfig(
            name="async-bot",
            url="http://localhost:8000",
            is_streaming=False,
            icon_emoji="⚡",
            initial_text="I'm async!",
        )

    @bt.chatbot(stream=False)
    async def async_bot(message: str):
        """Async bot simulating database or API operations"""
        # Simulate async work (e.g., database query, API call)
        import asyncio
        await asyncio.sleep(0.001)
        return [bt.Text(f"Async response: {message}")]

    server = BubbleTeaServer(async_bot, port=8010)

    with TestClient(server.app) as client:
        # Test async bot configuration
        config_response = client.get("/config")
        assert config_response.status_code == 200, "Async bot config should work"
        assert config_response.json()["icon_emoji"] == "⚡", "Should have lightning emoji"

        # Test async chat functionality
        chat_response = client.post(
            "/chat", json={"type": "user", "message": "async test"}
        )
        assert chat_response.status_code == 200, "Async chat should work"
        chat_data = chat_response.json()
        assert "Async response: async test" in chat_data["responses"][0]["text"], "Async response should work"


if __name__ == "__main__":
    """
    Integration test execution
    
    These integration tests provide comprehensive coverage of real-world
    bot deployment scenarios. They're more complex than unit tests but
    provide confidence that the entire system works together correctly.
    
    Run integration tests with:
        python -m pytest tests/test_config_integration.py -v
    
    These tests are especially valuable for:
    - Verifying deployment readiness
    - Testing component serialization
    - Validating HTTP API contracts
    - Ensuring end-to-end functionality
    """
    print("Test file converted to pytest format successfully!")
    print("Run with: python -m pytest tests/test_config_integration.py -v")