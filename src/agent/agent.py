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
from ..localization import get_localization, set_language_from_user_input
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
        workspace_info = f"Current working directory: {workspace_path}" if workspace_path else "Working directory not selected"
        
        # Get tool names and descriptions for the prompt
        tool_names = [tool.name for tool in self.tools]
        tool_descriptions = get_simple_tool_descriptions()
        
        # Create custom prompt template
        prompt_template = f"""
You are AI Punk Agent, an autonomous software development assistant.

{workspace_info}

Your task is to help users with any programming tasks using available tools.

IMPORTANT PRINCIPLES:
1. Always work only within the current working directory
2. Use ONLY RELATIVE PATHS: "." for current directory, "src/config.py" for files in subdirectories
3. DO NOT use absolute paths like "C:\\Users\\..." - they don't work!
4. Be methodical and thorough in your actions
5. Explain your thoughts and actions in clear language
6. When errors occur, suggest solutions
7. Always verify the results of your actions

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
        set_language_from_user_input(message)
        
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


def create_agent(console: Optional[Console] = None) -> AIPunkAgent:
    """Factory function to create an AI Punk agent"""
    return AIPunkAgent(console)


def quick_execute(task: str, console: Optional[Console] = None) -> Dict[str, Any]:
    """Quick execution of a task with a new agent instance"""
    agent = create_agent(console)
    return agent.execute_task(task) 