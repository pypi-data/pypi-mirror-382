"""
LLM Provider Factory - A unified interface for multiple LLM providers.

This package provides a clean, extensible way to interact with different LLM providers
(OpenAI, Anthropic, Gemini, etc.) through a single, consistent interface.

Example usage:
    ```python
    from llm_provider import LLMProviderFactory, OpenAI
    
    # Method 1: Using factory with provider instance
    provider = LLMProviderFactory(OpenAI())
    response = await provider.generate("Hello, world!")
    
    # Method 2: Using factory with provider name
    factory = LLMProviderFactory()
    factory.set_provider("openai")
    response = await factory.generate("Hello, world!")
    
    # Method 3: Direct provider usage
    factory = LLMProviderFactory.create_openai()
    response = await factory.generate("Hello, world!")
    ```
"""

from .factory import LLMProviderFactory
from .base_provider import BaseLLMProvider
from .providers import (
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    VertexAIProvider,
    OpenAI,
    Anthropic,
    Gemini,
    VertexAI,
)
from .settings import (
    GenerationRequest,
    GenerationResponse,
    StreamChunk,
    Message,
    MessageRole,
    ProviderInfo,
)
from .utils import (
    # Configurations
    ProviderConfig,
    OpenAIConfig,
    AnthropicConfig,
    GeminiConfig,
    VertexAIConfig,
    ConfigManager,
    config_manager,
    # Exceptions
    LLMProviderError,
    ProviderNotFoundError,
    InvalidConfigurationError,
    APIError,
    RateLimitError,
    AuthenticationError,
    ModelNotAvailableError,
    GenerationError,
    # Logger
    logger,
)

__version__ = "0.1.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    # Main factory
    "LLMProviderFactory",
    
    # Base classes
    "BaseLLMProvider",
    
    # Providers
    "OpenAIProvider",
    "AnthropicProvider", 
    "GeminiProvider",
    "VertexAIProvider",
    "OpenAI",
    "Anthropic",
    "Gemini",
    "VertexAI",
    
    # Data models
    "GenerationRequest",
    "GenerationResponse",
    "StreamChunk",
    "Message",
    "MessageRole",
    "ProviderInfo",
    
    # Configurations
    "ProviderConfig",
    "OpenAIConfig",
    "AnthropicConfig",
    "GeminiConfig",
    "VertexAIConfig",
    "ConfigManager",
    "config_manager",
    
    # Exceptions
    "LLMProviderError",
    "ProviderNotFoundError",
    "InvalidConfigurationError",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "ModelNotAvailableError",
    "GenerationError",
    
    # Utilities
    "logger",
]