"""
Configuration Manager
Handles saving and loading application configuration
"""

import json
from pathlib import Path
from typing import Dict, Any

from .models import AppConfig, AIProviderConfig, AgentConfig, UIConfig, AIProvider


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
        from dataclasses import asdict
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