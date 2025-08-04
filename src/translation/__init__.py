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
# - argos-translate Python package (or googletrans as fallback)
# - transformers Python package
# - sentencepiece Python package
# - torch Python package
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - Translator: Online translation using Ollama API     
# - OfflineTranslator: Offline translation using local models
# - translate_to_spanish: Convenience function for offline translation to Spanish
# - translate_text: General translation function
#----------------------------------------------------------------------------------------------------------------------------   

from .translator import Translator
from .offline_translator import OfflineTranslator, translate_to_spanish, TranslationError

# Try to import googletrans as fallback
try:
    from googletrans import Translator as GoogleTranslator
    GOOGLE_TRANSLATE_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATE_AVAILABLE = False

# Create a general translate_text function that the API expects
def translate_text(text: str, source_lang: str = "en", target_lang: str = "es") -> str:
    """
    General translation function that the API expects.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        Translated text
    """
    if not text or not text.strip():
        return ""
    
    # Try offline translation first
    try:
        if target_lang == "es":
            return translate_to_spanish(text, source_lang)
        else:
            # For other languages, use the offline translator
            translator = OfflineTranslator()
            return translator.translate_to_spanish(text, source_lang)  # Fallback to Spanish for now
    except Exception as e:
        # If offline translation fails, try Google Translate
        if GOOGLE_TRANSLATE_AVAILABLE:
            try:
                google_translator = GoogleTranslator()
                result = google_translator.translate(text, src=source_lang, dest=target_lang)
                return result.text
            except Exception as google_error:
                raise TranslationError(f"Translation failed: {e}. Google Translate also failed: {google_error}")
        else:
            raise TranslationError(f"Translation failed: {e}. No online fallback available.")

__all__ = [
    'Translator',
    'OfflineTranslator', 
    'translate_to_spanish',
    'translate_text',
    'TranslationError'
]

__version__ = "1.0.0" 