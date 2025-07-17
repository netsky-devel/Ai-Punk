"""
AI Punk Agent
Main agent class using LangChain ReAct pattern with full transparency
Enhanced with Smart Context Manager for intelligent workflow assistance
"""

import os
import asyncio
import time
from typing import Optional, Dict, Any, List
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from rich.console import Console

from ..config.manager import ConfigManager
from ..config.models import AIProvider
from ..workspace.manager import WorkspaceManager
from ..localization.core import Localization
from .transparency import TransparencyCallback
from .wrappers.factory import create_simple_langchain_tools, get_simple_tool_descriptions
from ..tools.project_analyzer import ProjectAnalyzer
from ..context.manager import SmartContextManager


class AIPunkAgent:
    """
    AI Punk autonomous coding agent with full process transparency
    Uses LangChain ReAct pattern for reasoning and acting
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.workspace = WorkspaceManager()
        self.localization = Localization()
        self.transparency_callback = TransparencyCallback(self.console)
        
        # Smart Context Manager for intelligent assistance
        self.context_manager = None
        self._context_initialized = False
        
        # Initialize LLM and agent
        self.llm = self._create_llm()
        self.tools = create_simple_langchain_tools()
        self.agent = self._create_agent()
        self.agent_executor = self._create_agent_executor()
        
        # Auto-analyze project for better context understanding
        self._auto_analyze_project()
        
        # Initialize Smart Context Manager (async)
        self._initialize_context_manager()
    
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
        workspace_info = f"Current working directory: {workspace_path}" if workspace_path else "Working directory not selected"
        
        # Get tool names and descriptions for the prompt
        tool_names = [tool.name for tool in self.tools]
        tool_descriptions = get_simple_tool_descriptions()
        
        # Create custom prompt template
        prompt_template = f"""
You are AI Punk Agent, an autonomous software development assistant with SEMANTIC UNDERSTANDING of codebases.

{workspace_info}

Your task is to help users with any programming tasks using available tools. You have INTELLIGENT UNDERSTANDING of the project structure and can find code by meaning, not just text search.

IMPORTANT PRINCIPLES:
1. Always work only within the current working directory
2. Use ONLY RELATIVE PATHS: "." for current directory, "src/config.py" for files in subdirectories
3. DO NOT use absolute paths like "C:\\Users\\..." - they don't work!
4. Be methodical and thorough in your actions
5. Explain your thoughts and actions in clear language
6. When errors occur, suggest solutions
7. Always verify the results of your actions

INTELLIGENT SEARCH CAPABILITIES:
- Use 'semantic_search' for finding code by MEANING and FUNCTIONALITY
- Use 'grep_search' only for exact text matches
- semantic_search understands concepts like "authentication", "error handling", "database operations"
- Always prefer semantic_search when user asks "where", "how", "find code that does X"

LANGUAGE ADAPTATION:
- Automatically detect the user's language from their input
- Respond in the same language the user uses
- If user writes in Russian, respond in Russian
- If user writes in English, respond in English
- For mixed languages, prioritize the dominant language in the user's message

PATH USAGE EXAMPLES:
- list_directory with path "." - show current directory
- list_directory with path "src" - show src folder
- read_file with path "main.py" - read main.py file
- read_file with path "src/config.py" - read file in subdirectory

SEARCH STRATEGY:
- For conceptual questions: Use semantic_search first (e.g., "where is user authentication?")
- For exact text: Use grep_search (e.g., find "import pandas")
- Read files that semantic_search identifies as relevant
- Understand the project context before making changes

AVAILABLE TOOLS:
{{tools}}

TOOL NAMES: {{tool_names}}

RESPONSE FORMAT:
Use the following format for reasoning:

Thought: I need to think about what I need to do
Action: tool_name
Action Input: input data for the tool
Observation: result of tool execution
... (this Thought/Action/Action Input/Observation cycle can repeat)
Thought: Now I know the final answer
Final Answer: final answer to the user

Begin!

