"""
Request and response schemas for BubbleTea
"""

from typing import List, Literal, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, validator
from .components import Component, BaseComponent


class ImageInput(BaseModel):
    """Image input that can be either a URL or base64 encoded data"""

    text: Optional[str] = Field(None, description="Text description of the image")
    url: Optional[str] = Field(
        None, description="URL of the image"
    )  # Can be https:// or data:image/...
    base64: Optional[str] = Field(
        None, description="Base64 encoded image data"
    )  # Raw base64 string
    mime_type: Optional[str] = Field(
        None, description="MIME type of the image (e.g., image/jpeg, image/png)"
    )


class ComponentChatRequest(BaseModel):
    """Incoming chat request from BubbleTea"""

    type: Literal["user"]  # Always "user" for user messages
    message: str  # The user's message text
    images: Optional[List[ImageInput]] = Field(
        None, description="Optional images to include with the message"
    )
    user_uuid: Optional[str] = Field(
        None, description="UUID of the user making the request"
    )  # Unique user identifier
    conversation_uuid: Optional[str] = Field(
        None, description="UUID of the conversation"
    )  # Conversation tracking
    user_email: Optional[str] = Field(
        None, description="Email of the user making the request"
    )  # If authenticated
    chat_history: Optional[Union[List[Dict[str, Any]], str]] = Field(
        None,
        description="Detailed message history with metadata (list) or context string",
    )
    thread_id: Optional[str] = Field(
        None, description="Thread ID of user conversation"
    )  # For threaded conversations


class ComponentChatResponse(BaseModel):
    """Non-streaming response containing list of components"""

    responses: List[Union[Component, BaseComponent]]  # List of UI components to display


class BotConfig(BaseModel):
    """Configuration for a BubbleTea bot"""

    # Required fields - These must be provided
    name: str = Field(
        ...,
        description="Handle - unique identifier used in URLs (no spaces)",
        pattern=r"^[a-zA-Z0-9_-]+$",
    )  # e.g., "weather-bot"
    url: str = Field(
        ..., description="URL where the bot is hosted"
    )  # Your bot's endpoint URL
    is_streaming: bool = Field(
        ..., description="Whether the bot supports streaming responses"
    )  # True if using yield

    # App Store-like metadata - For bot discovery and display
    display_name: Optional[str] = Field(
        None, max_length=20, description="Display name (max 20 chars)"
    )  # Shown in UI
    subtitle: Optional[str] = Field(
        None, max_length=30, description="Subtitle (max 30 chars)"
    )  # Short tagline
    icon_url: Optional[str] = Field(
        None, description="1024x1024 PNG icon URL"
    )  # Bot icon image
    icon_emoji: Optional[str] = Field(
        None, max_length=10, description="Emoji icon alternative"
    )  # If no icon_url
    preview_video_url: Optional[str] = Field(
        None, description="Preview video URL"
    )  # Demo video
    description: Optional[str] = Field(
        None, description="Markdown description"
    )  # Full description
    visibility: Optional[Literal["public", "private"]] = Field(
        "public", description="Bot visibility"
    )  # Who can see the bot
    discoverable: Optional[bool] = Field(
        True, description="Whether the bot is discoverable"
    )  # Show in bot directory
    entrypoint: Optional[str] = Field(
        None, description="Launch context page/action"
    )  # Initial action/page

    # Legacy fields (kept for backward compatibility)
    emoji: Optional[str] = Field(
        "🤖", description="Emoji to represent the bot (deprecated, use icon_emoji)"
    )  # Use icon_emoji instead
    initial_text: Optional[str] = Field(
        "Hi! How can I help you today?", description="Initial greeting message"
    )  # First message shown
    authorization: Optional[Literal["public", "private"]] = Field(
        "public", description="Authorization type (deprecated, use visibility)"
    )  # Use visibility instead
    authorized_emails: Optional[List[str]] = Field(
        None, description="List of authorized emails for private bots"
    )  # Whitelist for private bots
    subscription_monthly_price: Optional[int] = Field(
        0, description="Monthly subscription price in cents"
    )  # 0 = free, 500 = $5.00

    # Advanced configuration
    cors_config: Optional[Dict[str, Any]] = Field(
        None, description="Custom CORS configuration"
    )  # Override default CORS settings

    # Bot examples
    example_chats: Optional[List[str]] = Field(
        None, description="List of example chat messages for the bot"
    )  # Sample prompts users can try

    @validator("name")
    def validate_handle(cls, v):
        """Ensure bot handle is URL-safe"""
        if " " in v:
            raise ValueError("Bot handle cannot contain spaces")
        return v.lower()  # Convert to lowercase for consistency

    @validator("icon_url", "preview_video_url")
    def validate_media_urls(cls, v):
        """Validate that media URLs use HTTPS"""
        if v and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Media URLs must start with http:// or https://")
        return v
