"""
Grep Search Tool
Search for patterns in files using regular expressions
"""

import os
import re
import fnmatch
from typing import Dict, Any, Optional

from .security import PathSecurity, GitIgnoreParser


class GrepTool:
    """Инструмент для поиска в файлах"""
    
    def __init__(self, root_directory: str):
        self.security = PathSecurity(root_directory)
        self.gitignore = GitIgnoreParser(root_directory)
    
    def execute(self, pattern: str, path: str = ".", include: Optional[str] = None, 
                case_sensitive: bool = True) -> Dict[str, Any]:
        """Выполняет поиск по файлам"""
        
        # Валидация пути
        error = self.security.validate_path(path)
        if error:
            return {"success": False, "error": error}
        
        resolved_path = self.security.resolve_path(path)
        
        if not os.path.exists(resolved_path):
            return {"success": False, "error": f"Путь {path} не существует"}
        
        try:
            matches = []
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            if os.path.isfile(resolved_path):
                files_to_search = [resolved_path]
            else:
                files_to_search = []
                for root, dirs, files in os.walk(resolved_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Проверка на игнорирование
                        if self.gitignore.should_ignore(file_path):
                            continue
                        
                        # Фильтр по расширению
                        if include:
                            if not fnmatch.fnmatch(file, include):
                                continue
                        
                        files_to_search.append(file_path)
            
            for file_path in files_to_search:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                matches.append({
                                    "file": self.security.make_relative(file_path),
                                    "line": line_num,
                                    "content": line.rstrip()
                                })
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": matches,
                "total_matches": len(matches),
                "files_searched": len(files_to_search)
            }
        
        except re.error as e:
            return {"success": False, "error": f"Неверный regex паттерн: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Ошибка при поиске: {str(e)}"} 