"""Anthropic provider implementation."""

import json
from typing import List, Dict, Any, Optional, Union
import requests

from ..base_provider import BaseLLMProvider, LLMResponse, Message
from ..utils.exceptions import ConfigurationError, APIError, RateLimitError, AuthenticationError
from ..utils.logger import get_logger


class Anthropic(BaseLLMProvider):
    """
    Anthropic provider implementation.
    
    Supports Claude models through Anthropic API.
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://api.anthropic.com/v1",
        model: str = "claude-3-sonnet-20240229",
        **kwargs
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            base_url: Base URL for Anthropic API
            model: Default model to use
            **kwargs: Additional configuration
        """
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model=model,
            **kwargs
        )
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
    def _validate_config(self) -> None:
        """Validate Anthropic configuration."""
        if not self.config.get('api_key'):
            raise ConfigurationError("Anthropic API key is required", "anthropic")
        
        if not self.config.get('base_url'):
            raise ConfigurationError("Anthropic base URL is required", "anthropic")
    
    def generate(
        self, 
        prompt: str, 
        history: Optional[List[Union[Message, Dict[str, str]]]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response using Anthropic API.
        
        Args:
            prompt: Input prompt
            history: Conversation history
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            LLMResponse with generated content
        """
        self.logger.info(f"Generating response for prompt: {prompt[:50]}...")
        
        # Prepare messages
        messages = self._prepare_messages(prompt, history)
        
        # Prepare request data
        data = {
            "model": kwargs.get("model", self.config.get("model", "claude-3-sonnet-20240229")),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        # Add optional parameters
        if "temperature" in kwargs:
            data["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]
        if "stop_sequences" in kwargs:
            data["stop_sequences"] = kwargs["stop_sequences"]
        
        # Make API request
        try:
            response = self._make_request("/messages", data)
            
            # Parse response
            content = response["content"][0]["text"]
            model = response["model"]
            usage = response.get("usage", {})
            
            self.logger.info(f"Successfully generated response using model: {model}")
            
            return LLMResponse(
                content=content,
                model=model,
                usage=usage,
                metadata={"provider": "anthropic"}
            )
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available Anthropic models."""
        # Anthropic doesn't have a models endpoint, return known models
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ]
    
    def _make_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make HTTP request to Anthropic API.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
            
        Raises:
            APIError: For API errors
            RateLimitError: For rate limit errors
            AuthenticationError: For auth errors
        """
        url = f"{self.config['base_url']}{endpoint}"
        headers = {
            "x-api-key": self.config['api_key'],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        try:
            if data:
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            # Handle different status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key", "anthropic", response.status_code)
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded", "anthropic", response.status_code)
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
                raise APIError(error_msg, "anthropic", response.status_code)
                
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}", "anthropic")