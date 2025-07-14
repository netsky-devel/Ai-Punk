"""
AI Punk Agent Interface
Beautiful terminal interface for interacting with the agent
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.columns import Columns
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..agent import AIPunkAgent, create_agent
from ..config import get_config, AIProvider, set_ai_provider
from ..workspace import get_workspace, select_workspace


class AgentInterface:
    """Terminal interface for AI Punk Agent"""
    
    def __init__(self):
        self.console = Console()
        self.agent: Optional[AIPunkAgent] = None
        self.config = get_config()
        self.workspace = get_workspace()
        
    def display_banner(self):
        """Display welcome banner"""
        banner_text = Text()
        banner_text.append("🤖 AI Punk Agent", style="bold bright_blue")
        banner_text.append("\n", style="white")
        banner_text.append("Автономный помощник для разработки ПО", style="dim")
        
        banner_panel = Panel(
            Align.center(banner_text),
            title="Добро пожаловать",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(banner_panel)
        
    def display_status(self):
        """Display current system status"""
        status_table = Table(show_header=False, box=None, padding=(0, 1))
        status_table.add_column("Item", style="bold cyan")
        status_table.add_column("Value", style="white")
        
        # Workspace status
        workspace_path = self.workspace.get_current_workspace()
        if workspace_path:
            status_table.add_row("📁 Рабочая директория:", str(workspace_path))
        else:
            status_table.add_row("📁 Рабочая директория:", "❌ Не выбрана")
            
        # AI Provider status
        if self.config.ai_provider:
            status_table.add_row("🤖 AI Провайдер:", self.config.ai_provider.provider.value)
            status_table.add_row("🧠 Модель:", self.config.ai_provider.model)
        else:
            status_table.add_row("🤖 AI Провайдер:", "❌ Не настроен")
            
        # Agent status
        if self.agent:
            status_table.add_row("⚡ Агент:", "✅ Готов к работе")
            status_table.add_row("🔧 Инструменты:", str(len(self.agent.tools)))
        else:
            status_table.add_row("⚡ Агент:", "❌ Не инициализирован")
            
        status_panel = Panel(
            status_table,
            title="📊 Статус системы",
            border_style="cyan"
        )
        self.console.print(status_panel)
        
    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            if key and value:
                                os.environ[key] = value
            except Exception:
                pass  # Ignore errors in .env file
    
    def setup_ai_provider(self):
        """Setup AI provider configuration"""
        self.console.print("\n🔧 Настройка AI провайдера", style="bold yellow")
        
        # Try to load .env file
        self._load_env_file()
        
        # Choose provider
        provider_choices = {
            "1": ("OpenAI", AIProvider.OPENAI),
            "2": ("Google Gemini", AIProvider.GOOGLE),
            "3": ("Anthropic Claude", AIProvider.ANTHROPIC)
        }
        
        self.console.print("\nВыберите AI провайдера:")
        for key, (name, _) in provider_choices.items():
            self.console.print(f"  {key}. {name}")
            
        self.console.print("\n💡 [dim]Где получить API ключи:[/dim]")
        self.console.print("  [dim]• Google Gemini: https://aistudio.google.com/app/apikey[/dim]")
        self.console.print("  [dim]• OpenAI: https://platform.openai.com/api-keys[/dim]")
        self.console.print("  [dim]• Anthropic: https://console.anthropic.com/account/keys[/dim]")
            
        choice = Prompt.ask("Ваш выбор", choices=list(provider_choices.keys()))
        provider_name, provider = provider_choices[choice]
        
        # Check for existing API key in environment
        env_key_map = {
            AIProvider.GOOGLE: "GOOGLE_AI_API_KEY",
            AIProvider.OPENAI: "OPENAI_API_KEY", 
            AIProvider.ANTHROPIC: "ANTHROPIC_API_KEY"
        }
        
        env_key_name = env_key_map.get(provider)
        existing_key = os.getenv(env_key_name) if env_key_name else None
        
        if existing_key:
            self.console.print(f"✅ Найден API ключ в переменной окружения {env_key_name}", style="green")
            if Confirm.ask("Использовать найденный API ключ?", default=True):
                api_key = existing_key
            else:
                self.console.print(f"\n💡 [dim]Совет: Вы можете вставить API ключ из буфера обмена (Ctrl+V)[/dim]")
                api_key = Prompt.ask(f"Введите API ключ для {provider_name}")
        else:
            self.console.print(f"\n💡 [dim]Совет: Вы можете вставить API ключ из буфера обмена (Ctrl+V)[/dim]")
            self.console.print(f"💡 [dim]Или установить переменную окружения {env_key_name}[/dim]")
            api_key = Prompt.ask(f"Введите API ключ для {provider_name}")
        
        # Choose model
        model_suggestions = {
            AIProvider.OPENAI: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            AIProvider.GOOGLE: [
                "gemini-1.5-flash",      # Быстрая и универсальная (проверенная)
                "gemini-1.5-pro",        # Сложные задачи на рассуждение (проверенная)
                "gemini-1.5-flash-8b",   # Задачи большого объема
                "gemini-2.0-flash-exp",  # Экспериментальная версия 2.0
                "gemini-pro"             # Старая стабильная версия
            ],
            AIProvider.ANTHROPIC: ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        }
        
        suggested_models = model_suggestions.get(provider, [])
        if suggested_models:
            self.console.print(f"\nРекомендуемые модели для {provider_name}:")
            
            # Добавляем описания для Google моделей
            if provider == AIProvider.GOOGLE:
                model_descriptions = {
                    "gemini-1.5-flash": "🔥 Быстрая и универсальная (рекомендуется)",
                    "gemini-1.5-pro": "💎 Сложные задачи на рассуждение", 
                    "gemini-1.5-flash-8b": "⚡ Задачи большого объема, экономичная",
                    "gemini-2.0-flash-exp": "🧪 Экспериментальная версия 2.0",
                    "gemini-pro": "🛡️ Старая стабильная версия"
                }
                for i, model in enumerate(suggested_models, 1):
                    desc = model_descriptions.get(model, "")
                    self.console.print(f"  {i}. {model} {desc}")
            else:
                for i, model in enumerate(suggested_models, 1):
                    self.console.print(f"  {i}. {model}")
                
        # Allow selection by number or direct input
        if suggested_models:
            self.console.print(f"\nВыберите модель:")
            choice = Prompt.ask("Введите номер модели или название", default="1")
            
            # Check if it's a number
            try:
                model_index = int(choice) - 1
                if 0 <= model_index < len(suggested_models):
                    model = suggested_models[model_index]
                else:
                    model = choice  # Use as direct model name
            except ValueError:
                model = choice  # Use as direct model name
        else:
            model = Prompt.ask("Введите название модели")
        
        # Save configuration
        set_ai_provider(provider, api_key, model)
        self.console.print(f"✅ AI провайдер {provider_name} настроен успешно!", style="green")
        
    def setup_workspace(self):
        """Setup workspace directory"""
        self.console.print("\n📁 Настройка рабочей директории", style="bold yellow")
        
        current_workspace = self.workspace.get_current_workspace()
        if current_workspace:
            self.console.print(f"Текущая рабочая директория: {current_workspace}")
            if not Confirm.ask("Хотите изменить рабочую директорию?"):
                return
                
        path = Prompt.ask("Введите путь к рабочей директории", default=".")
        
        if select_workspace(path):
            self.console.print("✅ Рабочая директория установлена успешно!", style="green")
        else:
            self.console.print("❌ Ошибка при установке рабочей директории", style="red")
            
    def initialize_agent(self):
        """Initialize the agent"""
        if not self.config.ai_provider:
            self.console.print("❌ Сначала настройте AI провайдера", style="red")
            return False
            
        if not self.workspace.get_current_workspace():
            self.console.print("❌ Сначала выберите рабочую директорию", style="red")
            return False
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                task = progress.add_task("Инициализация агента...", total=None)
                self.agent = create_agent(self.console)
                
            self.console.print("✅ Агент инициализирован успешно!", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Ошибка инициализации агента: {e}", style="red")
            return False
            
    def run_agent_chat(self):
        """Run interactive chat with the agent"""
        if not self.agent:
            self.console.print("❌ Сначала инициализируйте агента", style="red")
            return
            
        self.console.print("\n💬 Режим чата с агентом", style="bold green")
        self.console.print("Введите 'exit' или 'quit' для выхода\n")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("[bold cyan]Вы[/bold cyan]")
                
                if user_input.lower() in ['exit', 'quit', 'выход']:
                    self.console.print("👋 До свидания!", style="yellow")
                    break
                    
                if not user_input.strip():
                    continue
                    
                # Execute task
                result = self.agent.execute_task(user_input)
                
                if not result["success"]:
                    self.console.print(f"❌ Ошибка: {result['error']}", style="red")
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 Прервано пользователем", style="yellow")
                break
            except Exception as e:
                self.console.print(f"❌ Неожиданная ошибка: {e}", style="red")
                
    def show_tools_info(self):
        """Show information about available tools"""
        if not self.agent:
            self.console.print("❌ Сначала инициализируйте агента", style="red")
            return
            
        tools_table = Table(title="🔧 Доступные инструменты")
        tools_table.add_column("Название", style="bold cyan")
        tools_table.add_column("Описание", style="white")
        
        for tool in self.agent.tools:
            tools_table.add_row(tool.name, tool.description)
            
        self.console.print(tools_table)
        
    def show_main_menu(self):
        """Show main menu"""
        menu_table = Table(show_header=False, box=None, padding=(0, 1))
        menu_table.add_column("Option", style="bold cyan")
        menu_table.add_column("Description", style="white")
        
        menu_table.add_row("1", "Настроить AI провайдера")
        menu_table.add_row("2", "Выбрать рабочую директорию")
        menu_table.add_row("3", "Инициализировать агента")
        menu_table.add_row("4", "Запустить чат с агентом")
        menu_table.add_row("5", "Показать доступные инструменты")
        menu_table.add_row("6", "Показать статус системы")
        menu_table.add_row("0", "Выход")
        
        menu_panel = Panel(
            menu_table,
            title="📋 Главное меню",
            border_style="bright_green"
        )
        self.console.print(menu_panel)
        
    def run(self):
        """Run the main interface"""
        self.display_banner()
        
        while True:
            self.console.print()
            self.show_main_menu()
            
            choice = Prompt.ask("Выберите действие", choices=["0", "1", "2", "3", "4", "5", "6"])
            
            if choice == "0":
                self.console.print("👋 До свидания!", style="yellow")
                break
            elif choice == "1":
                self.setup_ai_provider()
            elif choice == "2":
                self.setup_workspace()
            elif choice == "3":
                self.initialize_agent()
            elif choice == "4":
                self.run_agent_chat()
            elif choice == "5":
                self.show_tools_info()
            elif choice == "6":
                self.display_status()


def run_agent_interface():
    """Entry point for the agent interface"""
    try:
        interface = AgentInterface()
        interface.run()
    except KeyboardInterrupt:
        print("\n👋 Прервано пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1) 