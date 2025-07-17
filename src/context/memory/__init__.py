"""
Memory management for Smart Context Manager
Session state, project knowledge, and pattern storage
"""

from .session import SessionMemory
from .vectors import VectorMemory
from .patterns import PatternMemory

__all__ = ['SessionMemory', 'VectorMemory', 'PatternMemory'] 