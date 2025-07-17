"""
AI Punk Workspace Selector
Simple interface for selecting project directories
"""

import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..workspace.manager import WorkspaceManager
from ..config.manager import ConfigManager

console = Console()

class WorkspaceSelector:
    """Simple interface for workspace selection"""
    
    def __init__(self):
        self.workspace_manager = WorkspaceManager()
    
    def show_current_workspace(self):
        """Display current workspace information"""
        current = self.workspace_manager.get_current_workspace()
        
        if not current:
            console.print("❌ Рабочая директория не выбрана", style="red")
            return
        
        info = self.workspace_manager.get_workspace_info()
        
        if info["status"] == "active":
            table = Table(title="Текущая рабочая директория")
            table.add_column("Параметр", style="cyan")
            table.add_column("Значение", style="green")
            
            table.add_row("Путь", str(info["path"]))
            table.add_row("Файлов", str(info["files_count"]))
            table.add_row("Папок", str(info["dirs_count"]))
            table.add_row("Размер", self._format_size(info["total_size"]))
            
            console.print(table)
        else:
            console.print(f"❌ Ошибка с рабочей директорией: {info.get('error', 'Неизвестная ошибка')}", style="red")
    
    def select_workspace_interactive(self) -> bool:
        """Interactive workspace selection"""
        console.print(Panel.fit(
            "🎯 [bold blue]Выбор рабочей директории[/bold blue]\n\n"
            "Выберите папку проекта, в которой будет работать AI агент.\n"
            "Агент сможет читать, создавать и редактировать файлы только в этой папке.",
            title="AI Punk Workspace"
        ))
        
        # Show current workspace if exists
        current = self.workspace_manager.get_current_workspace()
        if current:
            console.print(f"\n📁 Текущая рабочая директория: [green]{current}[/green]")
            
            if Confirm.ask("Хотите изменить рабочую директорию?"):
                pass
            else:
                return True
        
        # Get new workspace path
        while True:
            console.print("\n💡 Примеры путей:")
            console.print("   • C:\\Users\\Username\\Projects\\MyProject")
            console.print("   • /home/user/projects/myproject")
            console.print("   • . (текущая директория)")
            console.print("   • .. (родительская директория)")
            
            path = Prompt.ask("\n📂 Введите путь к рабочей директории")
            
            if not path:
                console.print("❌ Путь не может быть пустым", style="red")
                continue
            
            # Expand path
            if path == ".":
                path = os.getcwd()
            elif path == "..":
                path = str(Path.cwd().parent)
            else:
                path = os.path.expanduser(path)
            
            # Try to select workspace
                            if self.workspace_manager.select_workspace(path):
                self.show_current_workspace()
                return True
            else:
                if not Confirm.ask("Попробовать другой путь?"):
                    return False
    
    def quick_select_common_paths(self) -> bool:
        """Quick selection from common paths"""
        console.print("\n🚀 Быстрый выбор:")
        
        options = [
            (".", "Текущая директория", os.getcwd()),
            ("..", "Родительская директория", str(Path.cwd().parent)),
            ("home", "Домашняя директория", str(Path.home())),
            ("desktop", "Рабочий стол", str(Path.home() / "Desktop")),
            ("documents", "Документы", str(Path.home() / "Documents")),
        ]
        
        table = Table()
        table.add_column("№", style="cyan")
        table.add_column("Описание", style="green")
        table.add_column("Путь", style="yellow")
        
        for i, (key, desc, path) in enumerate(options, 1):
            table.add_row(str(i), desc, path)
        
        console.print(table)
        
        choice = Prompt.ask(
            "Выберите опцию (1-5) или нажмите Enter для ручного ввода",
            default=""
        )
        
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            selected_path = options[int(choice) - 1][2]
            return self.workspace_manager.select_workspace(selected_path)
        
        return False
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

def select_workspace_ui() -> bool:
    """Main function for workspace selection UI"""
    selector = WorkspaceSelector()
    
    # Show current workspace first
    selector.show_current_workspace()
    
    # If no workspace or user wants to change
    current = get_current_workspace()
    if not current:
        console.print("\n⚠️  Необходимо выбрать рабочую директорию", style="yellow")
        return selector.select_workspace_interactive()
    
    return True

if __name__ == "__main__":
    select_workspace_ui() 