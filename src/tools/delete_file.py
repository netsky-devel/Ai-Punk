"""
AI Punk Delete File Tool
Safely deletes files with confirmation and backup options
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Confirm

from .base import FileSystemTool

console = Console()

class DeleteFileTool(FileSystemTool):
    """Tool for deleting files safely"""
    
    def __init__(self):
        super().__init__(
            name="delete_file",
            description="Deletes a file at the specified path. The operation will fail gracefully if the file doesn't exist, the operation is rejected for security reasons, or the file cannot be deleted."
        )
    
    def execute(self, path: str, create_backup: bool = False, force: bool = False) -> Dict[str, Any]:
        """
        Delete a file
        
        Args:
            path: File path to delete
            create_backup: Whether to create backup before deletion
            force: Skip confirmation prompt
            
        Returns:
            Dict with success status, message, and operation details
        """
        try:
            # Check workspace
            self._check_workspace()
            
            # Resolve path
            target_path = self._resolve_path(path)
            
            # Check if file exists
            if not target_path.exists():
                return self._format_error(f"Файл не найден: {target_path}")
            
            # Check if it's a file (not directory)
            if not target_path.is_file():
                return self._format_error(f"Путь не является файлом: {target_path}")
            
            # Get file info before deletion
            file_size = target_path.stat().st_size
            file_info = f"{target_path.name} ({self._format_file_size(file_size)})"
            
            # Show file info
            console.print(f"🗑️  [yellow]Удаление файла: {file_info}[/yellow]")
            
            # Confirmation (unless forced)
            if not force:
                if not Confirm.ask(f"Вы уверены, что хотите удалить {target_path.name}?"):
                    return self._format_error("Операция отменена пользователем")
            
            # Create backup if requested
            backup_path = None
            if create_backup:
                backup_path = self._create_backup(target_path)
                if not backup_path:
                    console.print("⚠️  [yellow]Продолжаем без создания бэкапа[/yellow]")
            
            # Delete file
            try:
                target_path.unlink()
            except PermissionError:
                return self._format_error(f"Нет прав для удаления файла: {target_path}")
            except OSError as e:
                return self._format_error(f"Ошибка при удалении файла: {e}")
            
            # Success message
            console.print(f"✅ [green]Файл удален: {file_info}[/green]")
            if backup_path:
                console.print(f"💾 [dim]Бэкап сохранен: {backup_path.name}[/dim]")
            
            return self._format_success(
                f"Файл удален: {target_path.name}",
                {
                    "path": str(target_path),
                    "size": file_size,
                    "backup_path": str(backup_path) if backup_path else None
                }
            )
            
        except Exception as e:
            return self._format_error(f"Ошибка при удалении файла: {str(e)}")
    
    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """Create backup of file before deletion"""
        try:
            # Create backup filename with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}.deleted_{timestamp}{file_path.suffix}"
            backup_path = file_path.parent / backup_name
            
            # Copy file to backup
            shutil.copy2(file_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            console.print(f"⚠️  [yellow]Не удалось создать бэкап: {e}[/yellow]")
            return None
    
    def delete_with_backup(self, path: str, force: bool = False) -> Dict[str, Any]:
        """Convenience method to delete file with backup"""
        return self.execute(path=path, create_backup=True, force=force)
    
    def delete_force(self, path: str) -> Dict[str, Any]:
        """Convenience method to delete file without confirmation"""
        return self.execute(path=path, create_backup=False, force=True)
    
    def get_langchain_tool(self):
        """Get LangChain tool representation"""
        from langchain.tools import Tool
        
        def tool_func(path: str, create_backup: bool = False, force: bool = False):
            return self.run(path=path, create_backup=create_backup, force=force)
        
        return Tool(
            name=self.name,
            description=self.description,
            func=tool_func
        )

# Create tool instance
delete_file_tool = DeleteFileTool() 