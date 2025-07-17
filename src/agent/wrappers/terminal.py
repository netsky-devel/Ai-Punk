"""
Terminal LangChain Wrapper
Shell command execution for LangChain agents
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

from ...tools.filesystem import TerminalTool


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