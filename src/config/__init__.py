"""
AI Punk Configuration System
Centralized configuration management for the application
"""

import os
from .models import AIProvider, AIProviderConfig, AgentConfig, UIConfig, AppConfig
from .manager import ConfigManager

# Export main models and enums
__all__ = [
    'AIProvider',
    'AIProviderConfig', 
    'AgentConfig',
    'UIConfig',
    'AppConfig',
    'get_config',
    'save_config',
    'set_workspace',
    'set_ai_provider'
]

# Global config manager instance
_config_manager = ConfigManager()


def get_config() -> AppConfig:
    """Get current configuration"""
    return _config_manager.load_config()


def save_config(config: AppConfig):
    """Save configuration"""
    _config_manager.save_config(config)


def set_workspace(path: str):
    """Set workspace path"""
    config = get_config()
    config.workspace_path = os.path.abspath(path)
    save_config(config)


def set_ai_provider(provider: AIProvider, api_key: str, model: str):
    """Set AI provider configuration"""
    config = get_config()
    config.ai_provider = AIProviderConfig(
        provider=provider,
        api_key=api_key,
        model=model
    )
    save_config(config) 