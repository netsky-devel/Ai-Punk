"""
AI Punk Agent
Main agent class using LangChain ReAct pattern with full transparency
"""

import os
from typing import Optional, Dict, Any, List
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from rich.console import Console

from ..config import get_config, AIProvider
from ..workspace import get_workspace
from .transparency import TransparencyCallback
from .langchain_tools import create_simple_langchain_tools, get_simple_tool_descriptions


class AIPunkAgent:
    """
    AI Punk autonomous coding agent with full process transparency
    Uses LangChain ReAct pattern for reasoning and acting
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.config = get_config()
        self.workspace = get_workspace()
        self.transparency_callback = TransparencyCallback(self.console)
        
        # Initialize LLM and agent
        self.llm = self._create_llm()
        self.tools = create_simple_langchain_tools()
        self.agent = self._create_agent()
        self.agent_executor = self._create_agent_executor()
        
    def _create_llm(self):
        """Create LLM based on configuration"""
        if not self.config.ai_provider:
            raise ValueError("AI provider not configured. Please run setup first.")
            
        provider_config = self.config.ai_provider
        
        if provider_config.provider == AIProvider.OPENAI:
            return ChatOpenAI(
                api_key=provider_config.api_key,
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
        elif provider_config.provider == AIProvider.GOOGLE:
            return ChatGoogleGenerativeAI(
                google_api_key=provider_config.api_key,
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
        elif provider_config.provider == AIProvider.ANTHROPIC:
            return ChatAnthropic(
                anthropic_api_key=provider_config.api_key,
                model=provider_config.model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
        else:
            raise ValueError(f"Unsupported AI provider: {provider_config.provider}")
    
    def _create_agent(self):
        """Create ReAct agent with custom prompt"""
        
        # Get current workspace info
        workspace_path = self.workspace.get_current_workspace()
        workspace_info = f"Текущая рабочая директория: {workspace_path}" if workspace_path else "Рабочая директория не выбрана"
        
        # Get tool names and descriptions for the prompt
        tool_names = [tool.name for tool in self.tools]
        tool_descriptions = get_simple_tool_descriptions()
        
        # Create custom prompt template
        prompt_template = f"""
Ты - AI Punk Agent, автономный помощник для разработки программного обеспечения.

{workspace_info}

Твоя задача - помочь пользователю с любыми задачами программирования, используя доступные инструменты.

ВАЖНЫЕ ПРИНЦИПЫ:
1. Всегда работай только в пределах текущей рабочей директории
2. Используй ТОЛЬКО ОТНОСИТЕЛЬНЫЕ ПУТИ: "." для текущей директории, "src/config.py" для файлов в подпапках
3. НЕ используй абсолютные пути типа "C:\\Users\\..." - они не работают!
4. Будь методичным и тщательным в своих действиях
5. Объясняй свои мысли и действия понятным языком
6. При возникновении ошибок предлагай решения
7. Всегда проверяй результаты своих действий

ПРИМЕРЫ ПРАВИЛЬНОГО ИСПОЛЬЗОВАНИЯ ПУТЕЙ:
- list_dir с путем "." - показать текущую директорию
- list_dir с путем "src" - показать папку src
- read_file с путем "main.py" - прочитать файл main.py
- read_file с путем "src/config.py" - прочитать файл в подпапке

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:
{{tools}}

ИМЕНА ИНСТРУМЕНТОВ: {{tool_names}}

ФОРМАТ ОТВЕТА:
Используй следующий формат для рассуждений:

Thought: Я должен подумать о том, что мне нужно сделать
Action: название_инструмента
Action Input: входные данные для инструмента
Observation: результат выполнения инструмента
... (этот цикл Thought/Action/Action Input/Observation может повторяться)
Thought: Теперь я знаю окончательный ответ
Final Answer: окончательный ответ пользователю

Начинай!

Вопрос: {{input}}
Thought: {{agent_scratchpad}}
"""
        
        prompt = PromptTemplate.from_template(prompt_template)
        
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    def _create_agent_executor(self):
        """Create agent executor with transparency callbacks"""
        return AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            callbacks=[self.transparency_callback],
            max_iterations=self.config.agent.max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a task using the agent
        
        Args:
            task: The task description from the user
            
        Returns:
            Dictionary with execution results and metadata
        """
        # Display welcome message and task header
        self.transparency_callback.display_welcome()
        self.transparency_callback.display_task_header(task)
        
        try:
            # Get current workspace for context
            workspace_path = self.workspace.get_current_workspace()
            
            # Prepare input with workspace context
            agent_input = {
                "input": task,
                "workspace": str(workspace_path) if workspace_path else "Не выбрана"
            }
            
            # Execute the agent
            result = self.agent_executor.invoke(agent_input)
            
            return {
                "success": True,
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "workspace": str(workspace_path) if workspace_path else None
            }
            
        except Exception as e:
            error_msg = f"Ошибка выполнения задачи: {str(e)}"
            self.console.print(f"❌ {error_msg}", style="red")
            
            return {
                "success": False,
                "error": error_msg,
                "workspace": str(workspace_path) if workspace_path else None
            }
    
    def chat(self, message: str) -> str:
        """
        Simple chat interface for the agent
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        result = self.execute_task(message)
        
        if result["success"]:
            return result["output"]
        else:
            return f"Произошла ошибка: {result['error']}"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        workspace_path = self.workspace.get_current_workspace()
        
        return {
            "workspace": str(workspace_path) if workspace_path else None,
            "ai_provider": self.config.ai_provider.provider.value if self.config.ai_provider else None,
            "model": self.config.ai_provider.model if self.config.ai_provider else None,
            "tools_available": len(self.tools),
            "max_iterations": self.config.agent.max_iterations,
            "verbose": self.config.agent.verbose
        }
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return [tool.name for tool in self.tools]
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        for tool in self.tools:
            if tool.name == tool_name:
                return {
                    "name": tool.name,
                    "description": tool.description,
                    "args_schema": tool.args_schema.schema() if tool.args_schema else None
                }
        return None


def create_agent(console: Optional[Console] = None) -> AIPunkAgent:
    """Factory function to create an AI Punk agent"""
    return AIPunkAgent(console)


def quick_execute(task: str, console: Optional[Console] = None) -> Dict[str, Any]:
    """Quick execution of a task with a new agent instance"""
    agent = create_agent(console)
    return agent.execute_task(task) 