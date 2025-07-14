"""
AI Punk Transparency System
Real-time display of agent thoughts, actions, and observations
"""

import time
from typing import Dict, Any, List, Optional
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.align import Align
from rich.columns import Columns

class TransparencyCallback(BaseCallbackHandler):
    """Callback handler for displaying agent process transparency"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.step_count = 0
        self.start_time = None
        self.current_step = None
        self.live_display = None
        
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Called when agent takes an action"""
        self.step_count += 1
        
        # Display thinking process
        thinking_panel = Panel(
            Text(action.log, style="cyan"),
            title=f"🧠 Мышление агента (Шаг {self.step_count})",
            title_align="left",
            border_style="cyan"
        )
        self.console.print(thinking_panel)
        
        # Display action details
        action_table = Table(show_header=False, box=None, padding=(0, 1))
        action_table.add_column("Field", style="bold yellow")
        action_table.add_column("Value", style="white")
        
        action_table.add_row("🔧 Инструмент:", action.tool)
        action_table.add_row("📝 Ввод:", str(action.tool_input))
        
        action_panel = Panel(
            action_table,
            title="⚡ Действие агента",
            title_align="left",
            border_style="yellow"
        )
        self.console.print(action_panel)
        
        # Show spinner while tool is executing
        self.console.print("⏳ Выполняется...", style="dim")
        
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Called when agent finishes"""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        # Display final result
        result_panel = Panel(
            Text(finish.return_values.get("output", ""), style="green"),
            title=f"✅ Результат выполнения (за {elapsed_time:.2f}с)",
            title_align="left",
            border_style="green"
        )
        self.console.print(result_panel)
        
        # Display summary
        summary_table = Table(show_header=False, box=None, padding=(0, 1))
        summary_table.add_column("Metric", style="bold blue")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("📊 Всего шагов:", str(self.step_count))
        summary_table.add_row("⏱️ Время выполнения:", f"{elapsed_time:.2f}с")
        summary_table.add_row("🎯 Статус:", "Завершено успешно")
        
        summary_panel = Panel(
            summary_table,
            title="📈 Сводка выполнения",
            title_align="left",
            border_style="blue"
        )
        self.console.print(summary_panel)
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        """Called when tool starts executing"""
        tool_name = serialized.get("name", "unknown")
        
        tool_panel = Panel(
            f"🔧 Запуск инструмента: {tool_name}\n📥 Входные данные: {input_str}",
            title="🚀 Начало выполнения инструмента",
            title_align="left",
            border_style="magenta"
        )
        self.console.print(tool_panel)
        
    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Called when tool finishes executing"""
        # Truncate very long outputs
        display_output = output
        if len(output) > 500:
            display_output = output[:500] + "\n... (вывод сокращен)"
            
        result_panel = Panel(
            display_output,
            title="📤 Результат инструмента",
            title_align="left",
            border_style="green"
        )
        self.console.print(result_panel)
        
    def on_tool_error(self, error: Exception, **kwargs: Any) -> Any:
        """Called when tool encounters an error"""
        error_panel = Panel(
            f"❌ Ошибка: {str(error)}",
            title="⚠️ Ошибка выполнения инструмента",
            title_align="left",
            border_style="red"
        )
        self.console.print(error_panel)
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> Any:
        """Called when LLM starts generating"""
        self.start_time = time.time()
        
        llm_panel = Panel(
            "🤖 Генерация ответа от языковой модели...",
            title="💭 Обработка LLM",
            title_align="left",
            border_style="blue"
        )
        self.console.print(llm_panel)
        
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Called when LLM finishes generating"""
        # Don't display raw LLM output as it's handled by agent callbacks
        pass
        
    def on_llm_error(self, error: Exception, **kwargs: Any) -> Any:
        """Called when LLM encounters an error"""
        error_panel = Panel(
            f"❌ Ошибка LLM: {str(error)}",
            title="⚠️ Ошибка языковой модели",
            title_align="left",
            border_style="red"
        )
        self.console.print(error_panel)
        
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Called when chain starts"""
        self.console.print("\n" + "="*80)
        
        start_panel = Panel(
            f"🎯 Задача: {inputs.get('input', 'Не указана')}\n"
            f"📁 Рабочая директория: {inputs.get('workspace', 'Не указана')}",
            title="🚀 Начало выполнения задачи",
            title_align="left",
            border_style="bright_blue"
        )
        self.console.print(start_panel)
        
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Called when chain ends"""
        self.console.print("="*80 + "\n")
        
    def on_chain_error(self, error: Exception, **kwargs: Any) -> Any:
        """Called when chain encounters an error"""
        error_panel = Panel(
            f"❌ Критическая ошибка: {str(error)}",
            title="💥 Ошибка выполнения цепочки",
            title_align="left",
            border_style="red"
        )
        self.console.print(error_panel)
        
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = Text()
        welcome_text.append("🤖 AI Punk Agent", style="bold bright_blue")
        welcome_text.append(" готов к работе!\n", style="white")
        welcome_text.append("Все действия и мысли агента будут отображаться в реальном времени", style="dim")
        
        welcome_panel = Panel(
            Align.center(welcome_text),
            title="🎉 Добро пожаловать",
            border_style="bright_blue"
        )
        self.console.print(welcome_panel)
        
    def display_task_header(self, task: str):
        """Display task header"""
        task_panel = Panel(
            Text(task, style="bold white"),
            title="📋 Новая задача",
            title_align="left",
            border_style="bright_green"
        )
        self.console.print(task_panel) 