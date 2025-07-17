"""
Legacy Workspace Import
Re-exports from organized workspace package for backward compatibility
"""

from .workspace import (
    WorkspaceManager,
    get_workspace,
    select_workspace,
    get_current_workspace, 
    resolve_workspace_path
)

# Legacy exports for backward compatibility
__all__ = [
    'WorkspaceManager',
    'get_workspace',
    'select_workspace',
    'get_current_workspace',
    'resolve_workspace_path'
] 