#!/usr/bin/env python3
"""
AI Punk - Autonomous AI Coding Assistant
Main entry point with workspace selection
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.workspace_selector import select_workspace_ui
from src.config import get_config, AIProvider, set_ai_provider
from src.workspace import get_current_workspace

console = Console()

def show_welcome():
    """Show welcome message"""
    welcome_text = Text()
    welcome_text.append("🎯 AI Punk", style="bold blue")
    welcome_text.append(" - Autonomous AI Coding Assistant\n\n", style="bold")
    welcome_text.append("Особенности:\n", style="bold")
    welcome_text.append("• 🔍 Полная прозрачность процесса мышления\n", style="green")
    welcome_text.append("• 🤖 Автономная работа без запросов разрешений\n", style="green")
    welcome_text.append("• 🛠️ 9 мощных инструментов для работы с кодом\n", style="green")
    welcome_text.append("• 🌍 Поддержка русского и английского языков\n", style="green")
    welcome_text.append("• 🏗️ Работа в выбранной пользователем директории\n", style="green")
    
    console.print(Panel(welcome_text, title="Добро пожаловать!", border_style="blue"))

def check_ai_provider():
    """Check if AI provider is configured"""
    config = get_config()
    
    if not config.ai_provider:
        console.print("\n⚠️  AI провайдер не настроен", style="yellow")
        console.print("Доступные провайдеры:")
        console.print("• Google Gemini (рекомендуется)")
        console.print("• OpenAI GPT")
        console.print("• Anthropic Claude")
        
        # TODO: Add AI provider configuration UI
        console.print("\n💡 Пока что настройте провайдер вручную в коде")
        return False
    
    console.print(f"✅ AI провайдер: {config.ai_provider.provider.value} ({config.ai_provider.model})", style="green")
    return True

def main():
    """Main application entry point"""
    try:
        # Show welcome
        show_welcome()
        
        # Select workspace
        console.print("\n" + "="*50)
        console.print("📂 Настройка рабочей директории", style="bold blue")
        console.print("="*50)
        
        if not select_workspace_ui():
            console.print("❌ Не удалось выбрать рабочую директорию", style="red")
            return 1
        
        # Check AI provider
        console.print("\n" + "="*50)
        console.print("🤖 Проверка AI провайдера", style="bold blue")
        console.print("="*50)
        
        if not check_ai_provider():
            console.print("❌ AI провайдер не настроен", style="red")
            return 1
        
        # Show ready status
        workspace = get_current_workspace()
        console.print(f"\n🎉 [bold green]AI Punk готов к работе![/bold green]")
        console.print(f"📁 Рабочая директория: [cyan]{workspace}[/cyan]")
        
        # TODO: Launch AI agent
        console.print("\n💻 Запуск AI агента...")
        console.print("⚠️  [yellow]Агент пока не реализован - это будет следующий шаг[/yellow]")
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n\n👋 До свидания!", style="blue")
        return 0
    except Exception as e:
        console.print(f"\n❌ Критическая ошибка: {e}", style="red")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 