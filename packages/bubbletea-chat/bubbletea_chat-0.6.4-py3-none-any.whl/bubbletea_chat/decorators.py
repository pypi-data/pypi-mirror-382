"""
BubbleTea Decorators
====================

Powerful decorators for creating chatbots with minimal boilerplate.
Supports both synchronous and asynchronous functions, streaming,
and automatic parameter injection.

Core Decorators:
    @chatbot - Transform any function into a chatbot endpoint
    @config - Define bot configuration and metadata
"""

import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    AsyncGenerator,
    Union,
    Tuple,
    Optional,
)

from .components import Component, Done
from .schemas import ComponentChatRequest, ComponentChatResponse, ImageInput

# Global registries for managing chatbots and configurations
_config_function: Optional[Tuple[Callable, str]] = None  # Legacy support
_chatbot_registry: Dict[str, "ChatbotFunction"] = {}  # All registered chatbots
_bot_config_registry: Dict[str, Callable] = {}  # Bot-specific configurations


class ChatbotFunction:
    """
    Wrapper class for chatbot functions.

    Handles function execution, parameter injection, streaming,
    and configuration management for chatbot endpoints.

    Attributes:
        func: The wrapped chatbot function
        name: Bot name for identification
        url_path: HTTP endpoint path
        stream: Whether responses are streamed
        is_async: Whether the function is async
        is_generator: Whether the function yields responses
    """

    def __init__(
        self,
        func: Callable,
        name: str = None,
        stream: bool = None,
        url_path: str = None,
    ):
        """Initialize a chatbot function wrapper.

        Args:
            func: The function to wrap
            name: Optional bot name (defaults to function name)
            stream: Force streaming mode (auto-detected if None)
            url_path: Custom URL path (defaults to /chat)
        """
        self.func = func
        self.name = name or func.__name__
        self.url_path = url_path or "/chat"
        self.is_async = inspect.iscoroutinefunction(func)
        self.is_generator = inspect.isgeneratorfunction(
            func
        ) or inspect.isasyncgenfunction(func)
        self.stream = stream if stream is not None else self.is_generator
        self._config_func = None

    def config(self, func: Callable) -> Callable:
        """
        Decorator to attach configuration to this specific bot.

        Allows bot-specific configuration without global config.

        Args:
            func: Configuration function returning BotConfig

        Returns:
            The configuration function (unchanged)

        Example:
            >>> @bt.chatbot("weather-bot")
            ... def weather_bot(message: str):
            ...     return bt.Text("Current weather...")
            ...
            >>> @weather_bot.config
            ... def config():
            ...     return BotConfig(
            ...         name="Weather Bot",
            ...         emoji="🌤️",
            ...         description="Real-time weather updates"
            ...     )
        """
        self._config_func = func
        _bot_config_registry[self.url_path] = func
        return func

    async def __call__(
        self,
        message: str,
        images: List[ImageInput] = None,
        user_email: str = None,
        user_uuid: str = None,
        conversation_uuid: str = None,
        chat_history: Union[List[Dict[str, Any]], str] = None,
        thread_id: str = None,
    ) -> Union[List[Component], AsyncGenerator[Component, None]]:
        """
        Execute the wrapped chatbot function with smart parameter injection.

        Automatically provides only the parameters that the function accepts,
        allowing for flexible function signatures.

        Args:
            message: User's input message
            images: Optional list of images from user
            user_email: User's email if authenticated
            user_uuid: User's unique identifier
            conversation_uuid: Conversation identifier
            chat_history: Previous messages in conversation
            thread_id: Thread identifier for grouped conversations

        Returns:
            List of components or async generator for streaming
        """
        # Inspect function signature for smart parameter injection
        sig = inspect.signature(self.func)
        params = list(sig.parameters.keys())

        # Build kwargs based on what the function accepts
        kwargs = {}
        if "images" in params:
            kwargs["images"] = images
        if "user_email" in params:
            kwargs["user_email"] = user_email
        if "user_uuid" in params:
            kwargs["user_uuid"] = user_uuid
        if "conversation_uuid" in params:
            kwargs["conversation_uuid"] = conversation_uuid
        if "thread_id" in params:
            kwargs["thread_id"] = thread_id

        # Handle chat_history parameter compatibility
        if "chat_history" in params:
            # Check if the function signature expects a specific type
            param_annotation = sig.parameters["chat_history"].annotation
            if param_annotation is str or param_annotation == Optional[str]:
                # Function expects string, convert list to string if needed
                if isinstance(chat_history, list):
                    kwargs["chat_history"] = str(chat_history)
                else:
                    kwargs["chat_history"] = chat_history
            else:
                # Function expects list or is untyped, keep as is
                kwargs["chat_history"] = chat_history

        # Call function with appropriate parameters
        if self.is_async:
            result = await self.func(message, **kwargs)
        else:
            result = self.func(message, **kwargs)

        # Handle different return types
        if self.is_generator:
            # Generator functions yield components
            if inspect.isasyncgen(result):
                return result
            else:
                # Convert sync generator to async
                async def async_wrapper():
                    for item in result:
                        yield item

                return async_wrapper()
        else:
            # Non-generator functions return list of components
            if not isinstance(result, list):
                result = [result]
            return result

    async def handle_request(self, request: ComponentChatRequest):
        """Handle incoming chat request and return appropriate response"""
        components = await self(
            request.message,
            images=request.images,
            user_email=request.user_email,
            user_uuid=request.user_uuid,
            conversation_uuid=request.conversation_uuid,
            chat_history=request.chat_history,
            thread_id=request.thread_id,
        )

        if self.stream:
            # Return async generator for streaming
            return components
        else:
            # Return list for non-streaming
            if inspect.isasyncgen(components):
                # Collect all components from generator
                collected = []
                async for component in components:
                    if not isinstance(component, Done):
                        collected.append(component)
                return ComponentChatResponse(responses=collected)
            else:
                return ComponentChatResponse(responses=components)


