"""
File Operations LangChain Wrappers
LangChain обертки для операций с файлами (поиск, удаление)
"""

from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from ...tools.filesystem.file_search import FileSearchTool
from ...tools.filesystem.delete_file import DeleteFileTool


class SimpleFileSearchInput(BaseModel):
    """Входные данные для поиска файлов"""
    query: str = Field(description="Поисковый запрос (часть имени файла или пути)")
    path: str = Field(default=".", description="Путь для поиска (по умолчанию текущая директория)")
    max_results: int = Field(default=10, description="Максимальное количество результатов")


class SimpleDeleteFileInput(BaseModel):
    """Входные данные для удаления файла"""
    path: str = Field(description="Путь к файлу для удаления")
    create_backup: bool = Field(default=True, description="Создать резервную копию перед удалением")


class SimpleFileSearchLangChain(BaseTool):
    """Простая LangChain обертка для поиска файлов"""
    name: str = "file_search"
    description: str = """Ищет файлы по имени или части пути.
    
    Передай поисковый запрос. Поиск работает по частичному совпадению имени файла или пути.
    Примеры: "config", "main.py", "test", ".json"
    """
    args_schema: Type[BaseModel] = SimpleFileSearchInput
    
    def __init__(self, workspace_path: str):
        super().__init__()
        self._tool = FileSearchTool(workspace_path)
    
    def _run(self, query: str, path: str = ".", max_results: int = 10) -> str:
        result = self._tool.execute(query, path, max_results)
        
        if not result["success"]:
            return f"❌ Ошибка: {result['error']}"
        
        if not result["files"]:
            return f"🔍 Поиск '{query}': файлы не найдены"
        
        output = [f"🔍 Поиск '{query}': найдено {len(result['files'])} файлов"]
        output.append("")
        
        for file_info in result["files"]:
            match_type_emoji = {
                "exact_name": "🎯",
                "partial_name": "📋", 
                "path_match": "📁",
                "wildcard": "🔎"
            }
            emoji = match_type_emoji.get(file_info["match_type"], "📄")
            output.append(f"{emoji} {file_info['name']} - {file_info['path']}")
        
        return "\n".join(output)


class SimpleDeleteFileLangChain(BaseTool):
    """Простая LangChain обертка для удаления файлов"""
    name: str = "delete_file" 
    description: str = """Безопасно удаляет файл с созданием резервной копии.
    
    Передай путь к файлу. По умолчанию создается резервная копия перед удалением.
    Примеры: "temp.txt", "src/old_file.py", "backup/data.json"
    """
    args_schema: Type[BaseModel] = SimpleDeleteFileInput
    
    def __init__(self, workspace_path: str):
        super().__init__()
        self._tool = DeleteFileTool(workspace_path)
    
    def _run(self, path: str, create_backup: bool = True) -> str:
        result = self._tool.execute(path, create_backup)
        
        if not result["success"]:
            return f"❌ Ошибка: {result['error']}"
        
        output = [f"✅ {result['message']}"]
        
        if result.get("backup_path"):
            output.append(f"💾 Создана резервная копия: {result['backup_path']}")
        
        if result.get("file_size"):
            size = result["file_size"]
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            output.append(f"📊 Размер файла: {size_str}")
        
        return "\n".join(output) 