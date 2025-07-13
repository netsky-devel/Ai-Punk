"""
AI Punk Read File Tool
Reads file contents with line numbers and range support
"""

from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

from .base import FileSystemTool

console = Console()

class ReadFileTool(FileSystemTool):
    """Tool for reading file contents"""
    
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read the contents of a file. The output of this tool call will be the 1-indexed file contents from start_line_one_indexed to end_line_one_indexed_inclusive, together with a summary of the lines outside start_line_one_indexed and end_line_one_indexed_inclusive."
        )
    
    def execute(self, path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> Dict[str, Any]:
        """
        Read file contents
        
        Args:
            path: File path to read
            start_line: Starting line number (1-indexed, optional)
            end_line: Ending line number (1-indexed, inclusive, optional)
            
        Returns:
            Dict with success status, message, and file contents
        """
        try:
            # Check workspace
            self._check_workspace()
            
            # Resolve path
            target_path = self._resolve_path(path)
            
            # Check if file exists
            if not self._check_file_exists(target_path):
                return self._format_error(f"Файл не найден: {target_path}")
            
            # Check file size
            file_size = target_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return self._format_error(f"Файл слишком большой: {self._format_file_size(file_size)}")
            
            # Read file
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                try:
                    with open(target_path, 'r', encoding='cp1251') as f:
                        lines = f.readlines()
                except UnicodeDecodeError:
                    return self._format_error(f"Не удалось прочитать файл: неподдерживаемая кодировка")
            except PermissionError:
                return self._format_error(f"Нет доступа к файлу: {target_path}")
            
            total_lines = len(lines)
            
            # Handle line range
            if start_line is not None or end_line is not None:
                start_idx = (start_line - 1) if start_line else 0
                end_idx = end_line if end_line else total_lines
                
                # Validate range
                if start_idx < 0 or start_idx >= total_lines:
                    return self._format_error(f"Неверная начальная строка: {start_line}")
                if end_idx <= start_idx or end_idx > total_lines:
                    return self._format_error(f"Неверная конечная строка: {end_line}")
                
                # Get selected lines
                selected_lines = lines[start_idx:end_idx]
                
                # Create summary
                summary = self._create_summary(lines, start_idx, end_idx, total_lines)
                
                # Display content
                self._display_content(target_path, selected_lines, start_line or 1, summary)
                
                return self._format_success(
                    f"Прочитано строк {start_line or 1}-{end_idx} из {total_lines}",
                    {
                        "path": str(target_path),
                        "content": "".join(selected_lines),
                        "lines": selected_lines,
                        "start_line": start_line or 1,
                        "end_line": end_idx,
                        "total_lines": total_lines,
                        "summary": summary
                    }
                )
            else:
                # Read entire file
                content = "".join(lines)
                
                # Display content
                self._display_content(target_path, lines, 1)
                
                return self._format_success(
                    f"Прочитан файл: {total_lines} строк",
                    {
                        "path": str(target_path),
                        "content": content,
                        "lines": lines,
                        "total_lines": total_lines
                    }
                )
                
        except Exception as e:
            return self._format_error(f"Ошибка при чтении файла: {str(e)}")
    
    def _create_summary(self, lines: list, start_idx: int, end_idx: int, total_lines: int) -> str:
        """Create summary of lines outside the selected range"""
        summary_parts = []
        
        if start_idx > 0:
            summary_parts.append(f"Строки 1-{start_idx}: {start_idx} строк до выбранного диапазона")
        
        if end_idx < total_lines:
            remaining = total_lines - end_idx
            summary_parts.append(f"Строки {end_idx + 1}-{total_lines}: {remaining} строк после выбранного диапазона")
        
        return " | ".join(summary_parts) if summary_parts else "Показан весь файл"
    
    def _display_content(self, path: Path, lines: list, start_line: int, summary: Optional[str] = None):
        """Display file content with syntax highlighting"""
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
        content = "".join(lines)
        
        # Create syntax highlighted content
        syntax = Syntax(
            content,
            lexer,
            line_numbers=True,
            start_line=start_line,
            theme="monokai"
        )
        
        # Create panel title
        title = f"📄 {path.name}"
        if summary:
            title += f" | {summary}"
        
        # Display in panel
        console.print(Panel(
            syntax,
            title=title,
            border_style="blue"
        ))
    
    def get_langchain_tool(self):
        """Get LangChain tool representation"""
        from langchain.tools import Tool
        
        def tool_func(path: str, start_line: Optional[int] = None, end_line: Optional[int] = None):
            return self.run(path=path, start_line=start_line, end_line=end_line)
        
        return Tool(
            name=self.name,
            description=self.description,
            func=tool_func
        )

# Create tool instance
read_file_tool = ReadFileTool() 