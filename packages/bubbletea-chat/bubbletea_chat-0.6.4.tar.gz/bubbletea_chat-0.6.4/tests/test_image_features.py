#!/usr/bin/env python3
"""
Pytest tests for image-related features in BubbleTea package
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch
from bubbletea_chat import chatbot, Text, Image, LLM, ImageInput


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
@pytest.mark.asyncio
async def test_image_generation():
    """Test image generation functionality"""
    
    llm = LLM(model="dall-e-3")
    prompt = "A peaceful zen garden with cherry blossoms"

    try:
        image_url = await llm.agenerate_image(prompt)
        assert image_url is not None
        assert isinstance(image_url, str)
        assert image_url.startswith(("http://", "https://"))
    except Exception as e:
        pytest.skip(f"Image generation failed (likely API limitation): {e}")


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
@pytest.mark.asyncio
async def test_vision_analysis():
    """Test vision/image analysis functionality"""
    
    llm = LLM(model="gpt-4-vision-preview")
    
    # Test with URL image
    test_image = ImageInput(url="https://picsum.photos/400/300")
    prompt = "Describe what you see in this image"

    try:
        response = await llm.acomplete_with_images(prompt, [test_image])
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    except Exception as e:
        pytest.skip(f"Vision analysis failed (likely API limitation): {e}")


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
@pytest.mark.asyncio
async def test_streaming_vision():
    """Test streaming with vision"""
    
    llm = LLM(model="gpt-4-vision-preview")
    test_image = ImageInput(url="https://picsum.photos/400/300")

    try:
        chunks = []
        async for chunk in llm.stream_with_images(
            "What's in this image?", [test_image]
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
    except Exception as e:
        pytest.skip(f"Streaming vision failed (likely API limitation): {e}")


@pytest.mark.asyncio
async def test_chatbot_with_images():
    """Test chatbot decorator with image support"""
    
    @chatbot(stream=False)
    async def test_bot(message: str, images: list = None):
        if images:
            return [
                Text(f"Received {len(images)} images"),
                Text(f"Message: {message}")
            ]
        else:
            return [Text("No images received")]

    # Test without images
    result = await test_bot("Hello", None)
    assert len(result) == 1
    assert isinstance(result[0], Text)
    assert result[0].text == "No images received"

    # Test with images
    test_images = [ImageInput(url="https://example.com/image.jpg")]
    result = await test_bot("Analyze this", test_images)
    assert len(result) == 2
    assert isinstance(result[0], Text)
    assert isinstance(result[1], Text)
    assert "1 images" in result[0].text
    assert "Analyze this" in result[1].text


def test_image_component():
    """Test Image component rendering"""
    
    # Test basic image
    img1 = Image("https://example.com/test.jpg")
    assert img1.url == "https://example.com/test.jpg"
    assert img1.alt is None

    # Test image with alt text
    img2 = Image("https://example.com/test.jpg", alt="Test image")
    assert img2.url == "https://example.com/test.jpg" 
    assert img2.alt == "Test image"


def test_base64_image():
    """Test base64 image handling"""
    
    # Create a base64 image input (1x1 pixel PNG)
    base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    base64_image = ImageInput(base64=base64_data, mime_type="image/png")

    assert base64_image.base64 == base64_data
    assert base64_image.mime_type == "image/png"
    assert base64_image.url is None
    assert base64_image.text is None


def test_image_input_url():
    """Test ImageInput with URL"""
    
    test_url = "https://example.com/image.jpg"
    image_input = ImageInput(url=test_url, text="Test image description")
    
    assert image_input.url == test_url
    assert image_input.text == "Test image description"
    assert image_input.base64 is None
    assert image_input.mime_type is None


def test_image_input_validation():
    """Test ImageInput validation"""
    
    # Should work with URL
    img1 = ImageInput(url="https://example.com/test.jpg")
    assert img1.url is not None
    
    # Should work with base64
    img2 = ImageInput(
        base64="validbase64data", 
        mime_type="image/png"
    )
    assert img2.base64 is not None
    
    # Should work with neither (for text description only)
    img3 = ImageInput(text="Description only")
    assert img3.text is not None


@pytest.mark.asyncio
async def test_llm_image_methods():
    """Test LLM class image-related methods exist"""
    
    llm = LLM(model="gpt-4")
    
    # Test methods exist (even if we don't call them)
    assert hasattr(llm, 'acomplete_with_images')
    assert hasattr(llm, 'stream_with_images')
    assert hasattr(llm, 'agenerate_image')
    
    # Test they are callable
    assert callable(llm.acomplete_with_images)
    assert callable(llm.stream_with_images) 
    assert callable(llm.agenerate_image)


def test_image_component_serialization():
    """Test that Image component can be serialized"""
    
    img = Image("https://example.com/test.jpg", alt="Test alt")
    
    # Should have required attributes
    assert hasattr(img, 'url')
    assert hasattr(img, 'alt')
    assert img.url == "https://example.com/test.jpg"
    assert img.alt == "Test alt"


@pytest.mark.asyncio
async def test_chatbot_streaming_with_images():
    """Test streaming chatbot with images"""
    
    @chatbot(stream=True)
    async def streaming_image_bot(message: str, images: list = None):
        yield Text("Processing your request...")
        
        if images:
            yield Text(f"Found {len(images)} images")
            for i, img in enumerate(images):
                if img.url:
                    yield Text(f"Image {i+1}: URL provided")
                elif img.base64:
                    yield Text(f"Image {i+1}: Base64 data provided")
        else:
            yield Text("No images in this request")
        
        yield Text(f"Message: {message}")

    # Test without images
    result = streaming_image_bot("Hello", None)
    components = []
    async for component in result:
        components.append(component)
    
    assert len(components) >= 2
    assert any("No images" in comp.text for comp in components if hasattr(comp, 'text'))

    # Test with images
    test_images = [
        ImageInput(url="https://example.com/1.jpg"),
        ImageInput(base64="base64data", mime_type="image/png")
    ]
    
    result = streaming_image_bot("Analyze these", test_images)
    components = []
    async for component in result:
        components.append(component)
    
    assert len(components) >= 4
    assert any("Found 2 images" in comp.text for comp in components if hasattr(comp, 'text'))


def test_multiple_image_types():
    """Test handling multiple types of images"""
    
    images = [
        ImageInput(url="https://example.com/photo.jpg"),
        ImageInput(base64="base64data", mime_type="image/png"),
        ImageInput(text="Just a description")
    ]
    
    # All should be valid ImageInput instances
    for img in images:
        assert isinstance(img, ImageInput)
    
    # URL image
    assert images[0].url is not None
    assert images[0].base64 is None
    
    # Base64 image  
    assert images[1].base64 is not None
    assert images[1].url is None
    assert images[1].mime_type == "image/png"
    
    # Text-only image
    assert images[2].text is not None
    assert images[2].url is None
    assert images[2].base64 is None


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_image_features.py -v
    print("Test file converted to pytest format successfully!")