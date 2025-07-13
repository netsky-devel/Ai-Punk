"""
AI Punk List Directory Tool
Lists the contents of a directory with detailed information
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from rich.table import Table
from rich.console import Console

from .base import FileSystemTool

console = Console()

class ListDirTool(FileSystemTool):
    """Tool for listing directory contents"""
    
    def __init__(self):
        super().__init__(
            name="list_dir",
            description="List the contents of a directory. The quick tool to use for discovery, before using more targeted tools like semantic search or file reading. Useful to try to understand the file structure before diving deeper into specific files. Can be used to explore the codebase."
        )
    
    def execute(self, dir_path: str = ".") -> Dict[str, Any]:
        """
        List directory contents
        
        Args:
            dir_path: Directory path to list (default: current directory)
            
        Returns:
            Dict with success status, message, and file list
        """
        try:
            # Check workspace
            workspace = self._check_workspace()
            
            # Resolve path
            if dir_path == ".":
                target_path = workspace
            else:
                target_path = self._resolve_path(dir_path)
            
            # Check if directory exists
            if not self._check_dir_exists(target_path):
                return self._format_error(f"Директория не найдена: {target_path}")
            
            # Get directory contents
            items = []
            try:
                for item in target_path.iterdir():
                    item_info = self._get_item_info(item)
                    items.append(item_info)
            except PermissionError:
                return self._format_error(f"Нет доступа к директории: {target_path}")
            
            # Sort items: directories first, then files
            items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
            
            # Create table for display
            self._display_items(items, target_path)
            
            # Return result
            return self._format_success(
                f"Найдено {len(items)} элементов в {target_path}",
                {
                    "path": str(target_path),
                    "items": items,
                    "count": len(items)
                }
            )
            
        except Exception as e:
            return self._format_error(f"Ошибка при чтении директории: {str(e)}")
    
    def _get_item_info(self, item: Path) -> Dict[str, Any]:
        """Get information about a file or directory"""
        try:
            stat = item.stat()
            
            if item.is_dir():
                # Count items in directory
                try:
                    item_count = len(list(item.iterdir()))
                    size_display = f"{item_count} элементов"
                except (PermissionError, OSError):
                    size_display = "недоступно"
                
                return {
                    "name": item.name,
                    "type": "directory",
                    "size": 0,
                    "size_display": size_display,
                    "modified": stat.st_mtime,
                    "permissions": oct(stat.st_mode)[-3:]
                }
            else:
                return {
                    "name": item.name,
                    "type": "file",
                    "size": stat.st_size,
                    "size_display": self._format_file_size(stat.st_size),
                    "modified": stat.st_mtime,
                    "permissions": oct(stat.st_mode)[-3:]
                }
                
        except (OSError, PermissionError):
            return {
                "name": item.name,
                "type": "unknown",
                "size": 0,
                "size_display": "недоступно",
                "modified": 0,
                "permissions": "000"
            }
    
    def _display_items(self, items: List[Dict[str, Any]], path: Path):
        """Display items in a formatted table"""
        if not items:
            console.print(f"📁 [yellow]Директория пуста: {path}[/yellow]")
            return
        
        table = Table(title=f"📁 Содержимое: {path}")
        table.add_column("Тип", style="cyan", width=4)
        table.add_column("Имя", style="white", min_width=20)
        table.add_column("Размер", style="green", justify="right")
        table.add_column("Права", style="yellow", justify="center")
        
        for item in items:
            # Type icon
            if item["type"] == "directory":
                type_icon = "📁"
                name_style = "bold blue"
            elif item["type"] == "file":
                type_icon = "📄"
                name_style = "white"
            else:
                type_icon = "❓"
                name_style = "dim"
            
            table.add_row(
                type_icon,
                f"[{name_style}]{item['name']}[/{name_style}]",
                item["size_display"],
                item["permissions"]
            )
        
        console.print(table)
    
    def get_langchain_tool(self):
        """Get LangChain tool representation"""
        from langchain.tools import Tool
        
        return Tool(
            name=self.name,
            description=self.description,
            func=lambda dir_path=".": self.run(dir_path=dir_path)
        )

# Create tool instance
list_dir_tool = ListDirTool() 