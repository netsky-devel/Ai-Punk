"""
AI Punk Agent Transparency
Provides full visibility into agent's thinking and action process
"""

import time
from typing import Any, Dict, List, Optional
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from ..localization.core import Localization

class TransparencyCallback(BaseCallbackHandler):
    """Callback handler that provides full transparency into agent operations"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.step_count = 0
        self.start_time = None
        self.localization = Localization()
        
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Called when agent takes an action"""
        self.step_count += 1
        
        # Display thinking process
        thinking_panel = Panel(
            Text(action.log, style="cyan"),
            title=t("agent_thinking", self.step_count),
            title_align="left",
            border_style="cyan"
        )
        self.console.print(thinking_panel)
        
        # Display action details
        action_table = Table(show_header=False, box=None, padding=(0, 1))
        action_table.add_column("Field", style="bold yellow")
        action_table.add_column("Value", style="white")
        
        action_table.add_row(t("tool_label"), action.tool)
        action_table.add_row(t("input_label"), str(action.tool_input))
        
        action_panel = Panel(
            action_table,
            title=t("agent_action"),
            title_align="left",
            border_style="yellow"
        )
        self.console.print(action_panel)
        
        # Show spinner while tool is executing
        self.console.print(t("executing"), style="dim")
        
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Called when agent finishes"""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        # Display final result
        result_panel = Panel(
            Text(finish.return_values.get("output", ""), style="green"),
            title=t("execution_result", elapsed_time),
            title_align="left",
            border_style="green"
        )
        self.console.print(result_panel)
        
        # Display execution summary
        summary_table = Table(show_header=False, box=None, padding=(0, 1))
        summary_table.add_column("Metric", style="bold blue")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row(t("total_steps"), str(self.step_count))
        summary_table.add_row(t("execution_time"), f"{elapsed_time:.2f}с")
        summary_table.add_row("", "")
        summary_table.add_row(t("status"), t("status_completed"))
        
        summary_panel = Panel(
            summary_table,
            title=t("execution_summary"),
            title_align="left",
            border_style="blue"
        )
        self.console.print(summary_panel)
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        """Called when a tool starts"""
        # This is handled in on_agent_action for better UX
        pass
        
    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Called when a tool ends"""
        # Tool output is shown directly by the tools themselves
        # We don't need to duplicate it here
        pass
        
    def on_tool_error(self, error: Exception, **kwargs: Any) -> Any:
        """Called when a tool encounters an error"""
        error_panel = Panel(
            Text(str(error), style="red"),
            title=t("tool_error"),
            title_align="left",
            border_style="red"
        )
        self.console.print(error_panel)
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> Any:
        """Called when LLM starts"""
        # We don't show LLM details to keep output clean
        pass
        
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Called when LLM ends"""
        pass
        
    def on_llm_error(self, error: Exception, **kwargs: Any) -> Any:
        """Called when LLM encounters an error"""
        pass
        
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Called when chain starts"""
        self.start_time = time.time()
        
        # Display welcome and task header
        self.display_welcome()
        
        task = inputs.get("input", "Unknown task")
        self.display_task_header(task)
        
        # Detect language from user input and set localization
        if task and task != "Unknown task":
            self.localization.set_language_from_text(task)
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Called when chain ends"""
        pass
    
    def on_chain_error(self, error: Exception, **kwargs: Any) -> Any:
        """Called when chain encounters an error"""
        pass
        
    def display_welcome(self):
        """Display welcome banner"""
        welcome_text = Text()
        welcome_text.append(t("welcome_banner"), style="bold bright_blue")
        welcome_text.append(" готов к работе!", style="bold bright_blue")
        welcome_text.append("\n", style="white")
        welcome_text.append("Все действия и мысли агента будут отображаться в реальном времени", style="dim")
        
        welcome_panel = Panel(
            Align.center(welcome_text),
            title=t("welcome_title"),
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(welcome_panel)
        
    def display_task_header(self, task: str):
        """Display task header"""
        task_panel = Panel(
            Text(task, style="bold white"),
            title="📋 Новая задача",
            title_align="left",
            border_style="white"
        )
        self.console.print(task_panel) 