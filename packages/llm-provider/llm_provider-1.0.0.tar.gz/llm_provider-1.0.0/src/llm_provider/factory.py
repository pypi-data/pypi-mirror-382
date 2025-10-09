"""LLM Provider Factory implementation."""

from typing import Type, Dict, Any, Optional
from .base_provider import BaseLLMProvider
from .providers import OpenAI, Anthropic, Gemini
from .utils.exceptions import ProviderNotFoundError, ConfigurationError
from .utils.logger import get_logger
from .utils.config import Config


class LLMProviderFactory:
    """
    Factory class for creating and managing LLM providers.
    
    This class implements the Factory Pattern and provides a unified
    interface for working with different LLM providers.
    """
    
    # Registry of available providers
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        'openai': OpenAI,
        'anthropic': Anthropic,
        'gemini': Gemini,
    }
    
    def __init__(self, provider: BaseLLMProvider, config: Optional[Config] = None):
        """
        Initialize the factory with a provider instance.
        
        Args:
            provider: An instance of a provider class
            config: Optional configuration object
        """
        self.provider = provider
        self.config = config or Config()
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
        self.logger.info(f"Initialized factory with provider: {provider.get_provider_name()}")
    
    def generate(self, prompt: str, history: Optional[list] = None, **kwargs):
        """
        Generate response using the configured provider.
        
        Args:
            prompt: Input prompt
            history: Conversation history
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response from the provider
        """
        return self.provider.generate(prompt, history, **kwargs)
    
    def get_available_models(self):
        """Get available models from the current provider."""
        return self.provider.get_available_models()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current provider.
        
        Returns:
            Dictionary with provider information
        """
        return {
            "name": self.provider.get_provider_name(),
            "class": self.provider.__class__.__name__,
            "config": self.provider.config
        }
    
    @classmethod
    def create_provider(
        cls, 
        provider_name: str, 
        config: Optional[Config] = None,
        **kwargs
    ) -> 'LLMProviderFactory':
        """
        Create a factory instance with the specified provider.
        
        Args:
            provider_name: Name of the provider ('openai', 'anthropic', 'gemini')
            config: Optional configuration object
            **kwargs: Provider-specific configuration
            
        Returns:
            LLMProviderFactory instance
            
        Raises:
            ProviderNotFoundError: If provider is not found
            ConfigurationError: If configuration is invalid
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ProviderNotFoundError(
                f"Provider '{provider_name}' not found. Available providers: {available}",
                provider_name
            )
        
        try:
            provider_class = cls._providers[provider_name]
            provider_instance = provider_class(**kwargs)
            return cls(provider_instance, config)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to create provider '{provider_name}': {str(e)}",
                provider_name
            )
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]):
        """
        Register a new provider class.
        
        Args:
            name: Provider name
            provider_class: Provider class that extends BaseLLMProvider
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError("Provider class must extend BaseLLMProvider")
        
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names."""
        return list(cls._providers.keys())
    
    def switch_provider(self, provider: BaseLLMProvider):
        """
        Switch to a different provider instance.
        
        Args:
            provider: New provider instance
        """
        old_provider = self.provider.get_provider_name()
        self.provider = provider
        new_provider = self.provider.get_provider_name()
        
        self.logger.info(f"Switched provider from {old_provider} to {new_provider}")