Question: {{input}}
{{agent_scratchpad}}"""
        
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
    
    def _auto_analyze_project(self):
        """Automatically analyze project structure and create semantic index"""
        try:
            workspace_path = self.workspace.get_current_workspace()
            if not workspace_path:
                return
                
            self.console.print("🧠 [bold blue]Инициализирую умного агента...[/bold blue]")
            self.console.print("📊 Анализирую проект для лучшего понимания контекста")
            
            # Create project analyzer
            analyzer = ProjectAnalyzer(str(workspace_path))
            
            # Perform analysis (this also creates semantic index)
            result = analyzer.execute()
            
            if result["success"] and "summary" in result:
                self.console.print("\n✅ [bold green]Проект проанализирован![/bold green]")
                self.console.print(result["summary"])
                self.console.print("\n🚀 Агент готов к работе с полным пониманием проекта!\n")
            else:
                self.console.print("⚠️ [yellow]Анализ проекта завершился с ошибкой, но агент всё равно готов к работе[/yellow]")
                
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Ошибка автоанализа: {e}[/yellow]")
            self.console.print("🤖 Агент готов к работе в базовом режиме")
    
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
        # Set language based on user input
        self.localization.set_language_from_text(message)
        
        result = self.execute_task(message)
        
        if result["success"]:
            return result["output"]
        else:
            return f"Error: {result['error']}"
    
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
    
    def _initialize_context_manager(self):
        """Initialize Smart Context Manager asynchronously"""
        try:
            workspace_path = self.workspace.get_current_workspace()
            if workspace_path:
                self.context_manager = SmartContextManager(self.workspace)
                self.console.print("🧠 [blue]Smart Context Manager готов к инициализации[/blue]")
            else:
                self.console.print("⚠️ [yellow]Workspace не выбран - Smart Context Manager недоступен[/yellow]")
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Ошибка инициализации Smart Context Manager: {e}[/yellow]")
    
    async def _ensure_context_initialized(self) -> bool:
        """Ensure context manager is initialized"""
        if not self.context_manager:
            return False
            
        if not self._context_initialized:
            self.console.print("🧠 [blue]Инициализирую Smart Context Manager...[/blue]")
            result = await self.context_manager.initialize()
            
            if result["success"]:
                self._context_initialized = True
                self.console.print("✅ [green]Smart Context Manager активирован![/green]")
                return True
            else:
                self.console.print(f"❌ [red]Ошибка инициализации: {result.get('error', 'Unknown error')}[/red]")
                return False
        
        return True
    
    async def execute_task_with_context(self, task: str) -> Dict[str, Any]:
        """Execute task with Smart Context Manager enhancement"""
        start_time = time.time()
        
        # Initialize context if available
        context_available = await self._ensure_context_initialized()
        
        # Get context suggestions if available
        context_suggestions = {}
        if context_available:
            try:
                context_suggestions = await self.context_manager.suggest_next_actions(task)
                
                # Display context insights
                if context_suggestions.get("suggested_next_steps"):
                    self.console.print("\n💡 [blue]Smart Context Suggestions:[/blue]")
                    for suggestion in context_suggestions["suggested_next_steps"]:
                        self.console.print(f"   • {suggestion}")
                    self.console.print()
                
            except Exception as e:
                self.console.print(f"⚠️ [yellow]Context analysis error: {e}[/yellow]")
        
        # Enhanced prompt with context
        enhanced_task = task
        if context_suggestions.get("semantic_matches"):
            relevant_files = [match["file_path"] for match in context_suggestions["semantic_matches"][:2]]
            enhanced_task += f"\n\nContext: Consider these relevant files: {', '.join(relevant_files)}"
        
        # Execute original task
        result = self.execute_task(enhanced_task)
        
        # Track execution with context manager
        if context_available:
            try:
                execution_time = time.time() - start_time
                await self.context_manager.track_action(
                    tool_name="agent_execution",
                    input_data={"task": task, "enhanced": bool(context_suggestions)},
                    result={"success": result["success"]},
                    execution_time=execution_time
                )
            except Exception as e:
                self.console.print(f"⚠️ [yellow]Context tracking error: {e}[/yellow]")
        
        return result
    
    async def add_file_to_context(self, file_path: str, content: str = None):
        """Add file content to context for semantic search"""
        if not await self._ensure_context_initialized():
            return
        
        try:
            # Track file access
            file_size = 0
            if content is None:
                # Read file content if not provided
                full_path = self.workspace.get_current_workspace() / file_path
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    file_size = full_path.stat().st_size
            
            if content:
                # Add to context
                await self.context_manager.track_file_access(file_path, file_size)
                await self.context_manager.add_code_embedding(file_path, content)
                self.console.print(f"📝 [green]Added {file_path} to context[/green]")
        
        except Exception as e:
            self.console.print(f"❌ [red]Failed to add {file_path} to context: {e}[/red]")
    
    async def get_context_status(self) -> Dict[str, Any]:
        """Get Smart Context Manager status"""
        if not self.context_manager:
            return {"available": False, "reason": "Not initialized"}
        
        if not self._context_initialized:
            return {"available": False, "reason": "Not initialized"}
        
        try:
            return await self.context_manager.get_status()
        except Exception as e:
            return {"available": False, "error": str(e)}


def create_agent(console: Optional[Console] = None) -> AIPunkAgent:
    """Factory function to create an AI Punk agent"""
    return AIPunkAgent(console)


def quick_execute(task: str, console: Optional[Console] = None) -> Dict[str, Any]:
    """Quick execution of a task with a new agent instance"""
    agent = create_agent(console)
    return agent.execute_task(task) 