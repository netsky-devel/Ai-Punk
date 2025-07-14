#!/usr/bin/env python3
"""
AI Punk - Autonomous AI Coding Assistant
Main entry point with agent interface
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.agent_interface import run_agent_interface

def main():
    """Main application entry point"""
    try:
        # Run agent interface
        run_agent_interface()
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Прервано пользователем")
        return 0
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 