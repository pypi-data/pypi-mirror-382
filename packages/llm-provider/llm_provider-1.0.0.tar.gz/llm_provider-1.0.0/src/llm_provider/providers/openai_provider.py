"""OpenAI provider implementation."""

import json
from typing import List, Dict, Any, Optional, Union
import requests

from ..base_provider import BaseLLMProvider, LLMResponse, Message
from ..utils.exceptions import ConfigurationError, APIError, RateLimitError, AuthenticationError
from ..utils.logger import get_logger


class OpenAI(BaseLLMProvider):
    """
    OpenAI provider implementation.
    
    Supports GPT models through OpenAI API.
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-3.5-turbo",
        **kwargs
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            base_url: Base URL for OpenAI API
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
        """Validate OpenAI configuration."""
        if not self.config.get('api_key'):
            raise ConfigurationError("OpenAI API key is required", "openai")
        
        if not self.config.get('base_url'):
            raise ConfigurationError("OpenAI base URL is required", "openai")
    
    def generate(
        self, 
        prompt: str, 
        history: Optional[List[Union[Message, Dict[str, str]]]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response using OpenAI API.
        
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
            "model": kwargs.get("model", self.config.get("model", "gpt-3.5-turbo")),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        # Add other optional parameters
        for param in ["top_p", "frequency_penalty", "presence_penalty", "stop"]:
            if param in kwargs:
                data[param] = kwargs[param]
        
        # Make API request
        try:
            response = self._make_request("/chat/completions", data)
            
            # Parse response
            content = response["choices"][0]["message"]["content"]
            model = response["model"]
            usage = response.get("usage", {})
            
            self.logger.info(f"Successfully generated response using model: {model}")
            
            return LLMResponse(
                content=content,
                model=model,
                usage=usage,
                metadata={"provider": "openai"}
            )
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        try:
            response = self._make_request("/models")
            models = [model["id"] for model in response["data"]]
            return sorted(models)
        except Exception as e:
            self.logger.error(f"Error fetching models: {str(e)}")
            # Return common models as fallback
            return [
                "gpt-4",
                "gpt-4-turbo-preview",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ]
    
    def _make_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make HTTP request to OpenAI API.
        
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
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
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
                raise AuthenticationError("Invalid API key", "openai", response.status_code)
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded", "openai", response.status_code)
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
                raise APIError(error_msg, "openai", response.status_code)
                
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}", "openai")