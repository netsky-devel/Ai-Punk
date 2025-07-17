"""
Directory Listing Tool
Lists directory contents with security and .gitignore support
"""

import os
import fnmatch
from typing import Dict, Any, List, Optional

from .models import FileEntry
from .security import PathSecurity, GitIgnoreParser


class ListDirTool:
    """Инструмент для списка файлов"""
    
    def __init__(self, root_directory: str):
        self.security = PathSecurity(root_directory)
        self.gitignore = GitIgnoreParser(root_directory)
    
    def execute(self, path: str = ".", ignore_patterns: Optional[List[str]] = None, 
                respect_gitignore: bool = True) -> Dict[str, Any]:
        """Выполняет листинг директории"""
        
        # Валидация пути
        error = self.security.validate_path(path)
        if error:
            return {"success": False, "error": error}
        
        resolved_path = self.security.resolve_path(path)
        
        if not os.path.exists(resolved_path):
            return {"success": False, "error": f"Путь {path} не существует"}
        
        if not os.path.isdir(resolved_path):
            return {"success": False, "error": f"Путь {path} не является директорией"}
        
        try:
            entries = []
            for item in os.listdir(resolved_path):
                item_path = os.path.join(resolved_path, item)
                
                # Проверка на игнорирование
                if respect_gitignore and self.gitignore.should_ignore(item_path):
                    continue
                
                if ignore_patterns:
                    should_skip = False
                    for pattern in ignore_patterns:
                        if fnmatch.fnmatch(item, pattern):
                            should_skip = True
                            break
                    if should_skip:
                        continue
                
                # Получение информации о файле
                try:
                    stat = os.stat(item_path)
                    entry = FileEntry(
                        name=item,
                        path=self.security.make_relative(item_path),
                        is_directory=os.path.isdir(item_path),
                        size=stat.st_size if not os.path.isdir(item_path) else 0,
                        modified_time=str(stat.st_mtime)
                    )
                    entries.append(entry.__dict__)
                except Exception as e:
                    continue
            
            return {
                "success": True,
                "path": self.security.make_relative(resolved_path),
                "entries": entries,
                "total": len(entries)
            }
        
        except Exception as e:
            return {"success": False, "error": f"Ошибка при чтении директории: {str(e)}"} 