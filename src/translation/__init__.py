#!/usr/bin/env python3
"""
TalkBridge Translation -   Init   - Package Initialization
==========================================================

Inicialización del paquete

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- argos-translate (primary)
- deep-translator (fallback)
======================================================================
Functions:
- translate_text: General translation function that the API expects.
======================================================================
"""

from .translator import Translator
from .offline_translator import OfflineTranslator, translate_to_spanish, TranslationError

# Try to import argos-translate first, then deep-translator as fallback
try:
    import argostranslate.translate
    import argostranslate.package
    ARGOS_TRANSLATE_AVAILABLE = True
except ImportError:
    ARGOS_TRANSLATE_AVAILABLE = False

try:
    from deep_translator import GoogleTranslator as DeepGoogleTranslator
    DEEP_TRANSLATE_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATE_AVAILABLE = False

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
        # If offline translation fails, try Argos Translate
        if ARGOS_TRANSLATE_AVAILABLE:
            try:
                # Use argos-translate for translation
                translated_text = argostranslate.translate.translate(text, source_lang, target_lang)
                return translated_text
            except Exception as argos_error:
                # If argos fails, try Deep Translator
                if DEEP_TRANSLATE_AVAILABLE:
                    try:
                        deep_translator = DeepGoogleTranslator(source=source_lang, target=target_lang)
                        result = deep_translator.translate(text)
                        return result
                    except Exception as deep_error:
                        raise TranslationError(f"Translation failed: {e}. Argos failed: {argos_error}. Deep Translator failed: {deep_error}")
                else:
                    raise TranslationError(f"Translation failed: {e}. Argos Translate failed: {argos_error}. No other fallback available.")
        elif DEEP_TRANSLATE_AVAILABLE:
            try:
                deep_translator = DeepGoogleTranslator(source=source_lang, target=target_lang)
                result = deep_translator.translate(text)
                return result
            except Exception as deep_error:
                raise TranslationError(f"Translation failed: {e}. Deep Translator also failed: {deep_error}")
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