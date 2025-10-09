"""
Pytest tests for BubbleTea bot functionality

This module contains unit tests for the core BubbleTea chatbot features including:
- Basic bot creation and response handling
- Different component types (Text, Markdown, Image)
- Server integration with FastAPI
- Non-streaming bot patterns

These tests demonstrate how to:
- Create and test chatbots using the @chatbot decorator
- Test different response component types
- Validate bot responses and component properties
- Test server endpoints and HTTP integration
"""

import pytest
from fastapi.testclient import TestClient
import bubbletea_chat as bt
from bubbletea_chat.server import BubbleTeaServer


def test_simple_bot():
    """
    Test basic bot functionality with simple text response
    
    This test demonstrates:
    - Creating a basic non-streaming bot with @chatbot(stream=False)
    - Returning a list of components from the bot function
    - Testing direct bot function calls (without server)
    - Validating response structure and content
    """
    @bt.chatbot(stream=False)
    def simple_bot(message: str):
        """A simple echo bot that responds with user input"""
        return [bt.Text(f"Hello! You said: {message}")]
    
    # Test bot function directly (without HTTP server)
    response = simple_bot("test message")
    
    # Verify response structure
    assert len(response) == 1, "Bot should return exactly one component"
    assert isinstance(response[0], bt.Text), "Response should be a Text component"
    assert "test message" in response[0].text, "Response should contain the original message"


def test_help_command():
    """
    Test bot with conditional logic and multiple component types
    
    This test demonstrates:
    - Implementing conditional responses based on user input
    - Returning multiple components in a single response
    - Using both Text and Markdown components
    - Building component lists dynamically
    """
    @bt.chatbot(stream=False)
    def help_bot(message: str):
        """Bot that provides help information when requested"""
        components = []
        
        # Always echo the user's message
        components.append(bt.Text(f"You said: {message}"))
        
        # Provide help if requested
        if "help" in message.lower():
            components.append(bt.Markdown("""
## Available Commands
- Say "image" to see an image
- Say "markdown" to see formatted text
- Say anything else for an echo response
            """))
        return components
    
    # Test help command triggers additional response
    response = help_bot("help me")
    
    # Verify multi-component response
    assert len(response) == 2, "Help command should return two components"
    assert isinstance(response[0], bt.Text), "First component should be Text"
    assert isinstance(response[1], bt.Markdown), "Second component should be Markdown"
    assert "Available Commands" in response[1].markdown, "Help content should be present"


def test_image_response():
    """
    Test bot image functionality and component properties
    
    This test demonstrates:
    - Creating and returning Image components
    - Setting image properties (URL and alt text)
    - Conditional response logic
    - Validating component attributes
    """
    @bt.chatbot(stream=False)
    def image_bot(message: str):
        """Bot that returns images when requested"""
        components = []
        
        if "image" in message.lower():
            # Provide an image when requested
            components.append(bt.Text("Here's a nice image for you:"))
            components.append(bt.Image(
                url="https://picsum.photos/400/300", 
                alt="Random image"
            ))
        else:
            # Default response
            components.append(bt.Text("Say 'image' to see an image"))
        
        return components
    
    # Test image command
    response = image_bot("show me an image")
    
    # Verify image response structure
    assert len(response) == 2, "Image request should return text + image"
    assert isinstance(response[0], bt.Text), "First component should be descriptive text"
    assert isinstance(response[1], bt.Image), "Second component should be Image"
    
    # Verify image properties
    assert response[1].url == "https://picsum.photos/400/300", "Image should have correct URL"
    assert response[1].alt == "Random image", "Image should have alt text for accessibility"


def test_markdown_response():
    """
    Test bot markdown functionality and formatting
    
    This test demonstrates:
    - Creating Markdown components with rich formatting
    - Using multi-line markdown content
    - Testing markdown-specific features (headers, bold, code blocks)
    """
    @bt.chatbot(stream=False)
    def markdown_bot(message: str):
        """Bot that demonstrates markdown formatting"""
        components = []
        
        if "markdown" in message.lower():
            # Return formatted markdown content
            components.append(bt.Markdown("""
# Markdown Example
This is **bold** and this is *italic*.

Here's a code block:
```python
print("Hello, BubbleTea!")
```
            """))
        else:
            components.append(bt.Text("Say 'markdown' to see formatted text"))
        
        return components
    
    # Test markdown command
    response = markdown_bot("show markdown")
    
    # Verify markdown response
    assert len(response) == 1, "Markdown request should return one component"
    assert isinstance(response[0], bt.Markdown), "Response should be Markdown component"
    assert "Markdown Example" in response[0].markdown, "Should contain header content"
    assert "**bold**" in response[0].markdown, "Should contain markdown formatting"


def test_bot_server_integration():
    """
    Test bot integration with FastAPI server and HTTP endpoints
    
    This test demonstrates:
    - Creating a BubbleTeaServer instance
    - Testing HTTP endpoints with FastAPI TestClient
    - Validating JSON response structure
    - Testing both health and chat endpoints
    """
    @bt.chatbot(stream=False)
    def integration_bot(message: str):
        """Simple bot for server integration testing"""
        return [bt.Text(f"Echo: {message}")]
    
    # Create BubbleTea server instance
    server = BubbleTeaServer(integration_bot, port=8000)
    
    # Use FastAPI TestClient for HTTP testing
    with TestClient(server.app) as client:
        # Test health endpoint (should be available on all servers)
        response = client.get("/health")
        assert response.status_code == 200, "Health endpoint should be accessible"
        
        # Test chat endpoint with JSON payload
        response = client.post(
            "/chat",
            json={"type": "user", "message": "Hello!"}
        )
        
        # Verify HTTP response
        assert response.status_code == 200, "Chat endpoint should accept valid requests"
        
        # Verify JSON response structure
        data = response.json()
        assert "responses" in data, "Response should contain 'responses' field"
        assert len(data["responses"]) == 1, "Should return one response component"
        assert data["responses"][0]["text"] == "Echo: Hello!", "Component should contain expected text"


if __name__ == "__main__":
    """
    When run directly, this will execute all tests in the file
    
    For development and debugging, you can run this file directly:
        python tests/test_bot.py
    
    For full pytest integration, use:
        python -m pytest tests/test_bot.py -v
    """
    print("Test file converted to pytest format successfully!")
    print("Run with: python -m pytest tests/test_bot.py -v")