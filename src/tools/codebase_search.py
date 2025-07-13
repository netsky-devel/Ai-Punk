"""
AI Punk Codebase Search Tool
Enhanced text search through codebase (placeholder for future vector search)
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .base import BaseTool

console = Console()

class CodebaseSearchTool(BaseTool):
    """Tool for searching through codebase content"""
    
    def __init__(self):
        super().__init__(
            name="codebase_search",
            description="semantic search that finds code by meaning, not exact text. Use when you need to explore unfamiliar codebases, ask 'how / where / what' questions to understand behavior, find code by meaning rather than exact text."
        )
    
    def execute(self, 
                query: str, 
                target_directories: Optional[List[str]] = None,
                max_results: int = 20) -> Dict[str, Any]:
        """
        Search through codebase content
        
        Args:
            query: Search query describing what to find
            target_directories: List of directories to search in (optional)
            max_results: Maximum number of results to return
            
        Returns:
            Dict with success status, message, and search results
        """
        try:
            # Check workspace
            workspace = self._check_workspace()
            
            # Determine search directories
            search_dirs = []
            if target_directories:
                for dir_path in target_directories:
                    resolved_dir = self._resolve_path(dir_path) if dir_path != "." else workspace
                    if resolved_dir.is_dir():
                        search_dirs.append(resolved_dir)
            else:
                search_dirs = [workspace]
            
            if not search_dirs:
                return self._format_error("Не найдено директорий для поиска")
            
            # Extract search terms from query
            search_terms = self._extract_search_terms(query)
            
            # Search through files
            results = []
            for search_dir in search_dirs:
                dir_results = self._search_directory(search_dir, search_terms, max_results - len(results))
                results.extend(dir_results)
                
                if len(results) >= max_results:
                    break
            
            # Sort results by relevance
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Display results
            self._display_results(results, query)
            
            return self._format_success(
                f"Найдено {len(results)} релевантных результатов",
                {
                    "query": query,
                    "results": results,
                    "search_terms": search_terms,
                    "directories_searched": [str(d) for d in search_dirs]
                }
            )
            
        except Exception as e:
            return self._format_error(f"Ошибка при поиске в кодовой базе: {str(e)}")
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from query"""
        # Simple term extraction - in future this would use NLP
        terms = []
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'how', 'where', 'what', 'when', 'why', 'who'}
        
        # Extract words
        words = re.findall(r'\b\w+\b', query.lower())
        
        for word in words:
            if len(word) > 2 and word not in stop_words:
                terms.append(word)
        
        # Add original query as a phrase
        terms.append(query.lower())
        
        return terms
    
    def _search_directory(self, directory: Path, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search through files in a directory"""
        results = []
        
        for file_path in directory.rglob("*"):
            if len(results) >= max_results:
                break
                
            if file_path.is_file() and self._is_searchable_file(file_path):
                file_results = self._search_file(file_path, search_terms)
                results.extend(file_results)
        
        return results[:max_results]
    
    def _is_searchable_file(self, file_path: Path) -> bool:
        """Check if file should be searched"""
        # Skip binary files and common non-text files
        binary_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.mp3', '.mp4', '.avi', '.mov', '.wav', '.zip', '.tar', '.gz', '.rar', '.7z', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.pyc', '.pyo', '.class', '.jar'}
        
        if file_path.suffix.lower() in binary_extensions:
            return False
        
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            return False
        
        # Skip common non-searchable directories
        skip_dirs = {'__pycache__', 'node_modules', '.git', '.svn', 'venv', '.venv'}
        if any(part in skip_dirs for part in file_path.parts):
            return False
        
        return True
    
    def _search_file(self, file_path: Path, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Search for terms in a single file"""
        results = []
        
        try:
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.splitlines()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='cp1251') as f:
                        content = f.read()
                        lines = content.splitlines()
                except UnicodeDecodeError:
                    return results
            
            # Search for terms
            for line_num, line in enumerate(lines, 1):
                line_lower = line.lower()
                relevance_score = 0
                matched_terms = []
                
                for term in search_terms:
                    if term in line_lower:
                        relevance_score += 1
                        matched_terms.append(term)
                
                if relevance_score > 0:
                    results.append({
                        "file": str(file_path.relative_to(file_path.parents[len(file_path.parents) - 1])),
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "relevance_score": relevance_score,
                        "matched_terms": matched_terms
                    })
        
        except (IOError, PermissionError):
            pass
        
        return results
    
    def _display_results(self, results: List[Dict[str, Any]], query: str):
        """Display search results"""
        if not results:
            console.print(f"🔍 [yellow]Результаты не найдены для запроса: '{query}'[/yellow]")
            console.print("💡 [dim]Попробуйте изменить запрос или использовать другие ключевые слова[/dim]")
            return
        
        console.print(f"🔍 [green]Найдено {len(results)} релевантных результатов для: '{query}'[/green]")
        
        # Group results by file
        files_with_results = {}
        for result in results:
            file_path = result["file"]
            if file_path not in files_with_results:
                files_with_results[file_path] = []
            files_with_results[file_path].append(result)
        
        # Display top results
        shown_files = 0
        for file_path, file_results in files_with_results.items():
            if shown_files >= 5:  # Limit to top 5 files
                break
            
            # Sort file results by relevance
            file_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            console.print(f"\n📄 [bold blue]{file_path}[/bold blue] ({len(file_results)} совпадений)")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Строка", style="cyan", width=6)
            table.add_column("Содержимое", style="white")
            table.add_column("Релевантность", style="green", width=12)
            
            for result in file_results[:5]:  # Top 5 results per file
                table.add_row(
                    str(result["line_number"]),
                    result["line_content"][:100] + "..." if len(result["line_content"]) > 100 else result["line_content"],
                    f"⭐ {result['relevance_score']}"
                )
            
            console.print(table)
            shown_files += 1
        
        if len(files_with_results) > 5:
            console.print(f"[dim]... и еще {len(files_with_results) - 5} файлов с результатами[/dim]")
    
    def get_langchain_tool(self):
        """Get LangChain tool representation"""
        from langchain.tools import Tool
        
        def tool_func(query: str, target_directories: Optional[List[str]] = None):
            return self.run(query=query, target_directories=target_directories)
        
        return Tool(
            name=self.name,
            description=self.description,
            func=tool_func
        )

# Create tool instance
codebase_search_tool = CodebaseSearchTool() 