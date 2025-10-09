"""Test configuration and utilities."""

import pytest
from unittest.mock import Mock

from llm_provider.utils import Config, get_logger
from llm_provider.utils.exceptions import (
    LLMProviderError,
    ConfigurationError,
    ProviderNotFoundError,
    APIError,
    RateLimitError,
    AuthenticationError
)


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_initialization(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.default_timeout == 30
        assert config.default_max_retries == 3
        assert config.enable_rate_limiting is True
        assert config.log_level == "INFO"
        assert config.env_prefix == "LLM_PROVIDER_"
    
    def test_get_provider_config(self):
        """Test getting provider-specific configuration."""
        config = Config()
        config.set_provider_config("openai", {"model": "gpt-4"})
        
        openai_config = config.get_provider_config("openai")
        assert openai_config["model"] == "gpt-4"
        
        # Test case insensitive
        openai_config_caps = config.get_provider_config("OPENAI")
        assert openai_config_caps["model"] == "gpt-4"
        
        # Test non-existent provider
        empty_config = config.get_provider_config("nonexistent")
        assert empty_config == {}
    
    def test_set_provider_config(self):
        """Test setting provider-specific configuration."""
        config = Config()
        
        test_config = {
            "model": "gpt-4",
            "temperature": 0.8,
            "max_tokens": 1000
        }
        
        config.set_provider_config("openai", test_config)
        retrieved_config = config.get_provider_config("openai")
        
        assert retrieved_config == test_config


class TestLogger:
    """Test cases for logging utilities."""
    
    def test_get_logger(self):
        """Test logger creation."""
        logger = get_logger("test_logger")
        
        assert logger.name == "test_logger"
        assert len(logger.handlers) > 0
    
    def test_get_logger_with_level(self):
        """Test logger creation with specific level."""
        logger = get_logger("test_logger", "DEBUG")
        
        assert logger.level == 10  # DEBUG level


class TestExceptions:
    """Test cases for custom exceptions."""
    
    def test_llm_provider_error(self):
        """Test base LLMProviderError."""
        error = LLMProviderError("Test error", "test_provider")
        
        assert str(error) == "Test error"
        assert error.provider_name == "test_provider"
    
    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Config error", "openai")
        
        assert str(error) == "Config error"
        assert error.provider_name == "openai"
        assert isinstance(error, LLMProviderError)
    
    def test_provider_not_found_error(self):
        """Test ProviderNotFoundError."""
        error = ProviderNotFoundError("Provider not found", "invalid")
        
        assert str(error) == "Provider not found"
        assert error.provider_name == "invalid"
        assert isinstance(error, LLMProviderError)
    
    def test_api_error(self):
        """Test APIError."""
        error = APIError("API error", "openai", 500)
        
        assert str(error) == "API error"
        assert error.provider_name == "openai"
        assert error.status_code == 500
        assert isinstance(error, LLMProviderError)
    
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError("Rate limit", "openai", 429)
        
        assert str(error) == "Rate limit"
        assert error.provider_name == "openai"
        assert error.status_code == 429
        assert isinstance(error, APIError)
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Auth failed", "openai", 401)
        
        assert str(error) == "Auth failed"
        assert error.provider_name == "openai"
        assert error.status_code == 401
        assert isinstance(error, APIError)