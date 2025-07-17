"""
Localization Core
Main localization system with language detection and message handling
"""

import re
from typing import Dict, Any

from .models import Language
from .messages.english import ENGLISH_MESSAGES
from .messages.russian import RUSSIAN_MESSAGES


class Localization:
    """Localization system with automatic language detection"""
    
    def __init__(self):
        self.current_language = Language.ENGLISH
        self.messages = {
            Language.ENGLISH: ENGLISH_MESSAGES,
            Language.RUSSIAN: RUSSIAN_MESSAGES
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