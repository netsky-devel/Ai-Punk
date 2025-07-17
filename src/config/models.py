"""
Configuration Models
Data structures for application configuration
"""

import os
from dataclasses import dataclass
from typing import Optional
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
    max_iterations: int = 50
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