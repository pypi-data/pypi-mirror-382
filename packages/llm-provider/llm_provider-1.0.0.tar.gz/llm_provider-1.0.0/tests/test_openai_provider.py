"""Test OpenAI provider functionality."""

import pytest
from unittest.mock import Mock, patch

from llm_provider.providers import OpenAI
from llm_provider.base_provider import Message, LLMResponse
from llm_provider.utils.exceptions import (
    ConfigurationError, 
    APIError, 
    RateLimitError, 
    AuthenticationError
)


class TestOpenAIProvider:
    """Test cases for OpenAI provider."""
    
    def test_initialization(self):
        """Test OpenAI provider initialization."""
        provider = OpenAI(api_key="test-key")
        
        assert provider.config["api_key"] == "test-key"
        assert provider.config["base_url"] == "https://api.openai.com/v1"
        assert provider.config["model"] == "gpt-3.5-turbo"
    
    def test_initialization_with_custom_config(self):
        """Test OpenAI provider initialization with custom config."""
        provider = OpenAI(
            api_key="test-key",
            base_url="https://custom.api.com/v1",
            model="gpt-4"
        )
        
        assert provider.config["api_key"] == "test-key"
        assert provider.config["base_url"] == "https://custom.api.com/v1"
        assert provider.config["model"] == "gpt-4"
    
    def test_validation_missing_api_key(self):
        """Test validation fails when API key is missing."""
        with pytest.raises(ConfigurationError, match="OpenAI API key is required"):
            OpenAI(api_key="")
    
    def test_get_provider_name(self):
        """Test getting provider name."""
        provider = OpenAI(api_key="test-key")
        assert provider.get_provider_name() == "openai"
    
    @patch('llm_provider.providers.openai_provider.requests.post')
    def test_generate_success(self, mock_post):
        """Test successful generation."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello, world!"}}],
            "model": "gpt-3.5-turbo",
            "usage": {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}
        }
        mock_post.return_value = mock_response
        
        provider = OpenAI(api_key="test-key")
        response = provider.generate("Hello")
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Hello, world!"
        assert response.model == "gpt-3.5-turbo"
        assert response.usage["total_tokens"] == 10
        assert response.metadata["provider"] == "openai"
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "https://api.openai.com/v1/chat/completions" in call_args[0][0]
    
    @patch('llm_provider.providers.openai_provider.requests.post')
    def test_generate_with_history(self, mock_post):
        """Test generation with conversation history."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Nice to meet you!"}}],
            "model": "gpt-3.5-turbo",
            "usage": {"total_tokens": 15}
        }
        mock_post.return_value = mock_response
        
        provider = OpenAI(api_key="test-key")
        history = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!")
        ]
        
        response = provider.generate("What's your name?", history=history)
        
        assert response.content == "Nice to meet you!"
        
        # Check that history was included in the request
        call_args = mock_post.call_args
        request_data = call_args[1]["json"]
        messages = request_data["messages"]
        
        assert len(messages) == 3  # 2 history + 1 current
        assert messages[0]["content"] == "Hello"
        assert messages[1]["content"] == "Hi there!"
        assert messages[2]["content"] == "What's your name?"
    
    @patch('llm_provider.providers.openai_provider.requests.post')
    def test_generate_with_parameters(self, mock_post):
        """Test generation with custom parameters."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Creative response"}}],
            "model": "gpt-4",
            "usage": {"total_tokens": 20}
        }
        mock_post.return_value = mock_response
        
        provider = OpenAI(api_key="test-key")
        response = provider.generate(
            "Write a story",
            model="gpt-4",
            temperature=0.9,
            max_tokens=500,
            top_p=0.95
        )
        
        assert response.content == "Creative response"
        
        # Check request parameters
        call_args = mock_post.call_args
        request_data = call_args[1]["json"]
        
        assert request_data["model"] == "gpt-4"
        assert request_data["temperature"] == 0.9
        assert request_data["max_tokens"] == 500
        assert request_data["top_p"] == 0.95
    
    @patch('llm_provider.providers.openai_provider.requests.post')
    def test_authentication_error(self, mock_post):
        """Test handling of authentication errors."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {"message": "Invalid API key"}
        }
        mock_post.return_value = mock_response
        
        provider = OpenAI(api_key="invalid-key")
        
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            provider.generate("Hello")
    
    @patch('llm_provider.providers.openai_provider.requests.post')
    def test_rate_limit_error(self, mock_post):
        """Test handling of rate limit errors."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {"message": "Rate limit exceeded"}
        }
        mock_post.return_value = mock_response
        
        provider = OpenAI(api_key="test-key")
        
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            provider.generate("Hello")
    
    @patch('llm_provider.providers.openai_provider.requests.post')
    def test_api_error(self, mock_post):
        """Test handling of general API errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": {"message": "Internal server error"}
        }
        mock_post.return_value = mock_response
        
        provider = OpenAI(api_key="test-key")
        
        with pytest.raises(APIError, match="Internal server error"):
            provider.generate("Hello")
    
    @patch('llm_provider.providers.openai_provider.requests.get')
    def test_get_available_models_success(self, mock_get):
        """Test getting available models successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-3.5-turbo"},
                {"id": "gpt-4"},
                {"id": "gpt-4-turbo-preview"}
            ]
        }
        mock_get.return_value = mock_response
        
        provider = OpenAI(api_key="test-key")
        models = provider.get_available_models()
        
        assert "gpt-3.5-turbo" in models
        assert "gpt-4" in models
        assert "gpt-4-turbo-preview" in models
        assert len(models) == 3
    
    @patch('llm_provider.providers.openai_provider.requests.get')
    def test_get_available_models_fallback(self, mock_get):
        """Test fallback when models endpoint fails."""
        mock_get.side_effect = Exception("Network error")
        
        provider = OpenAI(api_key="test-key")
        models = provider.get_available_models()
        
        # Should return fallback models
        assert "gpt-4" in models
        assert "gpt-3.5-turbo" in models
        assert len(models) > 0
    
    def test_prepare_messages(self):
        """Test message preparation functionality."""
        provider = OpenAI(api_key="test-key")
        
        # Test with Message objects
        history = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi!")
        ]
        messages = provider._prepare_messages("How are you?", history)
        
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Hi!"
        assert messages[2]["role"] == "user"
        assert messages[2]["content"] == "How are you?"
        
        # Test with dict objects
        history_dict = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"}
        ]
        messages = provider._prepare_messages("How are you?", history_dict)
        
        assert len(messages) == 3
        assert messages[0]["content"] == "Hello"
        assert messages[1]["content"] == "Hi!"
        assert messages[2]["content"] == "How are you?"