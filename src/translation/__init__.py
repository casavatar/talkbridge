"""
Translation Module

This module provides both online and offline translation capabilities.

Available classes:
- Translator: Online translation using Ollama API
- OfflineTranslator: Offline translation using local models

Available functions:
- translate_to_spanish: Convenience function for offline translation to Spanish
"""

from .translator import Translator
from .offline_translator import OfflineTranslator, translate_to_spanish, TranslationError

__all__ = [
    'Translator',
    'OfflineTranslator', 
    'translate_to_spanish',
    'TranslationError'
]

__version__ = "1.0.0" 