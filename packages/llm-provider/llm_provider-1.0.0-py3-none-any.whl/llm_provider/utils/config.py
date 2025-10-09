"""Configuration management for LLM Provider package."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration class for LLM providers."""
    
    # Default timeouts and retries
    default_timeout: int = 30
    default_max_retries: int = 3
    
    # Rate limiting
    enable_rate_limiting: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # Environment variables prefix
    env_prefix: str = "LLM_PROVIDER_"
    
    # Provider-specific configurations
    provider_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Load basic config
        self.default_timeout = int(os.getenv(
            f"{self.env_prefix}TIMEOUT", 
            self.default_timeout
        ))
        
        self.default_max_retries = int(os.getenv(
            f"{self.env_prefix}MAX_RETRIES", 
            self.default_max_retries
        ))
        
        self.log_level = os.getenv(
            f"{self.env_prefix}LOG_LEVEL", 
            self.log_level
        )
        
        self.enable_rate_limiting = os.getenv(
            f"{self.env_prefix}ENABLE_RATE_LIMITING", 
            str(self.enable_rate_limiting)
        ).lower() == "true"
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider configuration dictionary
        """
        return self.provider_configs.get(provider_name.lower(), {})
    
    def set_provider_config(self, provider_name: str, config: Dict[str, Any]):
        """
        Set configuration for a specific provider.
        
        Args:
            provider_name: Name of the provider
            config: Configuration dictionary
        """
        self.provider_configs[provider_name.lower()] = config