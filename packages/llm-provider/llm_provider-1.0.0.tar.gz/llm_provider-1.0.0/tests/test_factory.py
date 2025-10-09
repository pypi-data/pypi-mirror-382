"""Test factory functionality."""

import pytest
from unittest.mock import Mock, patch

from llm_provider import LLMProviderFactory, OpenAI, Anthropic, Gemini
from llm_provider.utils.exceptions import ProviderNotFoundError, ConfigurationError


class TestLLMProviderFactory:
    """Test cases for LLMProviderFactory."""
    
    def test_factory_initialization(self):
        """Test factory initialization with provider instance."""
        provider = OpenAI(api_key="test-key")
        factory = LLMProviderFactory(provider)
        
        assert factory.provider == provider
        assert factory.config is not None
    
    def test_create_provider_openai(self):
        """Test creating OpenAI provider via factory method."""
        factory = LLMProviderFactory.create_provider(
            "openai",
            api_key="test-key"
        )
        
        assert isinstance(factory.provider, OpenAI)
        assert factory.provider.config["api_key"] == "test-key"
    
    def test_create_provider_anthropic(self):
        """Test creating Anthropic provider via factory method."""
        factory = LLMProviderFactory.create_provider(
            "anthropic",
            api_key="test-key"
        )
        
        assert isinstance(factory.provider, Anthropic)
        assert factory.provider.config["api_key"] == "test-key"
    
    def test_create_provider_gemini(self):
        """Test creating Gemini provider via factory method."""
        factory = LLMProviderFactory.create_provider(
            "gemini",
            api_key="test-key"
        )
        
        assert isinstance(factory.provider, Gemini)
        assert factory.provider.config["api_key"] == "test-key"
    
    def test_create_provider_not_found(self):
        """Test creating provider with invalid name."""
        with pytest.raises(ProviderNotFoundError):
            LLMProviderFactory.create_provider("invalid_provider")
    
    def test_create_provider_configuration_error(self):
        """Test creating provider with invalid configuration."""
        with pytest.raises(ConfigurationError):
            LLMProviderFactory.create_provider("openai")  # Missing API key
    
    def test_get_available_providers(self):
        """Test getting list of available providers."""
        providers = LLMProviderFactory.get_available_providers()
        
        assert "openai" in providers
        assert "anthropic" in providers
        assert "gemini" in providers
    
    def test_register_custom_provider(self):
        """Test registering a custom provider."""
        from llm_provider.base_provider import BaseLLMProvider, LLMResponse
        
        class CustomProvider(BaseLLMProvider):
            def _validate_config(self):
                pass
            
            def generate(self, prompt, history=None, **kwargs):
                return LLMResponse(content="test", model="custom")
            
            def get_available_models(self):
                return ["custom-model"]
        
        LLMProviderFactory.register_provider("custom", CustomProvider)
        
        assert "custom" in LLMProviderFactory.get_available_providers()
        
        factory = LLMProviderFactory.create_provider("custom")
        assert isinstance(factory.provider, CustomProvider)
    
    def test_switch_provider(self):
        """Test switching between providers."""
        openai_provider = OpenAI(api_key="test-key")
        anthropic_provider = Anthropic(api_key="test-key")
        
        factory = LLMProviderFactory(openai_provider)
        assert isinstance(factory.provider, OpenAI)
        
        factory.switch_provider(anthropic_provider)
        assert isinstance(factory.provider, Anthropic)
    
    def test_get_provider_info(self):
        """Test getting provider information."""
        provider = OpenAI(api_key="test-key")
        factory = LLMProviderFactory(provider)
        
        info = factory.get_provider_info()
        
        assert info["name"] == "openai"
        assert info["class"] == "OpenAI"
        assert "config" in info
    
    @patch('llm_provider.providers.openai_provider.requests.post')
    def test_generate_delegation(self, mock_post):
        """Test that generate method delegates to provider."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello, world!"}}],
            "model": "gpt-3.5-turbo",
            "usage": {"total_tokens": 10}
        }
        mock_post.return_value = mock_response
        
        provider = OpenAI(api_key="test-key")
        factory = LLMProviderFactory(provider)
        
        response = factory.generate("Hello")
        
        assert response.content == "Hello, world!"
        assert response.model == "gpt-3.5-turbo"
        mock_post.assert_called_once()
    
    @patch('llm_provider.providers.openai_provider.requests.get')
    def test_get_available_models_delegation(self, mock_get):
        """Test that get_available_models delegates to provider."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-3.5-turbo"},
                {"id": "gpt-4"}
            ]
        }
        mock_get.return_value = mock_response
        
        provider = OpenAI(api_key="test-key")
        factory = LLMProviderFactory(provider)
        
        models = factory.get_available_models()
        
        assert "gpt-3.5-turbo" in models
        assert "gpt-4" in models
        mock_get.assert_called_once()