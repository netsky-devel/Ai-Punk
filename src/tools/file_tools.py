"""
Инструменты для работы с файлами на основе Google Gemini CLI
"""

import os
import re
import fnmatch
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import subprocess
import sys
import shutil
from dataclasses import dataclass


@dataclass
class FileEntry:
    """Информация о файле или директории"""
    name: str
    path: str
    is_directory: bool
    size: int
    modified_time: str


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


class TerminalTool:
    """Инструмент для выполнения команд терминала"""
    
    def __init__(self, root_directory: str):
        self.security = PathSecurity(root_directory)
    
    def execute(self, command: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
        """Выполняет команду в терминале"""
        
        # Определение рабочей директории
        if working_dir:
            error = self.security.validate_path(working_dir)
            if error:
                return {"success": False, "error": error}
            cwd = self.security.resolve_path(working_dir)
        else:
            cwd = self.security.root_directory
        
        if not os.path.exists(cwd):
            return {"success": False, "error": f"Рабочая директория не существует: {working_dir or '.'}"} 
        
        try:
            # Выполнение команды
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": True,
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "working_dir": self.security.make_relative(cwd)
            }
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Команда превысила лимит времени выполнения (60 сек)"}
        except Exception as e:
            return {"success": False, "error": f"Ошибка при выполнении команды: {str(e)}"}


# Глобальные экземпляры инструментов
_root_directory = os.getcwd()
_list_tool = ListDirTool(_root_directory)
_read_tool = ReadFileTool(_root_directory)
_edit_tool = EditFileTool(_root_directory)
_grep_tool = GrepTool(_root_directory)
_terminal_tool = TerminalTool(_root_directory)

# Функции-обертки для удобного использования
def list_directory(path: str = ".", ignore_patterns: Optional[List[str]] = None, 
                  respect_gitignore: bool = True) -> str:
    """Список файлов и директорий"""
    result = _list_tool.execute(path, ignore_patterns, respect_gitignore)
    return result.get('content', result.get('error', 'Unknown error'))

def read_file_content(file_path: str, offset: Optional[int] = None, 
                     limit: Optional[int] = None) -> str:
    """Чтение содержимого файла"""
    result = _read_tool.execute(file_path, offset, limit)
    return result.get('content', result.get('error', 'Unknown error'))

def edit_file_content(file_path: str, old_string: str, new_string: str, 
                     expected_replacements: int = 1) -> str:
    """Редактирование файла"""
    result = _edit_tool.execute(file_path, old_string, new_string, expected_replacements)
    return f"Success: {result.get('success', False)}, Changes: {result.get('replacements_made', 0)}"

def grep_search(pattern: str, path: str = ".", include: Optional[str] = None, 
               case_sensitive: bool = True) -> str:
    """Поиск по файлам"""
    result = _grep_tool.execute(pattern, path, include, case_sensitive)
    if result['success']:
        return f"Found {result['total_matches']} matches in {result['files_searched']} files"
    return result.get('error', 'Search failed')

def file_search(pattern: str, path: str = ".") -> str:
    """Поиск файлов по имени (простая реализация через grep)"""
    try:
        import glob
        search_path = os.path.join(path, "**", f"*{pattern}*")
        matches = glob.glob(search_path, recursive=True)
        
        if matches:
            return f"Found {len(matches)} files: {', '.join(matches[:10])}"
        else:
            return f"No files found matching '{pattern}'"
    except Exception as e:
        return f"Error searching files: {str(e)}"

def run_terminal_command(command: str, working_dir: Optional[str] = None) -> str:
    """Выполнение команды терминала"""
    result = _terminal_tool.execute(command, working_dir)
    if result['success']:
        output = result.get('stdout', '')
        if result.get('stderr'):
            output += f"\nErrors: {result['stderr']}"
        return output
    return result.get('error', 'Command failed') 