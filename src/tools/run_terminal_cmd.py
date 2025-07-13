"""
AI Punk Run Terminal Command Tool
Executes terminal commands in workspace with output capture
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .base import BaseTool

console = Console()

class RunTerminalCmdTool(BaseTool):
    """Tool for executing terminal commands"""
    
    def __init__(self):
        super().__init__(
            name="run_terminal_cmd",
            description="PROPOSE a command to run on behalf of the user. If you have this tool, note that you DO have the ability to run commands directly on the USER's system. Note that the user may have to approve the command before it is executed."
        )
    
    def execute(self, command: str, timeout: int = 30, show_output: bool = True) -> Dict[str, Any]:
        """
        Execute a terminal command
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            show_output: Whether to display command output
            
        Returns:
            Dict with success status, message, and command output
        """
        try:
            # Check workspace
            workspace = self._check_workspace()
            
            # Show command being executed
            console.print(f"💻 [bold blue]Выполнение команды:[/bold blue] [cyan]{command}[/cyan]")
            console.print(f"📁 [dim]Рабочая директория: {workspace}[/dim]")
            
            # Change to workspace directory
            original_cwd = os.getcwd()
            os.chdir(workspace)
            
            try:
                # Execute command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=workspace
                )
                
                # Get output
                stdout = result.stdout.strip() if result.stdout else ""
                stderr = result.stderr.strip() if result.stderr else ""
                return_code = result.returncode
                
                # Display output
                if show_output:
                    self._display_output(command, stdout, stderr, return_code)
                
                # Return result
                if return_code == 0:
                    return self._format_success(
                        f"Команда выполнена успешно (код: {return_code})",
                        {
                            "command": command,
                            "return_code": return_code,
                            "stdout": stdout,
                            "stderr": stderr,
                            "working_directory": str(workspace)
                        }
                    )
                else:
                    return self._format_error(
                        f"Команда завершилась с ошибкой (код: {return_code})",
                        {
                            "command": command,
                            "return_code": return_code,
                            "stdout": stdout,
                            "stderr": stderr,
                            "working_directory": str(workspace)
                        }
                    )
                    
            except subprocess.TimeoutExpired:
                return self._format_error(f"Команда превысила таймаут ({timeout}s)")
            except subprocess.CalledProcessError as e:
                return self._format_error(f"Ошибка выполнения команды: {e}")
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
                
        except Exception as e:
            return self._format_error(f"Ошибка при выполнении команды: {str(e)}")
    
    def _display_output(self, command: str, stdout: str, stderr: str, return_code: int):
        """Display command output in formatted panels"""
        
        # Command info
        status_color = "green" if return_code == 0 else "red"
        status_text = "✅ Успешно" if return_code == 0 else f"❌ Ошибка (код: {return_code})"
        
        console.print(f"\n{status_text}", style=status_color)
        
        # Standard output
        if stdout:
            console.print(Panel(
                stdout,
                title="📤 Вывод команды",
                border_style="green"
            ))
        
        # Standard error
        if stderr:
            console.print(Panel(
                stderr,
                title="⚠️ Ошибки",
                border_style="red"
            ))
        
        # Empty output
        if not stdout and not stderr:
            console.print("📭 [dim]Команда не вернула вывод[/dim]")
    
    def run_silent(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run command without displaying output"""
        return self.execute(command=command, timeout=timeout, show_output=False)
    
    def run_with_timeout(self, command: str, timeout: int) -> Dict[str, Any]:
        """Run command with custom timeout"""
        return self.execute(command=command, timeout=timeout)
    
    def get_langchain_tool(self):
        """Get LangChain tool representation"""
        from langchain.tools import Tool
        
        def tool_func(command: str, timeout: int = 30):
            return self.run(command=command, timeout=timeout)
        
        return Tool(
            name=self.name,
            description=self.description,
            func=tool_func
        )

# Create tool instance
run_terminal_cmd_tool = RunTerminalCmdTool() 