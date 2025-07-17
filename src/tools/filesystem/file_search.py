"""
File Search Tool
Finds files by name using fuzzy matching
"""

import os
import fnmatch
from typing import Dict, Any, List, Optional

from .security import PathSecurity, GitIgnoreParser


class FileSearchTool:
    """Инструмент для поиска файлов по имени"""
    
    def __init__(self, root_directory: str):
        self.security = PathSecurity(root_directory)
        self.gitignore = GitIgnoreParser(root_directory)
    
    def execute(self, query: str, path: str = ".", max_results: int = 10) -> Dict[str, Any]:
        """Поиск файлов по имени/пути"""
        
        # Валидация пути
        error = self.security.validate_path(path)
        if error:
            return {"success": False, "error": error}
        
        resolved_path = self.security.resolve_path(path)
        
        if not os.path.exists(resolved_path):
            return {"success": False, "error": f"Путь {path} не существует"}
        
        try:
            # Находим все файлы
            all_files = []
            for root, dirs, files in os.walk(resolved_path):
                # Фильтруем по gitignore
                dirs[:] = [d for d in dirs if not self.gitignore.is_ignored(os.path.join(root, d))]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if not self.gitignore.is_ignored(file_path) and self._is_searchable_file(file_path):
                        all_files.append(file_path)
            
            # Поиск совпадений
            matches = self._find_matches(all_files, query, max_results)
            
            return {
                "success": True,
                "files": matches,
                "total_searched": len(all_files),
                "query": query
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ошибка поиска: {str(e)}"}
    
    def _is_searchable_file(self, file_path: str) -> bool:
        """Проверяет стоит ли включать файл в поиск"""
        file_name = os.path.basename(file_path)
        
        # Пропускаем скрытые файлы
        if file_name.startswith('.'):
            return False
        
        # Пропускаем backup файлы
        if file_name.endswith('.backup') or '.backup_' in file_name:
            return False
        
        # Пропускаем бинарные файлы
        binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wav',
            '.zip', '.tar', '.gz', '.rar', '.7z',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.pyc', '.pyo', '.class', '.jar'
        }
        
        _, ext = os.path.splitext(file_name.lower())
        if ext in binary_extensions:
            return False
        
        return True
    
    def _find_matches(self, files: List[str], query: str, max_results: int) -> List[Dict[str, Any]]:
        """Находит файлы соответствующие запросу"""
        matches = []
        query_lower = query.lower()
        
        # Точные совпадения имени файла
        for file_path in files:
            file_name = os.path.basename(file_path)
            if query_lower == file_name.lower():
                matches.append({
                    "path": file_path,
                    "name": file_name,
                    "score": 100,
                    "match_type": "exact_name"
                })
        
        # Частичные совпадения имени файла
        for file_path in files:
            if len(matches) >= max_results:
                break
            file_name = os.path.basename(file_path)
            if query_lower in file_name.lower() and not any(m["path"] == file_path for m in matches):
                matches.append({
                    "path": file_path,
                    "name": file_name,
                    "score": 80,
                    "match_type": "partial_name"
                })
        
        # Совпадения в пути
        for file_path in files:
            if len(matches) >= max_results:
                break
            if query_lower in file_path.lower() and not any(m["path"] == file_path for m in matches):
                matches.append({
                    "path": file_path,
                    "name": os.path.basename(file_path),
                    "score": 60,
                    "match_type": "path_match"
                })
        
        # Wildcard поиск
        for file_path in files:
            if len(matches) >= max_results:
                break
            file_name = os.path.basename(file_path)
            if fnmatch.fnmatch(file_name.lower(), f"*{query_lower}*") and not any(m["path"] == file_path for m in matches):
                matches.append({
                    "path": file_path,
                    "name": file_name,
                    "score": 40,
                    "match_type": "wildcard"
                })
        
        # Сортируем по релевантности
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:max_results] 