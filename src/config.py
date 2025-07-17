"""
Legacy Configuration Import
Re-exports from organized config package for backward compatibility
"""

from .config import (
    AIProvider,
    AIProviderConfig,
    AgentConfig, 
    UIConfig,
    AppConfig,
    get_config,
    save_config,
    set_workspace,
    set_ai_provider
)

# Legacy exports for backward compatibility
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