"""Google Gemini provider implementation."""

import json
from typing import List, Dict, Any, Optional, Union
import requests

from ..base_provider import BaseLLMProvider, LLMResponse, Message
from ..utils.exceptions import ConfigurationError, APIError, RateLimitError, AuthenticationError
from ..utils.logger import get_logger


class Gemini(BaseLLMProvider):
    """
    Google Gemini provider implementation.
    
    Supports Gemini models through Google AI API.
    """
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        model: str = "gemini-1.5-flash",
        **kwargs
    ):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google AI API key
            base_url: Base URL for Google AI API
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
        """Validate Gemini configuration."""
        if not self.config.get('api_key'):
            raise ConfigurationError("Gemini API key is required", "gemini")
        
        if not self.config.get('base_url'):
            raise ConfigurationError("Gemini base URL is required", "gemini")
    
    def generate(
        self, 
        prompt: str, 
        history: Optional[List[Union[Message, Dict[str, str]]]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response using Gemini API.
        
        Args:
            prompt: Input prompt
            history: Conversation history
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            LLMResponse with generated content
        """
        self.logger.info(f"Generating response for prompt: {prompt[:50]}...")
        
        # Prepare contents for Gemini format
        contents = self._prepare_gemini_contents(prompt, history)
        
        # Prepare request data
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 1000),
            }
        }
        
        # Add optional parameters
        if "top_p" in kwargs:
            data["generationConfig"]["topP"] = kwargs["top_p"]
        if "top_k" in kwargs:
            data["generationConfig"]["topK"] = kwargs["top_k"]
        if "stop_sequences" in kwargs:
            data["generationConfig"]["stopSequences"] = kwargs["stop_sequences"]
        
        # Make API request
        model = kwargs.get("model", self.config.get("model", "gemini-1.5-flash"))
        try:
            response = self._make_request(f"/models/{model}:generateContent", data)
            
            # Parse response
            content = response["candidates"][0]["content"]["parts"][0]["text"]
            usage = response.get("usageMetadata", {})
            
            self.logger.info(f"Successfully generated response using model: {model}")
            
            return LLMResponse(
                content=content,
                model=model,
                usage=usage,
                metadata={"provider": "gemini"}
            )
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available Gemini models."""
        try:
            response = self._make_request("/models")
            models = []
            for model in response.get("models", []):
                model_name = model["name"].split("/")[-1]
                if "generateContent" in model.get("supportedGenerationMethods", []):
                    models.append(model_name)
            return sorted(models)
        except Exception as e:
            self.logger.error(f"Error fetching models: {str(e)}")
            # Return common models as fallback
            return [
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-1.0-pro"
            ]
    
    def _prepare_gemini_contents(
        self, 
        prompt: str, 
        history: Optional[List[Union[Message, Dict[str, str]]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare contents in Gemini format.
        
        Args:
            prompt: Input prompt
            history: Conversation history
            
        Returns:
            List of formatted contents
        """
        contents = []
        
        # Add history messages
        if history:
            for msg in history:
                if isinstance(msg, Message):
                    role = "user" if msg.role == "user" else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": msg.content}]
                    })
                elif isinstance(msg, dict):
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": msg["content"]}]
                    })
        
        # Add current prompt
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        return contents
    
    def _make_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make HTTP request to Gemini API.
        
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
        params = {"key": self.config['api_key']}
        headers = {"Content-Type": "application/json"}
        
        try:
            if data:
                response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, params=params, timeout=30)
            
            # Handle different status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key", "gemini", response.status_code)
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded", "gemini", response.status_code)
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
                raise APIError(error_msg, "gemini", response.status_code)
                
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}", "gemini")