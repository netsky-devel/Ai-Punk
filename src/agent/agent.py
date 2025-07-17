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
from .prompts.core import PromptManager
from .session import SessionManager


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
        
        # Advanced Prompt Management System
        self.prompt_manager = None
        
        # Session Management for continuity
        self.session_manager = None
        
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
        """Create ReAct agent with advanced prompt system"""
        
        # Use advanced prompt system for dynamic prompt generation
        # The actual prompt will be generated dynamically for each task
        
        # Create a basic template for now - will be enhanced dynamically
        basic_template = """You are AI Punk Agent, an AUTONOMOUS software development assistant.

**CRITICAL**: Be PROACTIVE and AUTONOMOUS. When user asks for development:
1. START CODING IMMEDIATELY - don't ask clarifying questions
2. CREATE COMPLETE FEATURES - don't stop after one file
3. KEEP WORKING - continue until task is fully complete
4. BE DECISIVE - make reasonable assumptions

Available tools: {tools}
Tool names: {tool_names}

AUTONOMOUS WORK FORMAT:
Thought: I understand the requirement. I'll start implementing immediately.
Action: tool_name
Action Input: input data for the tool
Observation: result of tool execution
Thought: Good, continuing with next part...
Action: next_tool
Action Input: next step data
... (KEEP GOING until feature is COMPLETE)
Thought: Feature is complete and working
Final Answer: [Summary of what was built]

Question: {input}
{agent_scratchpad}"""
        
        prompt = PromptTemplate.from_template(basic_template)
        
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
            return_intermediate_steps=True,
            early_stopping_method="generate",  # Continue working autonomously
            max_execution_time=300  # 5 minutes maximum per task
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
        Execute a task using the agent with Smart Context Manager enhancement
        
        Args:
            task: The task description from the user
            
        Returns:
            Dictionary with execution results and metadata
        """
        # Try to use context-enhanced execution if possible
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.execute_task_with_context(task))
        except Exception:
            # Fallback to basic execution if context fails
            return self._execute_task_basic(task)
    
    def _execute_task_basic(self, task: str) -> Dict[str, Any]:
        """Basic task execution without context enhancement"""
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
        """Initialize Smart Context Manager, Advanced Prompt System and Session Management"""
        try:
            workspace_path = self.workspace.get_current_workspace()
            workspace_path_str = str(workspace_path) if workspace_path else None
            
            # Initialize session manager first
            self.session_manager = SessionManager(workspace_path_str)
            
            if workspace_path:
                self.context_manager = SmartContextManager(self.workspace)
                self.prompt_manager = PromptManager(self.context_manager)
                self.console.print("🧠 [blue]Smart Context Manager готов к инициализации[/blue]")
                self.console.print("🎯 [blue]Advanced Prompt System активирован[/blue]")
                self.console.print("💾 [blue]Session Management готов к работе[/blue]")
            else:
                # Initialize prompt manager without context manager
                self.prompt_manager = PromptManager(None)
                self.console.print("⚠️ [yellow]Workspace не выбран - Smart Context Manager недоступен[/yellow]")
                self.console.print("🎯 [blue]Advanced Prompt System работает в базовом режиме[/blue]")
                self.console.print("💾 [blue]Session Management работает глобально[/blue]")
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Ошибка инициализации систем: {e}[/yellow]")
            # Fallback to basic systems
            self.prompt_manager = PromptManager(None)
            self.session_manager = SessionManager(None)
    
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
        """Execute task with Smart Context Manager and Advanced Prompt System"""
        start_time = time.time()
        
        # Initialize context if available
        context_available = await self._ensure_context_initialized()
        
        # Initialize systems if not already done
        if not self.prompt_manager or not self.session_manager:
            self._initialize_context_manager()
        
        # Add conversation context from session
        conversation_context = ""
        if self.session_manager:
            conversation_context = self.session_manager.get_conversation_context()
        
        # Generate enhanced prompt using advanced prompt system
        try:
            workspace_path = self.workspace.get_current_workspace()
            tool_names = [tool.name for tool in self.tools]
            
            # Enhanced task with conversation context
            enhanced_task_with_context = f"{task}\n\n{conversation_context}" if conversation_context != "No previous conversation history." else task
            
            enhanced_prompt = await self.prompt_manager.create_enhanced_prompt(
                base_task=enhanced_task_with_context,
                tools=tool_names,
                workspace_path=str(workspace_path) if workspace_path else None
            )
            
            # Display context insights if available
            if self.prompt_manager.context_manager:
                context_suggestions = await self.prompt_manager.context_manager.suggest_next_actions(task)
                if context_suggestions.get("suggested_next_steps"):
                    self.console.print("\n💡 [blue]Smart Context Suggestions:[/blue]")
                    for suggestion in context_suggestions["suggested_next_steps"]:
                        self.console.print(f"   • {suggestion}")
                    self.console.print()
            
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Prompt enhancement error: {e}[/yellow]")
            enhanced_prompt = task
        
        # Execute task with enhanced prompt
        result = self._execute_task_with_enhanced_prompt(enhanced_prompt, task)
        
        # Update session memory and save conversation turn
        if self.prompt_manager:
            self.prompt_manager.update_session_memory(task, result)
        
        if self.session_manager:
            self.session_manager.add_conversation_turn(task, result)
        
        # Track execution with context manager
        if context_available:
            try:
                execution_time = time.time() - start_time
                await self.context_manager.track_action(
                    tool_name="agent_execution",
                    input_data={"task": task, "enhanced": True},
                    result={"success": result["success"]},
                    execution_time=execution_time
                )
            except Exception as e:
                self.console.print(f"⚠️ [yellow]Context tracking error: {e}[/yellow]")
        
        return result
    
    def _execute_task_with_enhanced_prompt(self, enhanced_prompt: str, original_task: str) -> Dict[str, Any]:
        """Execute task with enhanced prompt"""
        # Display welcome message and task header
        self.transparency_callback.display_welcome()
        self.transparency_callback.display_task_header(original_task)
        
        try:
            # Get current workspace for context
            workspace_path = self.workspace.get_current_workspace()
            
            # Use enhanced prompt as input
            agent_input = {
                "input": enhanced_prompt,
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
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics and status"""
        if not self.session_manager:
            return {"available": False, "reason": "Session manager not initialized"}
        
        try:
            stats = self.session_manager.get_session_stats()
            stats["available"] = True
            return stats
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def clear_session_memory(self):
        """Clear session memory and start fresh"""
        if self.session_manager:
            self.session_manager.clear_session()
            self.console.print("🔄 [green]Session memory cleared - starting fresh![/green]")
        
        if self.prompt_manager:
            self.prompt_manager.clear_session()
            self.console.print("🔄 [green]Prompt memory cleared![/green]")


def create_agent(console: Optional[Console] = None) -> AIPunkAgent:
    """Factory function to create an AI Punk agent"""
    return AIPunkAgent(console)


def quick_execute(task: str, console: Optional[Console] = None) -> Dict[str, Any]:
    """Quick execution of a task with a new agent instance"""
    agent = create_agent(console)
    return agent.execute_task(task) 