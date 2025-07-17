"""
File Editing Tool  
Edits files with search and replace functionality
"""

import os
from typing import Dict, Any

from .security import PathSecurity


class EditFileTool:
    """Инструмент для редактирования файлов"""
    
    def __init__(self, root_directory: str):
        self.security = PathSecurity(root_directory)
    
    def execute(self, file_path: str, old_string: str, new_string: str, 
                expected_replacements: int = 1) -> Dict[str, Any]:
        """Редактирует файл с заменой строк"""
        
        # Валидация пути
        error = self.security.validate_path(file_path)
        if error:
            return {"success": False, "error": error}
        
        resolved_path = self.security.resolve_path(file_path)
        
        # Создание файла если не существует и old_string пустой
        if not os.path.exists(resolved_path):
            if old_string == "":
                try:
                    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
                    with open(resolved_path, 'w', encoding='utf-8') as f:
                        f.write(new_string)
                    return {
                        "success": True,
                        "path": self.security.make_relative(resolved_path),
                        "replacements_made": 1,
                        "action": "created"
                    }
                except Exception as e:
                    return {"success": False, "error": f"Ошибка при создании файла: {str(e)}"}
            else:
                return {"success": False, "error": f"Файл {file_path} не существует"}
        
        if not os.path.isfile(resolved_path):
            return {"success": False, "error": f"Путь {file_path} не является файлом"}
        
        try:
            # Чтение файла
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Подсчет вхождений
            count = content.count(old_string)
            
            if count == 0:
                return {"success": False, "error": f"Строка '{old_string}' не найдена в файле"}
            
            if expected_replacements > 0 and count != expected_replacements:
                return {
                    "success": False, 
                    "error": f"Ожидалось {expected_replacements} вхождений, найдено {count}"
                }
            
            # Замена
            new_content = content.replace(old_string, new_string)
            
            # Запись файла
            with open(resolved_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                "success": True,
                "path": self.security.make_relative(resolved_path),
                "replacements_made": count,
                "action": "modified"
            }
        
        except UnicodeDecodeError:
            return {"success": False, "error": f"Файл {file_path} не является текстовым"}
        except Exception as e:
            return {"success": False, "error": f"Ошибка при редактировании файла: {str(e)}"} 