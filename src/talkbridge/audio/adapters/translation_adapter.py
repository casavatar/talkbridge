"""
Translation Adapter for TalkBridge

Wraps the existing Translator class to conform to the TranslationPort interface.
"""

import logging
import asyncio
import time
from typing import List

from ..ports import TranslationPort, TranslationResult
from ...utils.language_utils import get_supported_languages

try:
    from ...translation.translator import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

class TranslationAdapter:
    """Adapter that wraps Translator to implement TranslationPort."""
    
    def __init__(self, service: str = "google"):
        """Initialize the translation adapter.
        
        Args:
            service: Translation service to use ("google", "deepl", etc.)
        """
        self.logger = logging.getLogger("talkbridge.audio.translation_adapter")
        
        if not TRANSLATOR_AVAILABLE:
            raise ImportError("Translator module not available")
        
        try:
            self.translator = Translator(service=service)
            self._service = service
            self._supported_languages = get_supported_languages('translation')
            self.logger.info(f"Initialized translation adapter with service: {service}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Translator: {e}")
            raise
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text from source to target language."""
        start_time = time.time()
        
        try:
            # Use Translator's translate method
            result = self.translator.translate(
                text=text,
                source_language=source_lang,
                target_language=target_lang
            )
            
            processing_time = time.time() - start_time
            
            # Handle different result formats
            if isinstance(result, dict):
                translated_text = result.get('translated_text', result.get('text', ''))
                detected_lang = result.get('detected_language', source_lang)
                confidence = result.get('confidence', 1.0)
            elif isinstance(result, str):
                translated_text = result
                detected_lang = source_lang
                confidence = 1.0
            else:
                translated_text = str(result)
                detected_lang = source_lang
                confidence = 1.0
            
            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=detected_lang,
                target_language=target_lang,
                confidence=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            processing_time = time.time() - start_time
            
            return TranslationResult(
                original_text=text,
                translated_text=text,  # Return original text on failure
                source_language=source_lang,
                target_language=target_lang,
                confidence=0.0,
                processing_time=processing_time
            )
    
    async def translate_async(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text asynchronously."""
        # Run translation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.translate, text, source_lang, target_lang)
    
    def detect_language(self, text: str) -> str:
        """Detect the language of given text."""
        try:
            if hasattr(self.translator, 'detect_language'):
                result = self.translator.detect_language(text)
                
                # Handle different result formats
                if isinstance(result, dict):
                    return result.get('language', result.get('lang', 'unknown'))
                elif isinstance(result, str):
                    return result
                else:
                    return 'unknown'
            else:
                # Fallback: try to use translation with auto-detect
                dummy_translation = self.translator.translate(
                    text=text,
                    source_language='auto',
                    target_language='en'
                )
                
                if isinstance(dummy_translation, dict):
                    return dummy_translation.get('detected_language', 'unknown')
                else:
                    return 'unknown'
                    
        except Exception as e:
            self.logger.error(f"Language detection failed: {e}")
            return 'unknown'
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self._supported_languages.copy()
    
    def is_ready(self) -> bool:
        """Check if the translation service is ready."""
        try:
            # Test with a simple translation
            test_result = self.translate("hello", "en", "es")
            return test_result.confidence > 0
        except Exception:
            return False