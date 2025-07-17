"""
Delete File Tool
Safely deletes files with backup options
"""

import os
import shutil
from typing import Dict, Any, Optional

from .security import PathSecurity


class DeleteFileTool:
    """Инструмент для безопасного удаления файлов"""
    
    def __init__(self, root_directory: str):
        self.security = PathSecurity(root_directory)
    
    def execute(self, path: str, create_backup: bool = True) -> Dict[str, Any]:
        """Удаляет файл с опциональным созданием резервной копии"""
        
        # Валидация пути
        error = self.security.validate_path(path)
        if error:
            return {"success": False, "error": error}
        
        resolved_path = self.security.resolve_path(path)
        
        # Проверяем что файл существует
        if not os.path.exists(resolved_path):
            return {"success": False, "error": f"Файл не найден: {path}"}
        
        # Проверяем что это файл, а не директория
        if not os.path.isfile(resolved_path):
            return {"success": False, "error": f"Указанный путь не является файлом: {path}"}
        
        try:
            backup_path = None
            
            # Создаем резервную копию если нужно
            if create_backup:
                backup_path = self._create_backup(resolved_path)
                if not backup_path:
                    return {"success": False, "error": "Не удалось создать резервную копию"}
            
            # Получаем информацию о файле
            file_size = os.path.getsize(resolved_path)
            
            # Удаляем файл
            os.remove(resolved_path)
            
            return {
                "success": True,
                "message": f"Файл успешно удален: {path}",
                "file_path": resolved_path,
                "file_size": file_size,
                "backup_path": backup_path
            }
            
        except PermissionError:
            return {"success": False, "error": f"Нет прав для удаления файла: {path}"}
        except OSError as e:
            return {"success": False, "error": f"Ошибка при удалении файла: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Неожиданная ошибка: {str(e)}"}
    
    def _create_backup(self, file_path: str) -> Optional[str]:
        """Создает резервную копию файла"""
        try:
            # Генерируем имя для backup
            backup_path = f"{file_path}.backup"
            counter = 1
            
            # Ищем свободное имя
            while os.path.exists(backup_path):
                backup_path = f"{file_path}.backup_{counter}"
                counter += 1
            
            # Копируем файл
            shutil.copy2(file_path, backup_path)
            return backup_path
            
        except Exception:
            return None
    
    def list_backups(self, path: str = ".") -> Dict[str, Any]:
        """Показывает список backup файлов в директории"""
        
        error = self.security.validate_path(path)
        if error:
            return {"success": False, "error": error}
        
        resolved_path = self.security.resolve_path(path)
        
        if not os.path.exists(resolved_path):
            return {"success": False, "error": f"Путь не существует: {path}"}
        
        if not os.path.isdir(resolved_path):
            return {"success": False, "error": f"Указанный путь не является директорией: {path}"}
        
        try:
            backups = []
            for file_name in os.listdir(resolved_path):
                if '.backup' in file_name:
                    file_path = os.path.join(resolved_path, file_name)
                    if os.path.isfile(file_path):
                        backups.append({
                            "name": file_name,
                            "path": file_path,
                            "size": os.path.getsize(file_path),
                            "modified": os.path.getmtime(file_path)
                        })
            
            return {
                "success": True,
                "backups": backups,
                "count": len(backups)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ошибка при поиске backup файлов: {str(e)}"}
    
    def restore_backup(self, backup_path: str, target_path: str) -> Dict[str, Any]:
        """Восстанавливает файл из резервной копии"""
        
        # Валидация путей
        error = self.security.validate_path(backup_path)
        if error:
            return {"success": False, "error": f"Неверный backup путь: {error}"}
        
        error = self.security.validate_path(target_path)
        if error:
            return {"success": False, "error": f"Неверный целевой путь: {error}"}
        
        resolved_backup = self.security.resolve_path(backup_path)
        resolved_target = self.security.resolve_path(target_path)
        
        if not os.path.exists(resolved_backup):
            return {"success": False, "error": f"Backup файл не найден: {backup_path}"}
        
        try:
            shutil.copy2(resolved_backup, resolved_target)
            
            return {
                "success": True,
                "message": f"Файл восстановлен из резервной копии",
                "backup_path": resolved_backup,
                "target_path": resolved_target
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ошибка при восстановлении: {str(e)}"} 