"""
Search LangChain Wrapper
Grep search functionality for LangChain agents
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

from ...tools.filesystem import GrepTool


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