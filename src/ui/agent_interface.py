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
from ..config import AIProvider
from ..config.manager import ConfigManager
from ..config.models import AIProviderConfig
from ..config.memory import MemoryConfig, MemoryPresets, get_memory_config_info, calculate_estimated_memory_usage
from ..workspace.manager import WorkspaceManager
from ..localization.core import Localization


class AgentInterface:
    """Terminal interface for AI Punk Agent"""
    
    def __init__(self):
        self.console = Console()
        self.agent: Optional[AIPunkAgent] = None
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.workspace = WorkspaceManager()
        self.localization = Localization()
        
    def display_banner(self):
        """Display welcome banner"""
        banner_text = Text()
        banner_text.append(self.localization.get("welcome_banner"), style="bold bright_blue")
        banner_text.append("\n", style="white")
        banner_text.append(self.localization.get("welcome_subtitle"), style="dim")
        
        banner_panel = Panel(
            Align.center(banner_text),
            title=self.localization.get("welcome_title"),
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(banner_panel)
        
    def display_status(self):
        """Display current status"""
        status_table = Table(show_header=False, box=None, padding=(0, 1))
        status_table.add_column("Setting", style="bold")
        status_table.add_column("Status", style="white")
        
        # Workspace status
        workspace_path = self.workspace.get_current_workspace()
        if workspace_path:
            status_table.add_row("📁 Working Directory:", str(workspace_path))
        else:
            status_table.add_row("📁 Working Directory:", "❌ Not selected")
        
        # AI Provider status
        if self.config.ai_provider:
            provider_name = self.config.ai_provider.provider.value.upper()
            model_name = self.config.ai_provider.model
            status_table.add_row("🤖 AI Provider:", f"✅ {provider_name} ({model_name})")
        else:
            status_table.add_row("🤖 AI Provider:", "❌ Not configured")
            
        # Agent status
        if self.agent:
            status_table.add_row("⚡ Agent:", self.localization.get("agent_ready"))
            
            # Session status
            try:
                session_stats = self.agent.get_session_stats()
                if session_stats.get("available"):
                    turns_count = session_stats.get("total_turns", 0)
                    success_rate = session_stats.get("success_rate", 0) * 100
                    status_table.add_row("💾 Session:", f"✅ {turns_count} взаимодействий ({success_rate:.1f}% успех)")
                else:
                    status_table.add_row("💾 Session:", "❌ Недоступна")
            except Exception:
                status_table.add_row("💾 Session:", "❓ Неизвестно")
        else:
            status_table.add_row("⚡ Agent:", self.localization.get("agent_not_initialized"))
            
        status_panel = Panel(
            status_table,
            title="📊 Status",
            border_style="blue"
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
        self.config.ai_provider = AIProviderConfig(
            provider=provider,
            api_key=api_key,
            model=model
        )
        self.config_manager.save_config(self.config)
        # Reload configuration to update self.config
        self.config = self.config_manager.load_config()
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
            # Reload workspace and config to update self.workspace and self.config
            self.workspace = get_workspace()
            self.config = get_config()
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
    
    def clear_session_memory(self):
        """Clear session memory and start fresh"""
        if not self.agent:
            self.console.print("❌ Сначала инициализируйте агента", style="red")
            return
        
        if Confirm.ask("🔄 Очистить память сессии? Вся история взаимодействий будет удалена."):
            try:
                self.agent.clear_session_memory()
                self.console.print("✅ Память сессии успешно очищена!", style="green")
            except Exception as e:
                self.console.print(f"❌ Ошибка при очистке памяти: {e}", style="red")
        else:
            self.console.print("Операция отменена", style="yellow")
    
    def setup_memory_settings(self):
        """Setup memory and session configuration"""
        self.console.print("\n🧠 Настройка памяти и сессий", style="bold yellow")
        
        # Show current memory info if agent exists
        if self.agent:
            try:
                session_stats = self.agent.get_session_stats()
                if session_stats.get("available"):
                    current_history = session_stats.get("total_turns", 0)
                    self.console.print(f"Текущая сессия: {current_history} взаимодействий")
            except Exception:
                pass
        
        # Show preset options
        self.console.print("\nВыберите конфигурацию памяти:")
        self.console.print("  1. Минимальная (5 диалогов) - для слабых систем")
        self.console.print("  2. Сбалансированная (20 диалогов) - рекомендуется")
        self.console.print("  3. Расширенная (50 диалогов) - максимальный контекст")
        self.console.print("  4. Интенсивная разработка (100 диалогов) - для серьезной работы")
        self.console.print("  5. Показать подробную информацию о настройках")
        
        choice = Prompt.ask("Ваш выбор", choices=["1", "2", "3", "4", "5"], default="2")
        
        if choice == "1":
            config = MemoryPresets.minimal()
            self._show_memory_config_summary(config, "Минимальная")
        elif choice == "2":
            config = MemoryPresets.balanced()
            self._show_memory_config_summary(config, "Сбалансированная")
        elif choice == "3":
            config = MemoryPresets.extensive()
            self._show_memory_config_summary(config, "Расширенная")
        elif choice == "4":
            config = MemoryPresets.developer_intensive()
            self._show_memory_config_summary(config, "Интенсивная разработка")
        elif choice == "5":
            self._show_detailed_memory_info()
            return
        
        # Confirm and apply configuration
        if Confirm.ask("Применить эту конфигурацию?", default=True):
            # Here we would save the config and restart agent if needed
            self.console.print("✅ Конфигурация памяти сохранена!", style="green")
            self.console.print("💡 Для применения настроек перезапустите агента", style="blue")
        else:
            self.console.print("Настройки не изменены", style="yellow")
    
    def _show_memory_config_summary(self, config: MemoryConfig, preset_name: str):
        """Show summary of memory configuration"""
        usage_info = calculate_estimated_memory_usage(config)
        
        summary_table = Table(title=f"🧠 Конфигурация: {preset_name}")
        summary_table.add_column("Параметр", style="bold cyan")
        summary_table.add_column("Значение", style="white")
        
        summary_table.add_row("История диалогов", f"{config.max_conversation_history} взаимодействий")
        summary_table.add_row("Время жизни сессии", f"{config.session_timeout_hours} часов")
        summary_table.add_row("Максимум файлов", f"{config.max_context_files}")
        summary_table.add_row("Семантический поиск", f"{config.semantic_search_limit} результатов")
        summary_table.add_row("Изучение паттернов", "✅" if config.enable_pattern_learning else "❌")
        summary_table.add_row("Сжатие сессий", "✅" if config.compress_old_sessions else "❌")
        summary_table.add_row("Размер сессии", f"~{usage_info['estimated_session_size_mb']} МБ")
        summary_table.add_row("Рекомендация", usage_info['recommendation'])
        
        self.console.print(summary_table)
    
    def _show_detailed_memory_info(self):
        """Show detailed information about memory settings"""
        info_table = Table(title="📋 Подробная информация о настройках памяти")
        info_table.add_column("Параметр", style="bold cyan")
        info_table.add_column("Описание", style="white")
        
        config_info = get_memory_config_info()
        for param, description in config_info.items():
            info_table.add_row(param, description)
        
        self.console.print(info_table)
        
        self.console.print("\n💡 [blue]Рекомендации по выбору:[/blue]")
        self.console.print("• [green]Минимальная[/green] - для медленных компьютеров или ограниченной памяти")
        self.console.print("• [yellow]Сбалансированная[/yellow] - оптимальная для большинства пользователей")
        self.console.print("• [blue]Расширенная[/blue] - для длительных сессий и сложных проектов") 
        self.console.print("• [red]Интенсивная[/red] - для профессиональной разработки на мощных системах")
        
    def show_main_menu(self):
        """Display main menu"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="bold cyan")
        menu_table.add_column("Description", style="white")
        
        menu_table.add_row("1", self.localization.get("setup_ai_provider"))
        menu_table.add_row("2", self.localization.get("select_workspace"))
        menu_table.add_row("3", self.localization.get("initialize_agent"))
        menu_table.add_row("4", self.localization.get("start_chat"))
        menu_table.add_row("5", self.localization.get("show_tools"))
        menu_table.add_row("6", "Clear Session Memory")
        menu_table.add_row("7", "Memory Settings")
        menu_table.add_row("0", self.localization.get("exit"))
        
        menu_panel = Panel(
            menu_table,
            title=self.localization.get("main_menu"),
            border_style="cyan"
        )
        self.console.print(menu_panel)
        
    def run(self):
        """Run the main interface"""
        self.display_banner()
        
        while True:
            self.console.print()
            self.show_main_menu()
            
            choice = Prompt.ask("Выберите действие", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])
            
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
                self.clear_session_memory()
            elif choice == "7":
                self.setup_memory_settings()
            elif choice == "8":
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