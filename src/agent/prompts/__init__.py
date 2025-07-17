"""
Advanced Prompts System for AI Punk Agent
Inspired by professional AI coding assistants like Cursor
"""

from .core import PromptManager
from .templates import BasePromptTemplate, ContextualPromptTemplate
from .builders import PromptBuilder

__all__ = [
    'PromptManager',
    'BasePromptTemplate', 
    'ContextualPromptTemplate',
    'PromptBuilder'
] 