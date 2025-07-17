"""
Russian Language Messages
Complete set of UI messages in Russian
"""

RUSSIAN_MESSAGES = {
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