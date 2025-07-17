"""
Упрощенные LangChain обертки для инструментов
Принимают один строковый параметр для простоты парсинга
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Type
import os
import sys
import json

# Добавляем пути к нашим инструментам
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.tools.file_tools import (
    ListDirTool,
    ReadFileTool,
    EditFileTool,
    GrepTool,
    TerminalTool
)
from src.tools.semantic_search import SemanticSearchTool


class SimpleListDirInput(BaseModel):
    """Входные параметры для простого инструмента списка файлов"""
    path: str = Field(description="Путь к директории для просмотра (относительный)")


class SimpleListDirLangChain(BaseTool):
    """Простая LangChain обертка для инструмента списка файлов"""
    name: str = "list_directory"
    description: str = """Показывает содержимое директории.
    
    Используй ТОЛЬКО ОТНОСИТЕЛЬНЫЕ ПУТИ от корня проекта.
    Примеры: ".", "src", "docs"
    """
    args_schema: Type[BaseModel] = SimpleListDirInput
    
    def __init__(self, workspace_path: str):
        super().__init__()
        self._tool = ListDirTool(workspace_path)
    
    def _run(self, path: str) -> str:
        # Очищаем путь от лишних символов новой строки и пробелов
        clean_path = path.strip()
        result = self._tool.execute(clean_path)
        
        if not result["success"]:
            return f"❌ Ошибка: {result['error']}"
        
        output = [f"📁 Содержимое директории: {result['path']}"]
        output.append(f"📊 Всего элементов: {result['total']}")
        output.append("")
        
        for entry in result["entries"]:
            icon = "📁" if entry["is_directory"] else "📄"
            size = f" ({entry['size']} байт)" if not entry["is_directory"] else ""
            output.append(f"{icon} {entry['name']}{size}")
        
        return "\n".join(output)


class SimpleReadFileInput(BaseModel):
    """Входные параметры для простого инструмента чтения файлов"""
    file_path: str = Field(description="Путь к файлу для чтения (относительный)")


class SimpleReadFileLangChain(BaseTool):
    """Простая LangChain обертка для инструмента чтения файлов"""
    name: str = "read_file"
    description: str = """Читает содержимое файла.
    
    Используй ТОЛЬКО ОТНОСИТЕЛЬНЫЕ ПУТИ от корня проекта.
    Примеры: "README.md", "src/main.py", "docs/guide.md"
    """
    args_schema: Type[BaseModel] = SimpleReadFileInput
    
    def __init__(self, workspace_path: str):
        super().__init__()
        self._tool = ReadFileTool(workspace_path)
    
    def _run(self, file_path: str) -> str:
        # Очищаем путь от лишних символов новой строки и пробелов
        clean_path = file_path.strip()
        result = self._tool.execute(clean_path)
        
        if not result["success"]:
            return f"❌ Ошибка: {result['error']}"
        
        output = [f"📄 Файл: {result['path']}"]
        output.append("")
        output.append(result["content"])
        
        return "\n".join(output)


class SimpleEditFileInput(BaseModel):
    """Входные параметры для простого инструмента редактирования файлов"""
    input_data: str = Field(description="JSON строка с параметрами: {\"file_path\": \"path\", \"old_string\": \"old\", \"new_string\": \"new\"}")


class SimpleEditFileLangChain(BaseTool):
    """Простая LangChain обертка для инструмента редактирования файлов"""
    name: str = "edit_file"
    description: str = """Редактирует файл с заменой строк.
    
    Передай JSON строку с параметрами:
    {"file_path": "path/to/file", "old_string": "текст для замены", "new_string": "новый текст"}
    
    Для создания нового файла используй old_string="" и new_string="содержимое файла"
    """
    args_schema: Type[BaseModel] = SimpleEditFileInput
    
    def __init__(self, workspace_path: str):
        super().__init__()
        self._tool = EditFileTool(workspace_path)
    
    def _run(self, input_data: str) -> str:
        try:
            # Очищаем входные данные от лишних символов
            clean_input = input_data.strip()
            data = json.loads(clean_input)
            file_path = data["file_path"].strip()
            old_string = data.get("old_string", "")
            new_string = data["new_string"]
            
            result = self._tool.execute(file_path, old_string, new_string)
            
            if not result["success"]:
                return f"❌ Ошибка: {result['error']}"
            
            return f"✅ Файл {result['path']} изменен. Заменено {result['replacements_made']} вхождений."
            
        except json.JSONDecodeError:
            return "❌ Ошибка: Неверный JSON формат"
        except KeyError as e:
            return f"❌ Ошибка: Отсутствует параметр {e}"


class SimpleGrepInput(BaseModel):
    """Входные параметры для простого инструмента поиска"""
    pattern: str = Field(description="Паттерн для поиска")


class SimpleGrepLangChain(BaseTool):
    """Простая LangChain обертка для инструмента поиска"""
    name: str = "grep_search"
    description: str = """Ищет текст в файлах проекта.
    
    Передай паттерн для поиска. Поиск выполняется во всех файлах проекта.
    Примеры: "import", "function", "class MyClass"
    """
    args_schema: Type[BaseModel] = SimpleGrepInput
    
    def __init__(self, workspace_path: str):
        super().__init__()
        self._tool = GrepTool(workspace_path)
    
    def _run(self, pattern: str) -> str:
        # Очищаем паттерн от лишних символов новой строки и пробелов
        clean_pattern = pattern.strip()
        result = self._tool.execute(clean_pattern)
        
        if not result["success"]:
            return f"❌ Ошибка: {result['error']}"
        
        if not result["matches"]:
            return f"🔍 Поиск '{clean_pattern}': совпадений не найдено"
        
        output = [f"🔍 Поиск '{clean_pattern}': найдено {len(result['matches'])} совпадений"]
        output.append("")
        
        for match in result["matches"]:
            output.append(f"📄 {match['file']}:{match['line']} - {match['content'].strip()}")
        
        return "\n".join(output)


class SimpleTerminalInput(BaseModel):
    """Входные параметры для простого инструмента терминала"""
    command: str = Field(description="Команда для выполнения")


class SimpleTerminalLangChain(BaseTool):
    """Простая LangChain обертка для инструмента терминала"""
    name: str = "run_terminal"
    description: str = """Выполняет команды в терминале.
    
    Примеры команд: "python --version", "ls", "dir", "echo Hello"
    """
    args_schema: Type[BaseModel] = SimpleTerminalInput
    
    def __init__(self, workspace_path: str):
        super().__init__()
        self._tool = TerminalTool(workspace_path)
    
    def _run(self, command: str) -> str:
        # Очищаем команду от лишних символов новой строки и пробелов
        clean_command = command.strip()
        result = self._tool.execute(clean_command)
        
        if not result["success"]:
            return f"❌ Ошибка: {result['error']}"
        
        output = [f"💻 Команда: {clean_command}"]
        output.append("")
        output.append(f"📊 Код возврата: {result['return_code']}")
        output.append("")
        
        if result["stdout"]:
            output.append("📤 Вывод:")
            output.append(result["stdout"])
        
        if result["stderr"]:
            output.append("⚠️ Ошибки:")
            output.append(result["stderr"])
        
        return "\n".join(output)


class SimpleSemanticSearchInput(BaseModel):
    """Входные параметры для семантического поиска"""
    query: str = Field(description="Запрос для семантического поиска по смыслу")


class SimpleSemanticSearchLangChain(BaseTool):
    """LangChain обертка для семантического поиска"""
    name: str = "semantic_search"
    description: str = """Семантический поиск по кодовой базе по смыслу.
    
    Ищет код не по точному тексту, а по смыслу и функциональности.
    Примеры: "аутентификация пользователя", "обработка ошибок", "сохранение в базу данных"
    
    Этот инструмент понимает концепции и находит связанный код даже если названия функций отличаются.
    """
    args_schema: Type[BaseModel] = SimpleSemanticSearchInput
    
    def __init__(self, workspace_path: str):
        super().__init__()
        self._tool = SemanticSearchTool(workspace_path)
    
    def _run(self, query: str) -> str:
        clean_query = query.strip()
        result = self._tool.execute(clean_query)
        
        if not result["success"]:
            return f"❌ Ошибка семантического поиска: {result['error']}"
        
        if "results" not in result or not result["results"]:
            return f"🔍 Семантический поиск '{clean_query}': релевантных фрагментов не найдено"
        
        output = [f"🧠 Семантический поиск '{clean_query}': найдено {len(result['results'])} релевантных фрагментов"]
        output.append("")
        
        for item in result["results"]:
            score_percent = int(item["score"] * 100)
            output.append(f"📄 {item['file']}:{item['lines']} (релевантность: {score_percent}%)")
            # Show preview of content
            preview = item["content"].replace('\n', ' ').strip()
            if len(preview) > 150:
                preview = preview[:150] + "..."
            output.append(f"   💡 {preview}")
            output.append("")
        
        return "\n".join(output)


def create_simple_langchain_tools() -> List[BaseTool]:
    """Создает список простых LangChain инструментов для агента"""
    from ..workspace import get_workspace
    workspace = get_workspace()
    workspace_path = str(workspace.current_path) if workspace.current_path else "."
    
    return [
        SimpleListDirLangChain(workspace_path),
        SimpleReadFileLangChain(workspace_path),
        SimpleEditFileLangChain(workspace_path),
        SimpleGrepLangChain(workspace_path),
        SimpleTerminalLangChain(workspace_path),
        SimpleSemanticSearchLangChain(workspace_path)
    ]


def get_simple_tool_descriptions() -> str:
    """Возвращает описания простых инструментов для промпта"""
    descriptions = [
        "list_directory: Показывает содержимое директории",
        "read_file: Читает содержимое файла",
        "edit_file: Редактирует файл с заменой строк",
        "grep_search: Ищет текст в файлах проекта",
        "run_terminal: Выполняет команды в терминале",
        "semantic_search: Семантический поиск по кодовой базе по смыслу и функциональности"
    ]
    return "\n".join(descriptions) 