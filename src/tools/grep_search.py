"""
AI Punk Grep Search Tool
Searches for patterns in files using regular expressions
"""

import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from .base import BaseTool

console = Console()

class GrepSearchTool(BaseTool):
    """Tool for searching patterns in files"""
    
    def __init__(self):
        super().__init__(
            name="grep_search",
            description="This is best for finding exact text matches or regex patterns. This is preferred over semantic search when we know the exact symbol/function name/etc. to search in some set of directories/file types."
        )
    
    def execute(self, 
                pattern: str, 
                include_pattern: Optional[str] = None,
                exclude_pattern: Optional[str] = None,
                case_sensitive: bool = False,
                max_results: int = 50) -> Dict[str, Any]:
        """
        Search for pattern in files
        
        Args:
            pattern: Regex pattern to search for
            include_pattern: Glob pattern for files to include (e.g. '*.py')
            exclude_pattern: Glob pattern for files to exclude
            case_sensitive: Whether search should be case sensitive
            max_results: Maximum number of results to return
            
        Returns:
            Dict with success status, message, and search results
        """
        try:
            # Check workspace
            workspace = self._check_workspace()
            
            # Compile regex pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return self._format_error(f"Неверное регулярное выражение: {e}")
            
            # Find files to search
            files_to_search = self._find_files(workspace, include_pattern, exclude_pattern)
            
            if not files_to_search:
                return self._format_error("Не найдено файлов для поиска")
            
            # Search in files
            results = []
            for file_path in files_to_search:
                if len(results) >= max_results:
                    break
                    
                file_results = self._search_in_file(file_path, regex, max_results - len(results))
                results.extend(file_results)
            
            # Display results
            self._display_results(results, pattern, len(files_to_search))
            
            return self._format_success(
                f"Найдено {len(results)} совпадений в {len(files_to_search)} файлах",
                {
                    "pattern": pattern,
                    "results": results,
                    "files_searched": len(files_to_search),
                    "matches_found": len(results),
                    "case_sensitive": case_sensitive
                }
            )
            
        except Exception as e:
            return self._format_error(f"Ошибка при поиске: {str(e)}")
    
    def _find_files(self, workspace: Path, include_pattern: Optional[str], exclude_pattern: Optional[str]) -> List[Path]:
        """Find files matching the criteria"""
        files = []
        
        # Default include pattern
        if include_pattern is None:
            include_pattern = "*"
        
        # Find files recursively
        for file_path in workspace.rglob(include_pattern):
            if file_path.is_file():
                # Check exclude pattern
                if exclude_pattern and file_path.match(exclude_pattern):
                    continue
                
                # Skip binary files and common non-text files
                if self._is_text_file(file_path):
                    files.append(file_path)
        
        return files
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file"""
        # Skip common binary extensions
        binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wav',
            '.zip', '.tar', '.gz', '.rar', '.7z',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.pyc', '.pyo', '.class', '.jar'
        }
        
        if file_path.suffix.lower() in binary_extensions:
            return False
        
        # Skip hidden files and directories
        if file_path.name.startswith('.'):
            return False
        
        # Skip common non-text directories
        skip_dirs = {'.git', '.svn', '__pycache__', 'node_modules', '.venv', 'venv'}
        if any(part in skip_dirs for part in file_path.parts):
            return False
        
        return True
    
    def _search_in_file(self, file_path: Path, regex: re.Pattern, max_results: int) -> List[Dict[str, Any]]:
        """Search for pattern in a single file"""
        results = []
        
        try:
            # Try to read file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='cp1251') as f:
                        lines = f.readlines()
                except UnicodeDecodeError:
                    return results  # Skip files with encoding issues
            
            # Search in each line
            for line_num, line in enumerate(lines, 1):
                if len(results) >= max_results:
                    break
                
                matches = regex.finditer(line)
                for match in matches:
                    if len(results) >= max_results:
                        break
                    
                    results.append({
                        "file": str(file_path.relative_to(file_path.parents[len(file_path.parents) - 1])),
                        "line_number": line_num,
                        "line_content": line.rstrip(),
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end()
                    })
            
        except (IOError, PermissionError):
            pass  # Skip files we can't read
        
        return results
    
    def _display_results(self, results: List[Dict[str, Any]], pattern: str, files_searched: int):
        """Display search results in formatted table"""
        if not results:
            console.print(f"🔍 [yellow]Паттерн '{pattern}' не найден в {files_searched} файлах[/yellow]")
            return
        
        # Group results by file
        files_with_matches = {}
        for result in results:
            file_path = result["file"]
            if file_path not in files_with_matches:
                files_with_matches[file_path] = []
            files_with_matches[file_path].append(result)
        
        console.print(f"🔍 [green]Найдено {len(results)} совпадений паттерна '{pattern}' в {len(files_with_matches)} файлах[/green]")
        
        # Display results grouped by file
        for file_path, file_results in files_with_matches.items():
            console.print(f"\n📄 [bold blue]{file_path}[/bold blue] ({len(file_results)} совпадений)")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Строка", style="cyan", width=6)
            table.add_column("Содержимое", style="white")
            
            for result in file_results[:10]:  # Limit to 10 results per file
                line_content = result["line_content"]
                match_text = result["match"]
                
                # Highlight match in line
                highlighted_line = line_content.replace(
                    match_text, 
                    f"[bold red]{match_text}[/bold red]"
                )
                
                table.add_row(
                    str(result["line_number"]),
                    highlighted_line
                )
            
            console.print(table)
            
            if len(file_results) > 10:
                console.print(f"[dim]... и еще {len(file_results) - 10} совпадений[/dim]")
    
    def search_python_files(self, pattern: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """Convenience method to search only in Python files"""
        return self.execute(pattern=pattern, include_pattern="*.py", case_sensitive=case_sensitive)
    
    def search_text_files(self, pattern: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """Convenience method to search in common text files"""
        return self.execute(pattern=pattern, include_pattern="*.{txt,md,py,js,ts,html,css,json}", case_sensitive=case_sensitive)
    
    def get_langchain_tool(self):
        """Get LangChain tool representation"""
        from langchain.tools import Tool
        
        def tool_func(pattern: str, 
                     include_pattern: Optional[str] = None,
                     exclude_pattern: Optional[str] = None,
                     case_sensitive: bool = False):
            return self.run(pattern=pattern, 
                          include_pattern=include_pattern,
                          exclude_pattern=exclude_pattern,
                          case_sensitive=case_sensitive)
        
        return Tool(
            name=self.name,
            description=self.description,
            func=tool_func
        )

# Create tool instance
grep_search_tool = GrepSearchTool() 