"""Base provider interface for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a message in the conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format."""
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    """Represents a response from an LLM provider."""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    This class defines the interface that all LLM providers must implement.
    It follows the Interface Segregation Principle (ISP) by providing
    a minimal, focused interface.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the provider with configuration.
        
        Args:
            **kwargs: Provider-specific configuration parameters
        """
        self.config = kwargs
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate the provider configuration.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        history: Optional[List[Union[Message, Dict[str, str]]]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            history: Previous conversation history
            **kwargs: Additional generation parameters
            
        Returns:
            LLMResponse object containing the generated content
            
        Raises:
            APIError: If there's an error calling the provider API
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for this provider.
        
        Returns:
            List of model names
        """
        pass
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name
        """
        return self.__class__.__name__.replace('Provider', '').lower()
    
    def _prepare_messages(
        self, 
        prompt: str, 
        history: Optional[List[Union[Message, Dict[str, str]]]] = None
    ) -> List[Dict[str, str]]:
        """
        Prepare messages for the API call.
        
        Args:
            prompt: The input prompt
            history: Previous conversation history
            
        Returns:
            List of formatted messages
        """
        messages = []
        
        # Add history messages
        if history:
            for msg in history:
                if isinstance(msg, Message):
                    messages.append(msg.to_dict())
                elif isinstance(msg, dict):
                    messages.append(msg)
                else:
                    raise ValueError(f"Invalid message format: {type(msg)}")
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        return messages