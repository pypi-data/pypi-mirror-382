"""Custom exceptions for LLM Provider package."""


class LLMProviderError(Exception):
    """Base exception for all LLM provider errors."""
    
    def __init__(self, message: str, provider_name: str = None):
        super().__init__(message)
        self.provider_name = provider_name


class ConfigurationError(LLMProviderError):
    """Raised when there's a configuration error."""
    pass


class ProviderNotFoundError(LLMProviderError):
    """Raised when a requested provider is not found."""
    pass


class APIError(LLMProviderError):
    """Raised when there's an API error from the provider."""
    
    def __init__(self, message: str, provider_name: str = None, status_code: int = None):
        super().__init__(message, provider_name)
        self.status_code = status_code


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    pass