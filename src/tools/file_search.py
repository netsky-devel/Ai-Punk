"""
AI Punk File Search Tool
Finds files by name using fuzzy matching
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table

from .base import BaseTool

console = Console()

class FileSearchTool(BaseTool):
    """Tool for searching files by name"""
    
    def __init__(self):
        super().__init__(
            name="file_search",
            description="Fast file search based on fuzzy matching against file path. Use if you know part of the file path but don't know where it's located exactly. Response will be capped to 10 results. Make your query more specific if need to filter results further."
        )
    
    def execute(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for files by name
        
        Args:
            query: Search query (file name or part of path)
            max_results: Maximum number of results to return
            
        Returns:
            Dict with success status, message, and search results
        """
        try:
            # Check workspace
            workspace = self._check_workspace()
            
            # Find all files
            all_files = []
            for file_path in workspace.rglob("*"):
                if file_path.is_file() and self._is_searchable_file(file_path):
                    all_files.append(file_path)
            
            # Search for matches
            matches = self._find_matches(all_files, query, max_results)
            
            # Display results
            self._display_results(matches, query)
            
            return self._format_success(
                f"Найдено {len(matches)} файлов для запроса '{query}'",
                {
                    "query": query,
                    "results": [str(match.relative_to(workspace)) for match in matches],
                    "total_files_searched": len(all_files),
                    "matches_found": len(matches)
                }
            )
            
        except Exception as e:
            return self._format_error(f"Ошибка при поиске файлов: {str(e)}")
    
    def _is_searchable_file(self, file_path: Path) -> bool:
        """Check if file should be included in search"""
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            return False
        
        # Skip common non-searchable directories
        skip_dirs = {'__pycache__', 'node_modules', '.git', '.svn', 'venv', '.venv'}
        if any(part in skip_dirs for part in file_path.parts):
            return False
        
        # Skip backup files
        if file_path.name.endswith('.backup') or '.backup_' in file_path.name:
            return False
        
        return True
    
    def _find_matches(self, files: List[Path], query: str, max_results: int) -> List[Path]:
        """Find files matching the query"""
        query_lower = query.lower()
        matches = []
        
        # Score each file
        scored_files = []
        for file_path in files:
            score = self._calculate_match_score(file_path, query_lower)
            if score > 0:
                scored_files.append((file_path, score))
        
        # Sort by score (highest first)
        scored_files.sort(key=lambda x: x[1], reverse=True)
        
        # Return top matches
        return [file_path for file_path, score in scored_files[:max_results]]
    
    def _calculate_match_score(self, file_path: Path, query: str) -> int:
        """Calculate match score for a file"""
        file_name = file_path.name.lower()
        file_path_str = str(file_path).lower()
        
        score = 0
        
        # Exact filename match (highest score)
        if file_name == query:
            score += 1000
        
        # Filename starts with query
        elif file_name.startswith(query):
            score += 500
        
        # Filename contains query
        elif query in file_name:
            score += 200
        
        # Path contains query
        elif query in file_path_str:
            score += 100
        
        # Fuzzy match (characters in order)
        elif self._fuzzy_match(file_name, query):
            score += 50
        
        # Boost score for common file types
        if file_path.suffix.lower() in {'.py', '.js', '.ts', '.html', '.css', '.md', '.txt', '.json'}:
            score += 10
        
        return score
    
    def _fuzzy_match(self, text: str, query: str) -> bool:
        """Check if query characters appear in order in text"""
        query_idx = 0
        for char in text:
            if query_idx < len(query) and char == query[query_idx]:
                query_idx += 1
                if query_idx == len(query):
                    return True
        return query_idx == len(query)
    
    def _display_results(self, matches: List[Path], query: str):
        """Display search results"""
        if not matches:
            console.print(f"🔍 [yellow]Файлы не найдены для запроса '{query}'[/yellow]")
            return
        
        console.print(f"🔍 [green]Найдено {len(matches)} файлов для запроса '{query}'[/green]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("№", style="cyan", width=3)
        table.add_column("Файл", style="white")
        table.add_column("Размер", style="green", justify="right")
        table.add_column("Тип", style="yellow")
        
        for i, file_path in enumerate(matches, 1):
            try:
                file_size = file_path.stat().st_size
                file_type = file_path.suffix.upper() if file_path.suffix else "FILE"
                
                table.add_row(
                    str(i),
                    str(file_path.relative_to(file_path.parents[len(file_path.parents) - 1])),
                    self._format_file_size(file_size),
                    file_type
                )
            except (OSError, ValueError):
                table.add_row(
                    str(i),
                    str(file_path),
                    "?",
                    "?"
                )
        
        console.print(table)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_langchain_tool(self):
        """Get LangChain tool representation"""
        from langchain.tools import Tool
        
        def tool_func(query: str, max_results: int = 10):
            return self.run(query=query, max_results=max_results)
        
        return Tool(
            name=self.name,
            description=self.description,
            func=tool_func
        )

# Create tool instance
file_search_tool = FileSearchTool() 