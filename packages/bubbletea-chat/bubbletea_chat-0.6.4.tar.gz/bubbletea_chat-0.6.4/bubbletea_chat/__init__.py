"""
BubbleTea Chat SDK
==================

A professional Python SDK for building AI-powered chatbots with rich UI components.
Seamlessly integrate with 100+ LLMs through LiteLLM support.

Quick Start:
    >>> import bubbletea_chat as bt
    >>>
    >>> @bt.chatbot
    >>> def my_bot(message: str):
    ...     return bt.Text(f"Echo: {message}")
    >>>
    >>> bt.run_server(my_bot)

Features:
    - Rich UI components (Text, Images, Cards, Videos, etc.)
    - Streaming support for real-time responses
    - Built-in LLM integration via LiteLLM
    - Thread-based conversation management
    - Simple decorator-based API
    - Production-ready FastAPI server

Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "BubbleTea Team"

# Core Components - UI building blocks
from .components import (
    Text,
    Image,
    Markdown,
    Card,
    Cards,
    Done,
    Pill,
    Pills,
    Video,
    Block,
    Error,
    PaymentRequest,
    BaseComponent,
)

# Decorators - Easy bot creation
from .decorators import chatbot, config

# Server - Production-ready deployment
from .server import run_server

# Schemas - Type definitions
from .schemas import ImageInput, BotConfig

# Public API
__all__ = [
    # Components
    "Text",
    "Image",
    "Markdown",
    "Card",
    "Cards",
    "Done",
    "Pill",
    "Pills",
    "Video",
    "Block",
    "Error",
    "PaymentRequest",
    "BaseComponent",
    "chatbot",
    "config",
    "run_server",
    "ImageInput",
    "BotConfig",
    "LLM",
]


def __getattr__(name: str):
    """
    Lazy load optional dependencies to improve import performance.

    Args:
        name: Attribute name to load

    Returns:
        The requested attribute

    Raises:
        ImportError: If LiteLLM is not installed
        AttributeError: If attribute doesn't exist
    """
    if name == "LLM":
        try:
            from .llm import LLM

            return LLM
        except ImportError:
            raise ImportError(
                "\n"
                "LiteLLM is not installed. To use LLM features, install with:\n"
                "  pip install 'bubbletea-chat[llm]'\n"
            )
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
