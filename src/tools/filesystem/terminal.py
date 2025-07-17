"""
Terminal Tool
Execute shell commands with security and timeout
"""

import os
import subprocess
from typing import Dict, Any, Optional

from .security import PathSecurity


class TerminalTool:
    """Инструмент для выполнения команд терминала"""
    
    def __init__(self, root_directory: str):
        self.security = PathSecurity(root_directory)
    
    def execute(self, command: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
        """Выполняет команду в терминале"""
        
        # Определение рабочей директории
        if working_dir:
            error = self.security.validate_path(working_dir)
            if error:
                return {"success": False, "error": error}
            cwd = self.security.resolve_path(working_dir)
        else:
            cwd = self.security.root_directory
        
        if not os.path.exists(cwd):
            return {"success": False, "error": f"Рабочая директория не существует: {working_dir or '.'}"} 
        
        try:
            # Выполнение команды
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": True,
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "working_dir": self.security.make_relative(cwd)
            }
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Команда превысила лимит времени выполнения (60 сек)"}
        except Exception as e:
            return {"success": False, "error": f"Ошибка при выполнении команды: {str(e)}"} 