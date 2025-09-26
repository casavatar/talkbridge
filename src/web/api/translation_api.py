#! /usr/bin/env python3
"""
TalkBridge UI - Translation Api
===============================

Translation API module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- Flask
======================================================================
Functions:
- __init__: Initialize the Translation API.
- translate_text: Translate text from source language to target language.
- get_supported_languages: Get dictionary of supported languages.
- get_language_name: Get language name from language code.
- validate_language_pair: Validate language pair for translation.
- detect_language: Detect the language of the given text.
- translate_batch: Translate multiple texts.
- get_translation_quality_score: Get a quality score for the translation.
- get_current_settings: Get current translation settings.
- set_default_languages: Set default source and target languages.
======================================================================
"""

import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any
import logging

try:
    from ...translation import translate_text
    TRANSLATION_AVAILABLE = True
except ImportError:
    logging.warning("Translation module not available")
    TRANSLATION_AVAILABLE = False

logger = logging.getLogger(__name__)

class TranslationAPI:
    """API interface for translation functionality."""
    
    def __init__(self):
        """Initialize the Translation API."""
        self.supported_languages = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }
        self.default_source = "en"
        self.default_target = "es"
    
    def translate_text(self, text: str, source_lang: str = "en", 
                     target_lang: str = "es") -> Optional[str]:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text or None if failed
        """
        try:
            if not TRANSLATION_AVAILABLE:
                logger.error("Translation module not available")
                return None
                
            if not text.strip():
                logger.warning("Empty text provided for translation")
                return None
            
            # Validate languages
            if source_lang not in self.supported_languages:
                logger.error(f"Unsupported source language: {source_lang}")
                return None
            
            if target_lang not in self.supported_languages:
                logger.error(f"Unsupported target language: {target_lang}")
                return None
            
            # Don't translate if source and target are the same
            if source_lang == target_lang:
                return text
            
            # Translate text
            translated = translate_text(text, source_lang, target_lang)
            
            if translated:
                logger.info(f"Translated text from {source_lang} to {target_lang}")
                return translated
            else:
                logger.error("Translation failed")
                return None
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return None
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get dictionary of supported languages.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return self.supported_languages.copy()
    
    def get_language_name(self, lang_code: str) -> Optional[str]:
        """
        Get language name from language code.
        
        Args:
            lang_code: Language code
            
        Returns:
            Language name or None if not found
        """
        return self.supported_languages.get(lang_code)
    
    def validate_language_pair(self, source_lang: str, target_lang: str) -> bool:
        """
        Validate language pair for translation.
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            True if language pair is valid
        """
        if source_lang not in self.supported_languages:
            return False
        
        if target_lang not in self.supported_languages:
            return False
        
        if source_lang == target_lang:
            return False
        
        return True
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code or None if failed
        """
        try:
            if not text.strip():
                return None
            
            # Simple language detection based on common words
            # This is a basic implementation - in production you'd use a proper language detection library
            
            text_lower = text.lower()
            
            # English common words
            english_words = ['the', 'and', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for']
            # Spanish common words
            spanish_words = ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo']
            # French common words
            french_words = ['le', 'la', 'de', 'et', 'est', 'un', 'une', 'dans', 'pour', 'avec', 'sur']
            # German common words
            german_words = ['der', 'die', 'das', 'und', 'ist', 'sind', 'in', 'auf', 'mit', 'von', 'zu']
            
            scores = {
                'en': sum(1 for word in english_words if word in text_lower),
                'es': sum(1 for word in spanish_words if word in text_lower),
                'fr': sum(1 for word in french_words if word in text_lower),
                'de': sum(1 for word in german_words if word in text_lower)
            }
            
            if max(scores.values()) > 0:
                detected_lang = max(scores, key=scores.get)
                logger.info(f"Detected language: {detected_lang}")
                return detected_lang
            else:
                logger.warning("Could not detect language")
                return None
                
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None
    
    def translate_batch(self, texts: list, source_lang: str = "en", 
                       target_lang: str = "es") -> list:
        """
        Translate multiple texts.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of translated texts
        """
        try:
            if not texts:
                return []
            
            translated_texts = []
            
            for text in texts:
                translated = self.translate_text(text, source_lang, target_lang)
                translated_texts.append(translated if translated else text)
            
            logger.info(f"Translated {len(texts)} texts")
            return translated_texts
            
        except Exception as e:
            logger.error(f"Batch translation failed: {e}")
            return texts  # Return original texts if translation fails
    
    def get_translation_quality_score(self, original: str, translated: str) -> float:
        """
        Get a quality score for the translation.
        
        Args:
            original: Original text
            translated: Translated text
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            if not original or not translated:
                return 0.0
            
            score = 0.0
            
            # Length comparison (translated text should be reasonable length)
            orig_len = len(original)
            trans_len = len(translated)
            
            if orig_len > 0:
                length_ratio = trans_len / orig_len
                if 0.5 <= length_ratio <= 2.0:
                    score += 0.3
                elif 0.3 <= length_ratio <= 3.0:
                    score += 0.2
                else:
                    score += 0.1
            
            # Character diversity (translated text should have reasonable character diversity)
            unique_chars = len(set(translated))
            if unique_chars > len(translated) * 0.3:
                score += 0.2
            
            # Word count (translated text should have reasonable word count)
            word_count = len(translated.split())
            if word_count >= 1:
                score += 0.2
            
            # Punctuation preservation
            orig_punct = sum(1 for c in original if c in '.,!?;:')
            trans_punct = sum(1 for c in translated if c in '.,!?;:')
            if abs(orig_punct - trans_punct) <= 2:
                score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Failed to calculate translation quality: {e}")
            return 0.5
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current translation settings.
        
        Returns:
            Dictionary containing current settings
        """
        return {
            "default_source": self.default_source,
            "default_target": self.default_target,
            "supported_languages": self.supported_languages,
            "total_languages": len(self.supported_languages)
        }
    
    def set_default_languages(self, source_lang: str, target_lang: str) -> bool:
        """
        Set default source and target languages.
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            True if languages set successfully
        """
        if self.validate_language_pair(source_lang, target_lang):
            self.default_source = source_lang
            self.default_target = target_lang
            logger.info(f"Set default languages: {source_lang} -> {target_lang}")
            return True
        else:
            logger.error(f"Invalid language pair: {source_lang} -> {target_lang}")
            return False 