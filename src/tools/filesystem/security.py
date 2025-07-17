"""
Filesystem Security Utilities
Safe path operations and .gitignore handling
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional


class PathSecurity:
    """Утилиты для безопасной работы с путями"""
    
    def __init__(self, root_directory: str):
        self.root_directory = os.path.abspath(root_directory)
    
    def is_within_root(self, path: str) -> bool:
        """Проверяет, находится ли путь внутри корневой директории"""
        abs_path = os.path.abspath(path)
        return abs_path.startswith(self.root_directory)
    
    def make_relative(self, path: str) -> str:
        """Преобразует абсолютный путь в относительный"""
        abs_path = os.path.abspath(path)
        try:
            return os.path.relpath(abs_path, self.root_directory)
        except ValueError:
            return abs_path
    
    def resolve_path(self, path: str) -> str:
        """Разрешает путь относительно корневой директории"""
        if os.path.isabs(path):
            return path
        return os.path.join(self.root_directory, path)
    
    def validate_path(self, path: str) -> Optional[str]:
        """Валидирует путь и возвращает ошибку если есть"""
        resolved = self.resolve_path(path)
        if not self.is_within_root(resolved):
            return f"Путь {path} находится за пределами рабочей директории"
        return None


class GitIgnoreParser:
    """Парсер .gitignore файлов"""
    
    def __init__(self, root_directory: str):
        self.root_directory = root_directory
        self.patterns = self._load_gitignore()
    
    def _load_gitignore(self) -> List[str]:
        """Загружает паттерны из .gitignore"""
        gitignore_path = os.path.join(self.root_directory, '.gitignore')
        patterns = []
        
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception:
                pass
        
        return patterns
    
    def should_ignore(self, path: str) -> bool:
        """Проверяет, должен ли файл быть проигнорирован"""
        rel_path = os.path.relpath(path, self.root_directory)
        
        for pattern in self.patterns:
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            if fnmatch.fnmatch(os.path.basename(rel_path), pattern):
                return True
        
        return False 