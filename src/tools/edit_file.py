"""
AI Punk Edit File Tool
Creates new files or edits existing ones with backup support
"""

import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm

from .base import FileSystemTool

console = Console()

class EditFileTool(FileSystemTool):
    """Tool for editing files"""
    
    def __init__(self):
        super().__init__(
            name="edit_file",
            description="Use this tool to propose an edit to an existing file or create a new file. This will be read by a less intelligent model, which will quickly apply the edit. You should make it clear what the edit is, while also minimizing the unchanged code you write."
        )
    
    def execute(self, path: str, content: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        Edit or create a file
        
        Args:
            path: File path to edit or create
            content: New file content
            create_backup: Whether to create backup of existing file
            
        Returns:
            Dict with success status, message, and operation details
        """
        try:
            # Check workspace
            self._check_workspace()
            
            # Resolve path
            target_path = self._resolve_path(path)
            
            # Check if file exists
            file_exists = self._check_file_exists(target_path)
            
            # Create backup if file exists and backup is requested
            backup_path = None
            if file_exists and create_backup:
                backup_path = self._create_backup(target_path)
            
            # Ensure parent directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except PermissionError:
                return self._format_error(f"Нет доступа для записи: {target_path}")
            
            # Display the changes
            self._display_changes(target_path, content, file_exists, backup_path)
            
            # Return result
            operation = "обновлен" if file_exists else "создан"
            return self._format_success(
                f"Файл {operation}: {target_path}",
                {
                    "path": str(target_path),
                    "operation": "update" if file_exists else "create",
                    "content": content,
                    "backup_path": str(backup_path) if backup_path else None,
                    "size": len(content.encode('utf-8'))
                }
            )
            
        except Exception as e:
            return self._format_error(f"Ошибка при редактировании файла: {str(e)}")
    
    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """Create backup of existing file"""
        try:
            # Create backup filename with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
            backup_path = file_path.parent / backup_name
            
            # Copy file to backup
            shutil.copy2(file_path, backup_path)
            
            console.print(f"💾 [dim]Создан бэкап: {backup_path.name}[/dim]")
            return backup_path
            
        except Exception as e:
            console.print(f"⚠️  [yellow]Не удалось создать бэкап: {e}[/yellow]")
            return None
    
    def _display_changes(self, path: Path, content: str, file_exists: bool, backup_path: Optional[Path]):
        """Display file changes"""
        # Determine file type for syntax highlighting
        file_extension = path.suffix.lower()
        lexer_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.xml': 'xml',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bat': 'batch',
            '.ps1': 'powershell'
        }
        
        lexer = lexer_map.get(file_extension, 'text')
        
        # Create syntax highlighted content
        syntax = Syntax(
            content,
            lexer,
            line_numbers=True,
            theme="monokai"
        )
        
        # Create panel title
        operation = "📝 Обновлен" if file_exists else "📄 Создан"
        title = f"{operation}: {path.name}"
        if backup_path:
            title += f" (бэкап: {backup_path.name})"
        
        # Display in panel
        console.print(Panel(
            syntax,
            title=title,
            border_style="green"
        ))
        
        # Show file info
        file_size = len(content.encode('utf-8'))
        lines_count = len(content.splitlines())
        console.print(f"📊 [dim]Размер: {self._format_file_size(file_size)} | Строк: {lines_count}[/dim]")
    
    def create_new_file(self, path: str, content: str) -> Dict[str, Any]:
        """Convenience method to create new file"""
        return self.execute(path=path, content=content, create_backup=False)
    
    def update_existing_file(self, path: str, content: str, create_backup: bool = True) -> Dict[str, Any]:
        """Convenience method to update existing file"""
        return self.execute(path=path, content=content, create_backup=create_backup)
    
    def get_langchain_tool(self):
        """Get LangChain tool representation"""
        from langchain.tools import Tool
        
        def tool_func(path: str, content: str, create_backup: bool = True):
            return self.run(path=path, content=content, create_backup=create_backup)
        
        return Tool(
            name=self.name,
            description=self.description,
            func=tool_func
        )

# Create tool instance
edit_file_tool = EditFileTool() 