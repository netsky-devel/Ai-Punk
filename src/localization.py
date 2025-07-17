"""
Legacy Localization Import
Re-exports from organized localization package for backward compatibility
"""

from .localization import (
    Language,
    Localization,
    get_localization,
    t,
    set_language_from_user_input
)

# Legacy exports for backward compatibility
__all__ = [
    'Language',
    'Localization', 
    'get_localization',
    't',
    'set_language_from_user_input'
] 