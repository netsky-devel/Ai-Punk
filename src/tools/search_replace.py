"""
AI Punk Search and Replace Tool
Performs search and replace operations in files
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .base import FileSystemTool

console = Console()

class SearchReplaceTool(FileSystemTool):
    """Tool for search and replace operations in files"""
    
    def __init__(self):
        super().__init__(
            name="search_replace",
            description="Use this tool to propose a search and replace operation on an existing file. The tool will replace ONE occurrence of old_string with new_string in the specified file."
        )
    
    def execute(self, 
                file_path: str, 
                old_string: str, 
                new_string: str, 
                create_backup: bool = True) -> Dict[str, Any]:
        """
        Perform search and replace operation
        
        Args:
            file_path: Path to the file to modify
            old_string: String to search for
            new_string: String to replace with
            create_backup: Whether to create backup before modification
            
        Returns:
            Dict with success status, message, and operation details
        """
        try:
            # Check workspace
            self._check_workspace()
            
            # Resolve path
            target_path = self._resolve_path(file_path)
            
            # Check if file exists
            if not self._check_file_exists(target_path):
                return self._format_error(f"Файл не найден: {target_path}")
            
            # Read file content
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(target_path, 'r', encoding='cp1251') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    return self._format_error("Не удалось прочитать файл: неподдерживаемая кодировка")
            except PermissionError:
                return self._format_error(f"Нет доступа к файлу: {target_path}")
            
            # Check if old_string exists
            if old_string not in content:
                return self._format_error(f"Строка для замены не найдена: '{old_string}'")
            
            # Count occurrences
            occurrence_count = content.count(old_string)
            
            # Show what will be replaced
            self._show_replacement_preview(target_path, old_string, new_string, occurrence_count)
            
            # Create backup if requested
            backup_path = None
            if create_backup:
                backup_path = self._create_backup(target_path)
            
            # Perform replacement (only first occurrence)
            new_content = content.replace(old_string, new_string, 1)
            
            # Write modified content
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            except PermissionError:
                return self._format_error(f"Нет прав для записи в файл: {target_path}")
            
            # Show result
            self._show_replacement_result(target_path, old_string, new_string, backup_path)
            
            return self._format_success(
                f"Замена выполнена в файле: {target_path.name}",
                {
                    "file_path": str(target_path),
                    "old_string": old_string,
                    "new_string": new_string,
                    "total_occurrences": occurrence_count,
                    "replaced_count": 1,
                    "backup_path": str(backup_path) if backup_path else None
                }
            )
            
        except Exception as e:
            return self._format_error(f"Ошибка при выполнении замены: {str(e)}")
    
    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """Create backup of file before modification"""
        try:
            import shutil
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
            backup_path = file_path.parent / backup_name
            
            shutil.copy2(file_path, backup_path)
            console.print(f"💾 [dim]Создан бэкап: {backup_path.name}[/dim]")
            return backup_path
            
        except Exception as e:
            console.print(f"⚠️  [yellow]Не удалось создать бэкап: {e}[/yellow]")
            return None
    
    def _show_replacement_preview(self, file_path: Path, old_string: str, new_string: str, count: int):
        """Show preview of what will be replaced"""
        console.print(f"🔄 [blue]Замена в файле: {file_path.name}[/blue]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="white")
        
        table.add_row("Найдено вхождений", str(count))
        table.add_row("Будет заменено", "1 (первое вхождение)")
        table.add_row("Исходный текст", f"'{old_string}'")
        table.add_row("Новый текст", f"'{new_string}'")
        
        console.print(table)
    
    def _show_replacement_result(self, file_path: Path, old_string: str, new_string: str, backup_path: Optional[Path]):
        """Show result of replacement operation"""
        console.print(f"✅ [green]Замена выполнена успешно[/green]")
        
        if backup_path:
            console.print(f"💾 [dim]Бэкап сохранен: {backup_path.name}[/dim]")
        
        # Show change summary
        console.print(Panel(
            f"[red]- {old_string}[/red]\n[green]+ {new_string}[/green]",
            title="Изменения",
            border_style="blue"
        ))
    
    def replace_all(self, file_path: str, old_string: str, new_string: str, create_backup: bool = True) -> Dict[str, Any]:
        """Replace all occurrences of old_string with new_string"""
        try:
            # Check workspace
            self._check_workspace()
            
            # Resolve path
            target_path = self._resolve_path(file_path)
            
            # Check if file exists
            if not self._check_file_exists(target_path):
                return self._format_error(f"Файл не найден: {target_path}")
            
            # Read file content
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(target_path, 'r', encoding='cp1251') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    return self._format_error("Не удалось прочитать файл: неподдерживаемая кодировка")
            
            # Count occurrences
            occurrence_count = content.count(old_string)
            
            if occurrence_count == 0:
                return self._format_error(f"Строка для замены не найдена: '{old_string}'")
            
            # Create backup if requested
            backup_path = None
            if create_backup:
                backup_path = self._create_backup(target_path)
            
            # Perform replacement (all occurrences)
            new_content = content.replace(old_string, new_string)
            
            # Write modified content
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            console.print(f"✅ [green]Заменено {occurrence_count} вхождений в файле: {target_path.name}[/green]")
            
            return self._format_success(
                f"Заменено {occurrence_count} вхождений в файле: {target_path.name}",
                {
                    "file_path": str(target_path),
                    "old_string": old_string,
                    "new_string": new_string,
                    "replaced_count": occurrence_count,
                    "backup_path": str(backup_path) if backup_path else None
                }
            )
            
        except Exception as e:
            return self._format_error(f"Ошибка при выполнении замены: {str(e)}")
    
    def get_langchain_tool(self):
        """Get LangChain tool representation"""
        from langchain.tools import Tool
        
        def tool_func(file_path: str, old_string: str, new_string: str, create_backup: bool = True):
            return self.run(file_path=file_path, old_string=old_string, new_string=new_string, create_backup=create_backup)
        
        return Tool(
            name=self.name,
            description=self.description,
            func=tool_func
        )

# Create tool instance
search_replace_tool = SearchReplaceTool() 