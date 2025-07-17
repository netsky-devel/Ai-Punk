"""
Filesystem LangChain Wrappers
Directory listing, file reading and editing wrappers for LangChain
"""

import json
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

from ...tools.filesystem import ListDirTool, ReadFileTool, EditFileTool


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