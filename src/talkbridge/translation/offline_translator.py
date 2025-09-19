#!/usr/bin/env python3
"""
TalkBridge Translation - Offline Translator
===========================================

Offline translator module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- googletrans
======================================================================
Functions:
- translate_to_spanish: Convenience function to translate text to Spanish.
- __init__: Initialize the offline translator.
- _download_argos_model: Download argos-translate model for the specified language pair.
- _load_argos_model: Load or download argos-translate model.
- _load_hf_model: Load HuggingFace MarianMT model.
- translate_to_spanish: Translate text to Spanish.
- _translate_with_argos: Translate using argos-translate.
- _translate_with_hf: Translate using HuggingFace MarianMT.
- get_supported_languages: Get list of supported language pairs for each engine.
- is_available: Check if any translation engine is available.
======================================================================
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import time

# Configure logging
# Logging configuration is handled by src/desktop/logging_config.py
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False
    logger.warning("argos-translate not available. Install with: pip install argos-translate")

try:
    from transformers import MarianMTModel, MarianTokenizer
    import torch
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logger.warning("transformers not available. Install with: pip install transformers torch")

class OfflineTranslator:
    """
    Offline translation class that supports multiple translation engines.
    
    This class provides offline translation capabilities using:
    1. argos-translate (primary) - Fast, lightweight offline translation
    2. HuggingFace MarianMT models (fallback) - High-quality neural translation
    
    Models are automatically downloaded on first use and cached locally.
    """
    
    def __init__(self, 
                 preferred_engine: str = "argos",
                 model_cache_dir: Optional[str] = None,
                 auto_download: bool = True):
        """
        Initialize the offline translator.
        
        Args:
            preferred_engine: "argos" or "huggingface"
            model_cache_dir: Directory to cache downloaded models
            auto_download: Whether to automatically download missing models
        """
        self.preferred_engine = preferred_engine.lower()
        self.auto_download = auto_download
        
        # Set up model cache directory
        if model_cache_dir is None:
            self.model_cache_dir = Path.home() / ".cache" / "talkbridge" / "translation_models"
        else:
            self.model_cache_dir = Path(model_cache_dir)
        
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize translation engines
        self.argos_available = ARGOS_AVAILABLE
        self.hf_available = HF_AVAILABLE
        
        # Cache for loaded models
        self._argos_models = {}
        self._hf_models = {}
        
        # Supported language pairs
        self.supported_pairs = {
            "argos": {
                "en-es": "English to Spanish",
                "es-en": "Spanish to English",
                "fr-es": "French to Spanish",
                "de-es": "German to Spanish",
                "it-es": "Italian to Spanish",
                "pt-es": "Portuguese to Spanish"
            },
            "huggingface": {
                "en-es": "Helsinki-NLP/opus-mt-en-es",
                "es-en": "Helsinki-NLP/opus-mt-es-en",
                "fr-es": "Helsinki-NLP/opus-mt-fr-es",
                "de-es": "Helsinki-NLP/opus-mt-de-es",
                "it-es": "Helsinki-NLP/opus-mt-it-es",
                "pt-es": "Helsinki-NLP/opus-mt-pt-es"
            }
        }
        
        logger.info(f"OfflineTranslator initialized with {preferred_engine} engine")
        logger.info(f"Model cache directory: {self.model_cache_dir}")
    
    def _download_argos_model(self, source_lang: str, target_lang: str) -> bool:
        """
        Download argos-translate model for the specified language pair.
        
        Args:
            source_lang: Source language code (e.g., 'en')
            target_lang: Target language code (e.g., 'es')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get available packages
            available_packages = argostranslate.package.get_available_packages()
            
            # Find the package for our language pair
            package = None
            for pkg in available_packages:
                if (pkg.from_code == source_lang and 
                    pkg.to_code == target_lang):
                    package = pkg
                    break
            
            if package is None:
                logger.error(f"No argos-translate model found for {source_lang}-{target_lang}")
                return False
            
            # Download and install the package
            logger.info(f"Downloading argos-translate model: {package}")
            argostranslate.package.install_from_path(package.download())
            logger.info(f"Successfully downloaded model for {source_lang}-{target_lang}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading argos-translate model: {e}")
            return False
    
    def _load_argos_model(self, source_lang: str, target_lang: str) -> Optional[Any]:
        """
        Load or download argos-translate model.
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Loaded model or None if failed
        """
        model_key = f"{source_lang}-{target_lang}"
        
        if model_key in self._argos_models:
            return self._argos_models[model_key]
        
        try:
            # Try to load existing model
            model = argostranslate.translate.get_installed_languages()
            source_lang_obj = None
            target_lang_obj = None
            
            for lang in model:
                if lang.code == source_lang:
                    source_lang_obj = lang
                elif lang.code == target_lang:
                    target_lang_obj = lang
            
            if source_lang_obj and target_lang_obj:
                translation = source_lang_obj.get_translation(target_lang_obj)
                self._argos_models[model_key] = translation
                logger.info(f"Loaded argos-translate model for {model_key}")
                return translation
            
            # Model not found, try to download
            if self.auto_download:
                logger.info(f"Model not found, attempting to download...")
                if self._download_argos_model(source_lang, target_lang):
                    # Try loading again after download
                    return self._load_argos_model(source_lang, target_lang)
            
            logger.error(f"Could not load argos-translate model for {model_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading argos-translate model: {e}")
            return None
    
    def _load_hf_model(self, source_lang: str, target_lang: str) -> Optional[tuple]:
        """
        Load HuggingFace MarianMT model.
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of (model, tokenizer) or None if failed
        """
        model_key = f"{source_lang}-{target_lang}"
        
        if model_key in self._hf_models:
            return self._hf_models[model_key]
        
        try:
            model_name = self.supported_pairs["huggingface"].get(model_key)
            if not model_name:
                logger.error(f"No HuggingFace model found for {model_key}")
                return None
            
            logger.info(f"Loading HuggingFace model: {model_name}")
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            
            self._hf_models[model_key] = (model, tokenizer)
            logger.info(f"Successfully loaded HuggingFace model for {model_key}")
            return (model, tokenizer)
            
        except Exception as e:
            logger.error(f"Error loading HuggingFace model: {e}")
            return None
    
    def translate_to_spanish(self, text: str, source_lang: str = "en") -> str:
        """
        Translate text to Spanish.
        
        This is the main function that provides offline translation to Spanish.
        It automatically handles model loading and fallback between engines.
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: "en" for English)
            
        Returns:
            Translated text in Spanish
            
        Raises:
            TranslationError: If translation fails
        """
        if not text or not text.strip():
            return ""
        
        # Normalize language codes
        source_lang = source_lang.lower()[:2]
        target_lang = "es"
        
        # Try preferred engine first
        if self.preferred_engine == "argos" and self.argos_available:
            result = self._translate_with_argos(text, source_lang, target_lang)
            if result:
                return result
        
        # Fallback to HuggingFace
        if self.hf_available:
            result = self._translate_with_hf(text, source_lang, target_lang)
            if result:
                return result
        
        # If both engines fail
        raise TranslationError(
            f"Translation failed. No available translation engines for {source_lang}-{target_lang}"
        )
    
    def _translate_with_argos(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate using argos-translate.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text or None if failed
        """
        try:
            translation = self._load_argos_model(source_lang, target_lang)
            if translation is None:
                return None
            
            start_time = time.time()
            result = translation.translate(text)
            latency = time.time() - start_time
            
            logger.info(f"Argos translation completed in {latency:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Argos translation error: {e}")
            return None
    
    def _translate_with_hf(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate using HuggingFace MarianMT.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text or None if failed
        """
        try:
            model_data = self._load_hf_model(source_lang, target_lang)
            if model_data is None:
                return None
            
            model, tokenizer = model_data
            
            start_time = time.time()
            
            # Tokenize and translate
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            with torch.no_grad():
                translated = model.generate(**inputs)
            
            result = tokenizer.decode(translated[0], skip_special_tokens=True)
            latency = time.time() - start_time
            
            logger.info(f"HuggingFace translation completed in {latency:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"HuggingFace translation error: {e}")
            return None
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of supported language pairs for each engine.
        
        Returns:
            Dictionary of supported language pairs by engine
        """
        return self.supported_pairs
    
    def is_available(self) -> bool:
        """
        Check if any translation engine is available.
        
        Returns:
            True if at least one engine is available
        """
        return self.argos_available or self.hf_available

class TranslationError(Exception):
    """Custom exception for translation errors."""
    pass

# Convenience function for quick translation
def translate_to_spanish(text: str, source_lang: str = "en") -> str:
    """
    Convenience function to translate text to Spanish.
    
    This is the main function that provides offline translation to Spanish.
    It automatically handles model loading and fallback between engines.
    
    Args:
        text: Text to translate
        source_lang: Source language code (default: "en" for English)
        
    Returns:
        Translated text in Spanish
        
    Raises:
        TranslationError: If translation fails
    """
    translator = OfflineTranslator()
    return translator.translate_to_spanish(text, source_lang)

# Example usage and testing
if __name__ == "__main__":
    # Test the translation module
    test_texts = [
        "Hello, how are you?",
        "The weather is beautiful today.",
        "I love programming in Python.",
        "This is a test of the translation system."
    ]
    
    print("Testing offline translation module...")
    print("=" * 50)
    
    translator = OfflineTranslator()
    
    if not translator.is_available():
        print("ERROR: No translation engines available!")
        print("Please install required packages:")
        print("  pip install argos-translate")
        print("  pip install transformers torch")
        exit(1)
    
    print(f"Available engines: argos={translator.argos_available}, huggingface={translator.hf_available}")
    print(f"Preferred engine: {translator.preferred_engine}")
    print()
    
    for text in test_texts:
        try:
            translated = translator.translate_to_spanish(text)
            print(f"Original: {text}")
            print(f"Translated: {translated}")
            print("-" * 30)
        except TranslationError as e:
            print(f"Translation failed: {e}")
            print("-" * 30) 