"""
Advanced Prompts System for AI Punk Agent
Inspired by professional AI coding assistants like Cursor
"""

from .core import PromptManager, PromptBuilder
from .templates import BasePromptTemplate, ContextualPromptTemplate

__all__ = [
    'PromptManager',
    'PromptBuilder',
    'BasePromptTemplate', 
    'ContextualPromptTemplate'
] 