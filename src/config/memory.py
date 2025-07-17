"""
Memory and Session Configuration
Settings for conversation history, context retention, and learning
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple


@dataclass
class MemoryConfig:
    """Configuration for memory and session management"""
    
    # Session history settings
    max_conversation_history: int = 20  # Number of conversation turns to remember
    session_timeout_hours: int = 24     # Hours before session expires
    auto_save_session: bool = True      # Automatically save session data
    
    # Context retention settings
    max_context_files: int = 50         # Maximum files to track in context
    semantic_search_limit: int = 10     # Default semantic search results
    workflow_pattern_limit: int = 5     # Workflow patterns to track
    
    # Learning settings
    enable_pattern_learning: bool = True   # Learn user workflow patterns
    enable_preference_learning: bool = True # Learn user preferences
    min_pattern_frequency: int = 3         # Minimum occurrences to consider pattern
    
    # Performance settings
    compress_old_sessions: bool = True     # Compress sessions older than 7 days
    max_session_file_size_mb: int = 10     # Maximum session file size
    cleanup_interval_days: int = 30        # Clean up old sessions after N days


class MemoryPresets:
    """Predefined memory configuration presets"""
    
    @classmethod
    def minimal(cls) -> MemoryConfig:
        """Minimal memory usage - good for low-resource environments"""
        return MemoryConfig(
            max_conversation_history=5,
            session_timeout_hours=8,
            max_context_files=20,
            semantic_search_limit=5,
            workflow_pattern_limit=3,
            compress_old_sessions=True,
            max_session_file_size_mb=5
        )
    
    @classmethod
    def balanced(cls) -> MemoryConfig:
        """Balanced memory usage - default recommendation"""
        return MemoryConfig()  # Uses default values
    
    @classmethod
    def extensive(cls) -> MemoryConfig:
        """Extensive memory - maximum context retention"""
        return MemoryConfig(
            max_conversation_history=50,
            session_timeout_hours=72,
            max_context_files=200,
            semantic_search_limit=20,
            workflow_pattern_limit=10,
            max_session_file_size_mb=25,
            cleanup_interval_days=90
        )
    
    @classmethod
    def developer_intensive(cls) -> MemoryConfig:
        """For intensive development sessions"""
        return MemoryConfig(
            max_conversation_history=100,
            session_timeout_hours=48,
            max_context_files=500,
            semantic_search_limit=15,
            workflow_pattern_limit=15,
            enable_pattern_learning=True,
            enable_preference_learning=True,
            max_session_file_size_mb=50
        )


def get_memory_config_info() -> Dict[str, str]:
    """Get information about memory configuration options"""
    return {
        "max_conversation_history": "Количество диалогов для запоминания (5-100)",
        "session_timeout_hours": "Время жизни сессии в часах (1-168)",
        "max_context_files": "Максимум файлов для отслеживания (10-1000)",
        "semantic_search_limit": "Лимит результатов семантического поиска (3-50)",
        "workflow_pattern_limit": "Количество паттернов workflow (3-20)",
        "enable_pattern_learning": "Изучать паттерны работы пользователя",
        "enable_preference_learning": "Изучать предпочтения пользователя",
        "auto_save_session": "Автоматически сохранять сессию",
        "compress_old_sessions": "Сжимать старые сессии для экономии места"
    }


def validate_memory_config(config: MemoryConfig) -> Tuple[bool, Optional[str]]:
    """Validate memory configuration"""
    
    if config.max_conversation_history < 1 or config.max_conversation_history > 1000:
        return False, "max_conversation_history должно быть между 1 и 1000"
    
    if config.session_timeout_hours < 1 or config.session_timeout_hours > 168:
        return False, "session_timeout_hours должно быть между 1 и 168 (неделя)"
    
    if config.max_context_files < 1 or config.max_context_files > 10000:
        return False, "max_context_files должно быть между 1 и 10000"
    
    if config.semantic_search_limit < 1 or config.semantic_search_limit > 100:
        return False, "semantic_search_limit должно быть между 1 и 100"
    
    if config.max_session_file_size_mb < 1 or config.max_session_file_size_mb > 500:
        return False, "max_session_file_size_mb должно быть между 1 и 500"
    
    return True, None


def calculate_estimated_memory_usage(config: MemoryConfig) -> Dict[str, Any]:
    """Calculate estimated memory usage for given configuration"""
    
    # Rough estimates based on typical data sizes
    avg_turn_size_kb = 2  # Average conversation turn size
    avg_file_context_kb = 5  # Average file context size
    
    estimated_session_size_mb = (
        (config.max_conversation_history * avg_turn_size_kb) +
        (config.max_context_files * avg_file_context_kb)
    ) / 1024
    
    return {
        "estimated_session_size_mb": round(estimated_session_size_mb, 2),
        "estimated_daily_growth_mb": round(estimated_session_size_mb * 0.3, 2),
        "max_memory_per_workspace_mb": round(estimated_session_size_mb * 1.5, 2),
        "recommendation": _get_usage_recommendation(estimated_session_size_mb)
    }


def _get_usage_recommendation(estimated_mb: float) -> str:
    """Get usage recommendation based on estimated memory usage"""
    if estimated_mb < 1:
        return "Очень низкое потребление памяти - отлично для медленных систем"
    elif estimated_mb < 5:
        return "Низкое потребление памяти - хорошо для большинства систем"
    elif estimated_mb < 15:
        return "Умеренное потребление памяти - стандартная настройка"
    elif estimated_mb < 50:
        return "Высокое потребление памяти - для мощных систем"
    else:
        return "Очень высокое потребление памяти - только для серверов" 