"""
AI Punk Workspace Management
Secure workspace handling for file operations
"""

from pathlib import Path
from typing import Optional

from .manager import WorkspaceManager

# Export main components
__all__ = [
    'WorkspaceManager',
    'get_workspace',
    'select_workspace', 
    'get_current_workspace',
    'resolve_workspace_path'
]

# Global workspace manager instance
_workspace_manager = WorkspaceManager()


def get_workspace() -> WorkspaceManager:
    """Get global workspace manager"""
    return _workspace_manager


def select_workspace(path: str) -> bool:
    """Select workspace directory"""
    return _workspace_manager.select_workspace(path)


def get_current_workspace() -> Optional[Path]:
    """Get current workspace path"""
    return _workspace_manager.get_current_workspace()


def resolve_workspace_path(relative_path: str) -> Path:
    """Resolve path within current workspace"""
    return _workspace_manager.resolve_path(relative_path) 