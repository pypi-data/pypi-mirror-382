"""
LLM Provider Factory Package

A unified interface for multiple Large Language Model providers.
Supports OpenAI, Anthropic, and Google Gemini with a clean, extensible architecture.

Example usage:
    from llm_provider import LLMProviderFactory, OpenAI
    
    # Method 1: Using provider instance
    provider = LLMProviderFactory(OpenAI(api_key="your-key"))
    response = provider.generate(prompt="Hello", history=[])
    print(response.content)
    
    # Method 2: Using factory method
    provider = LLMProviderFactory.create_provider("openai", api_key="your-key")
    response = provider.generate(prompt="Hello", history=[])
    print(response.content)
"""

from .factory import LLMProviderFactory
from .base_provider import BaseLLMProvider, Message, LLMResponse
from .providers import OpenAI, Anthropic, Gemini
from .utils import Config, get_logger
from .utils.exceptions import (
    LLMProviderError,
    ConfigurationError,
    ProviderNotFoundError,
    APIError,
    RateLimitError,
    AuthenticationError
)
from .settings import __version__

# For backward compatibility and convenience imports
OpenAi = OpenAI  # Turkish naming convention

__all__ = [
    # Main classes
    'LLMProviderFactory',
    'BaseLLMProvider',
    'Message',
    'LLMResponse',
    
    # Providers
    'OpenAI',
    'OpenAi',  # Alias
    'Anthropic',
    'Gemini',
    
    # Utilities
    'Config',
    'get_logger',
    
    # Exceptions
    'LLMProviderError',
    'ConfigurationError',
    'ProviderNotFoundError',
    'APIError',
    'RateLimitError',
    'AuthenticationError',
    
    # Metadata
    '__version__',
]

__version__ = __version__