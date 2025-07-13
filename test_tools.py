#!/usr/bin/env python3
"""
Test script for AI Punk tools
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tools.list_dir import list_dir_tool
from src.tools.read_file import read_file_tool
from src.tools.edit_file import edit_file_tool
from src.workspace import select_workspace

def test_tools():
    """Test all implemented tools"""
    print("🧪 Тестирование инструментов AI Punk")
    print("=" * 50)
    
    # Set workspace to current directory
    current_dir = str(Path.cwd())
    if not select_workspace(current_dir):
        print("❌ Не удалось установить рабочую директорию")
        return
    
    print("\n1. Тест list_dir:")
    print("-" * 20)
    result = list_dir_tool.run(dir_path=".")
    print(f"Результат: {result['success']}")
    
    print("\n2. Тест read_file:")
    print("-" * 20)
    result = read_file_tool.run(path="README.md", start_line=1, end_line=10)
    print(f"Результат: {result['success']}")
    
    print("\n3. Тест edit_file (создание):")
    print("-" * 30)
    test_content = """# Test File
This is a test file created by AI Punk tools.

## Features
- File creation
- Syntax highlighting
- Backup support
"""
    result = edit_file_tool.run(path="test_output.md", content=test_content, create_backup=False)
    print(f"Результат: {result['success']}")
    
    print("\n4. Тест read_file (созданный файл):")
    print("-" * 35)
    result = read_file_tool.run(path="test_output.md")
    print(f"Результат: {result['success']}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_tools() 