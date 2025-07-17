"""
Semantic Search LangChain Wrapper
Intelligent code search by meaning for LangChain agents
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

from ...tools.semantic_search import SemanticSearchTool


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