"""
AI Punk Localization System
Provides automatic language detection and UI message translation
"""

import re
from typing import Dict, Any, Optional
from enum import Enum

class Language(Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"

class Localization:
    """Localization system with automatic language detection"""
    
    def __init__(self):
        self.current_language = Language.ENGLISH
        self.messages = {
            Language.ENGLISH: {
                # Agent thinking and actions
                "agent_thinking": "🧠 Agent Thinking (Step {})",
                "agent_action": "⚡ Agent Action",
                "tool_label": "🔧 Tool:",
                "input_label": "📝 Input:",
                "executing": "⏳ Executing...",
                "execution_result": "✅ Execution Result (in {:.2f}s)",
                "execution_summary": "📈 Execution Summary",
                "total_steps": "📊 Total steps:",
                "execution_time": "⏱️ Execution time:",
                "status": "🎯 Status:",
                "status_completed": "Completed successfully",
                "status_failed": "Failed with errors",
                
                # Workspace messages
                "workspace_set": "✅ Working directory set: {}",
                "workspace_not_selected": "Working directory not selected",
                "workspace_not_exists": "❌ Path does not exist: {}",
                "workspace_not_directory": "❌ Path is not a directory: {}",
                "workspace_error": "❌ Error selecting working directory: {}",
                "current_workspace": "📁 Current working directory: {}",
                "workspace_selection_error": "❌ Working directory selection error",
                
                # UI Interface
                "welcome_banner": "🤖 AI Punk Agent",
                "welcome_subtitle": "Autonomous Software Development Assistant",
                "welcome_title": "Welcome",
                "main_menu": "📋 Main Menu",
                "setup_ai_provider": "Setup AI Provider",
                "select_workspace": "Select Working Directory",
                "initialize_agent": "Initialize Agent",
                "start_chat": "Start Chat with Agent",
                "show_tools": "Show Available Tools",
                "exit": "Exit",
                
                # Agent status
                "agent_ready": "✅ Ready to work",
                "agent_not_initialized": "❌ Not initialized",
                "agent_initializing": "Initializing agent...",
                "agent_initialized": "✅ Agent initialized successfully!",
                "agent_init_error": "❌ Agent initialization error: {}",
                "agent_not_ready": "❌ Initialize agent first",
                "chat_mode": "💬 Chat mode with agent",
                
                # Error messages
                "error_tool_execution": "❌ Tool execution error: {}",
                "error_invalid_json": "❌ Invalid JSON format",
                "error_file_not_found": "❌ File not found: {}",
                "error_directory_not_exists": "❌ Directory does not exist: {}",
                
                # Tool descriptions
                "tool_error": "❌ Error:",
                "tool_success": "✅ Success:",
                "files_found": "📊 Total elements: {}",
                "content_directory": "📁 Directory contents: {}",
                "file_modified": "✅ File {} modified. Replaced {} occurrences.",
                "file_created": "✅ File {} created.",
                "command_executed": "💻 Command: {}",
                "return_code": "📊 Return code: {}",
                "command_output": "📤 Output:",
                "command_errors": "⚠️ Errors:",
            },
            
            Language.RUSSIAN: {
                # Agent thinking and actions
                "agent_thinking": "🧠 Мышление агента (Шаг {})",
                "agent_action": "⚡ Действие агента",
                "tool_label": "🔧 Инструмент:",
                "input_label": "📝 Ввод:",
                "executing": "⏳ Выполняется...",
                "execution_result": "✅ Результат выполнения (за {:.2f}с)",
                "execution_summary": "📈 Сводка выполнения",
                "total_steps": "📊 Всего шагов:",
                "execution_time": "⏱️ Время выполнения:",
                "status": "🎯 Статус:",
                "status_completed": "Завершено успешно",
                "status_failed": "Завершено с ошибками",
                
                # Workspace messages
                "workspace_set": "✅ Рабочая директория установлена: {}",
                "workspace_not_selected": "Рабочая директория не выбрана",
                "workspace_not_exists": "❌ Путь не существует: {}",
                "workspace_not_directory": "❌ Путь не является директорией: {}",
                "workspace_error": "❌ Ошибка при выборе рабочей директории: {}",
                "current_workspace": "📁 Текущая рабочая директория: {}",
                "workspace_selection_error": "❌ Ошибка выбора рабочей директории",
                
                # UI Interface
                "welcome_banner": "🤖 AI Punk Agent",
                "welcome_subtitle": "Автономный помощник для разработки ПО",
                "welcome_title": "Добро пожаловать",
                "main_menu": "📋 Главное меню",
                "setup_ai_provider": "Настроить AI провайдера",
                "select_workspace": "Выбрать рабочую директорию",
                "initialize_agent": "Инициализировать агента",
                "start_chat": "Запустить чат с агентом",
                "show_tools": "Показать доступные инструменты",
                "exit": "Выход",
                
                # Agent status
                "agent_ready": "✅ Готов к работе",
                "agent_not_initialized": "❌ Не инициализирован",
                "agent_initializing": "Инициализация агента...",
                "agent_initialized": "✅ Агент инициализирован успешно!",
                "agent_init_error": "❌ Ошибка инициализации агента: {}",
                "agent_not_ready": "❌ Сначала инициализируйте агента",
                "chat_mode": "💬 Режим чата с агентом",
                
                # Error messages
                "error_tool_execution": "❌ Ошибка выполнения инструмента: {}",
                "error_invalid_json": "❌ Неверный JSON формат",
                "error_file_not_found": "❌ Файл не найден: {}",
                "error_directory_not_exists": "❌ Директория не существует: {}",
                
                # Tool descriptions
                "tool_error": "❌ Ошибка:",
                "tool_success": "✅ Успех:",
                "files_found": "📊 Всего элементов: {}",
                "content_directory": "📁 Содержимое директории: {}",
                "file_modified": "✅ Файл {} изменен. Заменено {} вхождений.",
                "file_created": "✅ Файл {} создан.",
                "command_executed": "💻 Команда: {}",
                "return_code": "📊 Код возврата: {}",
                "command_output": "📤 Вывод:",
                "command_errors": "⚠️ Ошибки:",
            }
        }
    
    def detect_language(self, text: str) -> Language:
        """Detect language from user input"""
        if not text:
            return self.current_language
            
        # Count Cyrillic characters
        cyrillic_chars = len(re.findall(r'[а-яё]', text.lower()))
        # Count Latin characters  
        latin_chars = len(re.findall(r'[a-z]', text.lower()))
        
        # If more than 30% Cyrillic characters, consider it Russian
        total_letters = cyrillic_chars + latin_chars
        if total_letters > 0 and cyrillic_chars / total_letters > 0.3:
            return Language.RUSSIAN
        else:
            return Language.ENGLISH
    
    def set_language(self, language: Language):
        """Set current language"""
        self.current_language = language
    
    def set_language_from_text(self, text: str):
        """Set language based on text analysis"""
        detected = self.detect_language(text)
        self.set_language(detected)
    
    def get(self, key: str, *args, **kwargs) -> str:
        """Get localized message"""
        messages = self.messages.get(self.current_language, self.messages[Language.ENGLISH])
        message = messages.get(key, key)
        
        # Format message with arguments
        try:
            if args or kwargs:
                return message.format(*args, **kwargs)
            return message
        except (IndexError, KeyError, ValueError):
            return message
    
    def get_current_language(self) -> Language:
        """Get current language"""
        return self.current_language

# Global localization instance
_localization = Localization()

def get_localization() -> Localization:
    """Get global localization instance"""
    return _localization

def t(key: str, *args, **kwargs) -> str:
    """Shorthand for getting localized message"""
    return _localization.get(key, *args, **kwargs)

def set_language_from_user_input(text: str):
    """Set language based on user input"""
    _localization.set_language_from_text(text) 