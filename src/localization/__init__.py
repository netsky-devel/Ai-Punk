"""
AI Punk Localization System
Automatic language detection and UI message translation
"""

from .models import Language
from .core import Localization

# Export main components
__all__ = [
    'Language',
    'Localization',
    'get_localization',
    't',
    'set_language_from_user_input'
]

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