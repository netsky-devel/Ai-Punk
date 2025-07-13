"""
AI Punk Configuration System
Handles user settings, AI provider configuration, and workspace management
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class AIProvider(Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"

@dataclass
class AIProviderConfig:
    """Configuration for AI provider"""
    provider: AIProvider
    api_key: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.1

@dataclass
class AgentConfig:
    """Agent behavior configuration"""
    max_iterations: int = 10
    verbose: bool = True
    show_full_process: bool = True
    auto_save: bool = True

@dataclass
class UIConfig:
    """User interface configuration"""
    use_rich_formatting: bool = True
    terminal_width: int = 120
    show_timestamps: bool = True
    color_scheme: str = "dark"

@dataclass
class AppConfig:
    """Main application configuration"""
    workspace_path: Optional[str] = None
    ai_provider: Optional[AIProviderConfig] = None
    agent: AgentConfig = None
    ui: UIConfig = None
    
    def __post_init__(self):
        if self.workspace_path is None:
            self.workspace_path = os.getcwd()
        if self.agent is None:
            self.agent = AgentConfig()
        if self.ui is None:
            self.ui = UIConfig()

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_dir: str = ".ai-punk"):
        self.config_dir = Path.home() / config_dir
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        
    def load_config(self) -> AppConfig:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return self._dict_to_config(data)
            except Exception as e:
                print(f"Error loading config: {e}")
                
        return AppConfig()
    
    def save_config(self, config: AppConfig):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_to_dict(config), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _config_to_dict(self, config: AppConfig) -> Dict[str, Any]:
        """Convert config to dictionary"""
        data = asdict(config)
        if config.ai_provider:
            data['ai_provider']['provider'] = config.ai_provider.provider.value
        return data
    
    def _dict_to_config(self, data: Dict[str, Any]) -> AppConfig:
        """Convert dictionary to config"""
        config = AppConfig()
        
        if 'workspace_path' in data:
            config.workspace_path = data['workspace_path']
            
        if 'ai_provider' in data and data['ai_provider']:
            provider_data = data['ai_provider']
            config.ai_provider = AIProviderConfig(
                provider=AIProvider(provider_data['provider']),
                api_key=provider_data['api_key'],
                model=provider_data['model'],
                max_tokens=provider_data.get('max_tokens', 4000),
                temperature=provider_data.get('temperature', 0.1)
            )
            
        if 'agent' in data:
            agent_data = data['agent']
            config.agent = AgentConfig(
                max_iterations=agent_data.get('max_iterations', 10),
                verbose=agent_data.get('verbose', True),
                show_full_process=agent_data.get('show_full_process', True),
                auto_save=agent_data.get('auto_save', True)
            )
            
        if 'ui' in data:
            ui_data = data['ui']
            config.ui = UIConfig(
                use_rich_formatting=ui_data.get('use_rich_formatting', True),
                terminal_width=ui_data.get('terminal_width', 120),
                show_timestamps=ui_data.get('show_timestamps', True),
                color_scheme=ui_data.get('color_scheme', 'dark')
            )
            
        return config

# Global config instance
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