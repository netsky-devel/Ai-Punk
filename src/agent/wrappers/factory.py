"""
LangChain Tools Factory
Functions to create and describe tool collections
"""

from typing import List
from langchain.tools import BaseTool

from .filesystem import SimpleListDirLangChain, SimpleReadFileLangChain, SimpleEditFileLangChain
from .search import SimpleGrepLangChain
from .terminal import SimpleTerminalLangChain
from .semantic import SimpleSemanticSearchLangChain
from .file_ops import SimpleFileSearchLangChain, SimpleDeleteFileLangChain


def create_simple_langchain_tools() -> List[BaseTool]:
    """Создает список простых LangChain инструментов для агента"""
    from ...workspace.manager import WorkspaceManager
    workspace_manager = WorkspaceManager()
    workspace_path = str(workspace_manager.current_path) if workspace_manager.current_path else "."
    
    return [
        SimpleListDirLangChain(workspace_path),
        SimpleReadFileLangChain(workspace_path),
        SimpleEditFileLangChain(workspace_path),
        SimpleGrepLangChain(workspace_path),
        SimpleTerminalLangChain(workspace_path),
        SimpleSemanticSearchLangChain(workspace_path),
        SimpleFileSearchLangChain(workspace_path),
        SimpleDeleteFileLangChain(workspace_path)
    ]


def get_simple_tool_descriptions() -> str:
    """Возвращает описания простых инструментов для промпта"""
    descriptions = [
        "list_directory: Показывает содержимое директории",
        "read_file: Читает содержимое файла",
        "edit_file: Редактирует файл с заменой строк",
        "grep_search: Ищет текст в файлах проекта",
        "run_terminal: Выполняет команды в терминале",
        "semantic_search: Семантический поиск по кодовой базе по смыслу и функциональности",
        "file_search: Быстрый поиск файлов по имени или части пути",
        "delete_file: Безопасное удаление файлов с созданием резервных копий"
    ]
    return "\n".join(descriptions) 