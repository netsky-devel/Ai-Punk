"""
AI Punk Base Tool
Base class for all tools with workspace awareness and rich output
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pathlib import Path

from ..workspace.manager import WorkspaceManager

console = Console()

class BaseTool(ABC):
    """Base class for all AI Punk tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path within workspace with security checks"""
        try:
            workspace_manager = WorkspaceManager()
            return workspace_manager.resolve_path(path)
        except ValueError as e:
            raise ValueError(f"🚫 Путь недоступен: {e}")
    
    def _check_workspace(self) -> Path:
        """Check if workspace is selected"""
        workspace_manager = WorkspaceManager()
        workspace = workspace_manager.get_current_workspace()
        if not workspace:
            raise ValueError("🚫 Рабочая директория не выбрана")
        return workspace
    
    def _format_success(self, message: str, details: Optional[str] = None) -> Dict[str, Any]:
        """Format successful result"""
        result = {
            "success": True,
            "message": message,
            "tool": self.name
        }
        if details:
            result["details"] = details
        return result
    
    def _format_error(self, error: str, details: Optional[str] = None) -> Dict[str, Any]:
        """Format error result"""
        result = {
            "success": False,
            "error": error,
            "tool": self.name
        }
        if details:
            result["details"] = details
        return result
    
    def _print_action(self, action: str, params: Dict[str, Any]):
        """Print tool action with parameters"""
        console.print(f"🔧 [bold blue]{self.name}[/bold blue]: {action}")
        if params:
            for key, value in params.items():
                console.print(f"   • {key}: [cyan]{value}[/cyan]")
    
    def _print_result(self, result: Dict[str, Any]):
        """Print tool result"""
        if result["success"]:
            console.print(f"✅ [green]{result['message']}[/green]")
            if "details" in result:
                console.print(f"   {result['details']}")
        else:
            console.print(f"❌ [red]{result['error']}[/red]")
            if "details" in result:
                console.print(f"   {result['details']}")
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """Run tool with logging and error handling"""
        try:
            # Print action
            self._print_action("выполняется", kwargs)
            
            # Execute tool
            result = self.execute(**kwargs)
            
            # Print result
            self._print_result(result)
            
            return result
            
        except Exception as e:
            error_result = self._format_error(f"Ошибка выполнения: {str(e)}")
            self._print_result(error_result)
            return error_result

class FileSystemTool(BaseTool):
    """Base class for file system tools"""
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
    
    def _check_file_exists(self, path: Path) -> bool:
        """Check if file exists"""
        return path.exists() and path.is_file()
    
    def _check_dir_exists(self, path: Path) -> bool:
        """Check if directory exists"""
        return path.exists() and path.is_dir()
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB" 