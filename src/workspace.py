"""
AI Punk Workspace Manager
Handles user-selected project directories and provides safe file operations
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from .config import get_config, set_workspace

class WorkspaceManager:
    """Manages the current workspace directory where the agent operates"""
    
    def __init__(self):
        self.current_path: Optional[Path] = None
        self._load_workspace()
    
    def _load_workspace(self):
        """Load workspace from config"""
        config = get_config()
        if config.workspace_path:
            self.current_path = Path(config.workspace_path)
    
    def select_workspace(self, path: str) -> bool:
        """Select a new workspace directory"""
        try:
            workspace_path = Path(path).resolve()
            
            if not workspace_path.exists():
                print(f"❌ Путь не существует: {workspace_path}")
                return False
                
            if not workspace_path.is_dir():
                print(f"❌ Путь не является директорией: {workspace_path}")
                return False
                
            self.current_path = workspace_path
            set_workspace(str(workspace_path))
            print(f"✅ Рабочая директория установлена: {workspace_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при выборе рабочей директории: {e}")
            return False
    
    def get_current_workspace(self) -> Optional[Path]:
        """Get current workspace path"""
        return self.current_path
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """Get information about current workspace"""
        if not self.current_path:
            return {"status": "no_workspace", "message": "Рабочая директория не выбрана"}
        
        try:
            files = list(self.current_path.iterdir())
            return {
                "status": "active",
                "path": str(self.current_path),
                "exists": self.current_path.exists(),
                "is_dir": self.current_path.is_dir(),
                "files_count": len([f for f in files if f.is_file()]),
                "dirs_count": len([f for f in files if f.is_dir()]),
                "total_size": self._get_directory_size(self.current_path)
            }
        except Exception as e:
            return {
                "status": "error",
                "path": str(self.current_path),
                "error": str(e)
            }
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory"""
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except:
            pass
        return total
    
    def resolve_path(self, relative_path: str) -> Path:
        """Resolve relative path within workspace"""
        if not self.current_path:
            raise ValueError("Рабочая директория не выбрана")
        
        target_path = (self.current_path / relative_path).resolve()
        
        # Security check: ensure path is within workspace
        try:
            target_path.relative_to(self.current_path)
        except ValueError:
            raise ValueError(f"Путь выходит за пределы рабочей директории: {relative_path}")
        
        return target_path
    
    def is_path_safe(self, path: str) -> bool:
        """Check if path is safe to access within workspace"""
        try:
            self.resolve_path(path)
            return True
        except ValueError:
            return False
    
    def change_directory(self, path: str = ".") -> bool:
        """Change current working directory within workspace"""
        try:
            if path == ".":
                target = self.current_path
            else:
                target = self.resolve_path(path)
            
            if not target.exists():
                print(f"❌ Директория не существует: {target}")
                return False
                
            if not target.is_dir():
                print(f"❌ Путь не является директорией: {target}")
                return False
            
            os.chdir(target)
            print(f"📁 Перешли в директорию: {target}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при смене директории: {e}")
            return False
    
    def list_recent_workspaces(self) -> List[str]:
        """List recently used workspaces"""
        # TODO: Implement history of workspaces
        return []

# Global workspace instance
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