def chatbot(
    name_or_url: Union[str, Callable] = None, stream: bool = None, name: str = None
) -> Union[ChatbotFunction, Callable[[Callable], ChatbotFunction]]:
    """
    Transform any function into a BubbleTea chatbot.

    This decorator is the heart of BubbleTea. It converts regular Python
    functions into fully-featured chatbot endpoints with automatic:
    - HTTP endpoint creation
    - Streaming support detection
    - Parameter injection
    - Response formatting

    Args:
        name_or_url: URL path for the bot (e.g., "weather" → /weather)
                    Or the function itself when used without parentheses
        stream: Force streaming mode (auto-detected if None)
        name: Explicit bot name (defaults to function name)

    Returns:
        ChatbotFunction wrapper or decorator function

    Examples:
        Simple bot:
            >>> @chatbot
            ... def echo_bot(message: str):
            ...     return Text(f"Echo: {message}")

        Custom endpoint:
            >>> @chatbot("weather")
            ... def weather_bot(message: str, user_uuid: str):
            ...     return Text(f"Weather for user {user_uuid}")

        Streaming bot:
            >>> @chatbot(stream=True)
            ... async def stream_bot(message: str):
            ...     for word in message.split():
            ...         yield Text(word)
    """

    def decorator(func: Callable) -> ChatbotFunction:
        # Determine URL path
        url_path = None
        bot_name = name

        if isinstance(name_or_url, str):
            # If it doesn't start with /, treat it as URL path and prepend /
            if not name_or_url.startswith("/"):
                url_path = f"/{name_or_url}"
            else:
                url_path = name_or_url
            # If no explicit name provided, derive from URL
            if not bot_name:
                bot_name = name_or_url.strip("/").replace("-", "_").replace("/", "_")

        chatbot_func = ChatbotFunction(
            func, name=bot_name, stream=stream, url_path=url_path
        )

        # Check if this URL path is already registered
        if chatbot_func.url_path in _chatbot_registry:
            raise ValueError(
                f"A chatbot is already registered at URL path '{chatbot_func.url_path}'. "
                f"Each chatbot must have a unique URL path."
            )

        # Register the chatbot function in the global registry
        _chatbot_registry[chatbot_func.url_path] = chatbot_func

        return chatbot_func

    # Allow using @chatbot without parentheses
    if callable(name_or_url):
        func = name_or_url
        chatbot_func = ChatbotFunction(func)

        # Check if this URL path is already registered
        if chatbot_func.url_path in _chatbot_registry:
            raise ValueError(
                f"A chatbot is already registered at URL path '{chatbot_func.url_path}'. "
                f"Each chatbot must have a unique URL path."
            )

        _chatbot_registry[chatbot_func.url_path] = chatbot_func
        return chatbot_func

    return decorator


def get_registered_chatbots() -> Dict[str, ChatbotFunction]:
    """
    Get all registered chatbot functions.

    Returns:
        Dictionary mapping URL paths to ChatbotFunction instances

    Note:
        This is primarily used internally by the server.
        Returns a copy to prevent external modification.
    """
    return _chatbot_registry.copy()


def get_bot_configs() -> Dict[str, Callable]:
    """
    Get all registered bot-specific configurations.

    Returns:
        Dictionary mapping URL paths to configuration functions

    Note:
        Used internally for serving bot configurations.
    """
    return _bot_config_registry.copy()


def config(path: str = "/config") -> Union[Callable, Callable[[Callable], Callable]]:
    """
    Define global bot configuration.

    Sets up a configuration endpoint that returns bot metadata,
    settings, and capabilities. This is used by BubbleTea to
    understand how to interact with your bot.

    Args:
        path: Custom path for config endpoint (default: /config)

    Returns:
        Decorator function or decorated function

    Example:
        >>> @config()
        ... def get_config():
        ...     return BotConfig(
        ...         name="Assistant Bot",
        ...         url="https://bot.example.com",
        ...         is_streaming=True,
        ...         emoji="🤖",
        ...         subtitle="Your AI assistant",
        ...         description="I can help with various tasks",
        ...         initial_text="Hello! How can I help you today?",
        ...         visibility="public",
        ...         authorization="none"
        ...     )

    Note:
        For multiple bots, use bot-specific config instead:
        @bot_name.config
    """

    def decorator(func: Callable) -> Callable:
        global _config_function
        _config_function = (func, path)
        return func

    # Allow using @config without parentheses
    if callable(path):
        func = path
        _config_function = (func, "/config")
        return func

    return decorator
