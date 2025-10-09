"""Settings and configuration for LLM Provider package."""

from .utils.config import Config

# Default configuration instance
default_config = Config()

# Version information
__version__ = "1.0.0"
__author__ = "Sadık Hanecioglu"
__email__ = "sadikhanecioglu@example.com"

# Package metadata
PACKAGE_NAME = "llm-provider"
PACKAGE_DESCRIPTION = "A unified interface for multiple LLM providers"
PACKAGE_URL = "https://github.com/sadikhanecioglu/llm-provider"

# Default timeouts and limits
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_MAX_TOKENS = 1000

# Supported providers
SUPPORTED_PROVIDERS = ["openai", "anthropic", "gemini"]

# Rate limiting settings
DEFAULT_RATE_LIMIT = {
    "requests_per_minute": 60,
    "tokens_per_minute": 40000
}