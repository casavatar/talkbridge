#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: Translation Module
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - argos-translate Python package
# - transformers Python package
# - sentencepiece Python package
# - torch Python package
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - Translator: Online translation using Ollama API     
# - OfflineTranslator: Offline translation using local models
# - translate_to_spanish: Convenience function for offline translation to Spanish
#----------------------------------------------------------------------------------------------------------------------------   

from .translator import Translator
from .offline_translator import OfflineTranslator, translate_to_spanish, TranslationError

__all__ = [
    'Translator',
    'OfflineTranslator', 
    'translate_to_spanish',
    'TranslationError'
]

__version__ = "1.0.0" 