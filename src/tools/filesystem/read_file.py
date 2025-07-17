"""
File Reading Tool
Reads file contents with offset and limit support
"""

import os
from typing import Dict, Any, Optional

from .security import PathSecurity


class ReadFileTool:
    """Инструмент для чтения файлов"""
    
    def __init__(self, root_directory: str):
        self.security = PathSecurity(root_directory)
    
    def execute(self, file_path: str, offset: Optional[int] = None, 
                limit: Optional[int] = None) -> Dict[str, Any]:
        """Читает файл с поддержкой offset/limit"""
        
        # Валидация пути
        error = self.security.validate_path(file_path)
        if error:
            return {"success": False, "error": error}
        
        resolved_path = self.security.resolve_path(file_path)
        
        if not os.path.exists(resolved_path):
            return {"success": False, "error": f"Файл {file_path} не существует"}
        
        if not os.path.isfile(resolved_path):
            return {"success": False, "error": f"Путь {file_path} не является файлом"}
        
        try:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            
            # Применение offset и limit
            if offset is not None:
                if offset < 0 or offset >= total_lines:
                    return {"success": False, "error": f"Offset {offset} вне диапазона (0-{total_lines-1})"}
                lines = lines[offset:]
            
            if limit is not None:
                if limit <= 0:
                    return {"success": False, "error": "Limit должен быть положительным"}
                lines = lines[:limit]
            
            content = ''.join(lines)
            
            return {
                "success": True,
                "path": self.security.make_relative(resolved_path),
                "content": content,
                "total_lines": total_lines,
                "lines_returned": len(lines),
                "offset": offset or 0
            }
        
        except UnicodeDecodeError:
            return {"success": False, "error": f"Файл {file_path} не является текстовым"}
        except Exception as e:
            return {"success": False, "error": f"Ошибка при чтении файла: {str(e)}"} 