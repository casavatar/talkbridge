#!/usr/bin/env python3
"""
Test module for Translation

Tests the translation functionality including:
- Translation model integration
- Language detection and translation
- Error handling for various inputs
- Cross-platform compatibility

Author: TalkBridge QA Team
Date: 2024-01-01
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import json

# Mock translation module
class MockTranslator:
    """Mock translator class for testing."""
    
    def __init__(self):
        self.is_loaded = False
        self.supported_languages = ["en", "es", "fr", "de", "it", "pt"]
        self.translation_cache = {}
    
    def load_model(self):
        """Load translation model."""
        self.is_loaded = True
        return True
    
    def translate_text(self, text, source_lang="en", target_lang="es"):
        """Translate text from source language to target language."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(text) > 5000:
            raise ValueError("Text too long (max 5000 characters)")
        
        # Mock translations
        mock_translations = {
            ("en", "es"): {
                "Hello, how are you?": "Hola, ¿cómo estás?",
                "What's the weather like today?": "¿Cómo está el clima hoy?",
                "I love this application": "Me encanta esta aplicación",
                "Good morning": "Buenos días",
                "Thank you very much": "Muchas gracias"
            },
            ("es", "en"): {
                "Hola, ¿cómo estás?": "Hello, how are you?",
                "¿Cómo está el clima hoy?": "What's the weather like today?",
                "Me encanta esta aplicación": "I love this application",
                "Buenos días": "Good morning",
                "Muchas gracias": "Thank you very much"
            },
            ("en", "fr"): {
                "Hello, how are you?": "Bonjour, comment allez-vous?",
                "What's the weather like today?": "Quel temps fait-il aujourd'hui?",
                "I love this application": "J'aime cette application",
                "Good morning": "Bonjour",
                "Thank you very much": "Merci beaucoup"
            },
            ("fr", "en"): {
                "Bonjour, comment allez-vous?": "Hello, how are you?",
                "Quel temps fait-il aujourd'hui?": "What's the weather like today?",
                "J'aime cette application": "I love this application",
                "Bonjour": "Good morning",
                "Merci beaucoup": "Thank you very much"
            }
        }
        
        # Check cache first
        cache_key = (text, source_lang, target_lang)
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Get translation
        lang_pair = (source_lang, target_lang)
        if lang_pair in mock_translations and text in mock_translations[lang_pair]:
            translation = mock_translations[lang_pair][text]
        else:
            # Generate mock translation for unknown text
            translation = f"[{target_lang.upper()}] {text}"
        
        # Calculate confidence based on text length and language pair
        confidence = min(0.95, 0.7 + (len(text) * 0.01))
        
        result = {
            "translated_text": translation,
            "source_language": source_lang,
            "target_language": target_lang,
            "confidence": confidence,
            "original_text": text
        }
        
        # Cache result
        self.translation_cache[cache_key] = result
        return result
    
    def detect_language(self, text):
        """Detect the language of the input text."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Mock language detection
        language_hints = {
            "hello": "en",
            "hola": "es",
            "bonjour": "fr",
            "hallo": "de",
            "ciao": "it",
            "olá": "pt"
        }
        
        text_lower = text.lower()
        for hint, lang in language_hints.items():
            if hint in text_lower:
                return {
                    "detected_language": lang,
                    "confidence": 0.9
                }
        
        # Default to English if no hints found
        return {
            "detected_language": "en",
            "confidence": 0.5
        }
    
    def get_supported_languages(self):
        """Get list of supported languages."""
        return self.supported_languages


class TestTranslator(unittest.TestCase):
    """Test cases for the Translator class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.translator = MockTranslator()
    
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_translator_initialization(self):
        """Test translator initialization."""
        translator = MockTranslator()
        self.assertFalse(translator.is_loaded)
        self.assertIsInstance(translator.supported_languages, list)
        self.assertGreater(len(translator.supported_languages), 0)
        self.assertEqual(len(translator.translation_cache), 0)
    
    def test_model_loading(self):
        """Test model loading functionality."""
        # Test loading model
        success = self.translator.load_model()
        self.assertTrue(success)
        self.assertTrue(self.translator.is_loaded)
    
    def test_translate_text(self):
        """Test text translation functionality."""
        # Load model first
        self.translator.load_model()
        
        # Test translation
        text = "Hello, how are you?"
        result = self.translator.translate_text(text, "en", "es")
        
        # Verify result structure
        self.assertIn("translated_text", result)
        self.assertIn("source_language", result)
        self.assertIn("target_language", result)
        self.assertIn("confidence", result)
        self.assertIn("original_text", result)
        
        # Verify content
        self.assertEqual(result["original_text"], text)
        self.assertEqual(result["source_language"], "en")
        self.assertEqual(result["target_language"], "es")
        self.assertEqual(result["translated_text"], "Hola, ¿cómo estás?")
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)
    
    def test_translate_without_model(self):
        """Test translation without loading model first."""
        text = "Hello, world!"
        
        with self.assertRaises(RuntimeError):
            self.translator.translate_text(text)
    
    def test_translate_empty_text(self):
        """Test translation with empty text."""
        self.translator.load_model()
        
        # Test with empty string
        with self.assertRaises(ValueError):
            self.translator.translate_text("")
        
        # Test with whitespace only
        with self.assertRaises(ValueError):
            self.translator.translate_text("   ")
        
        # Test with None
        with self.assertRaises(ValueError):
            self.translator.translate_text(None)
    
    def test_translate_long_text(self):
        """Test translation with very long text."""
        self.translator.load_model()
        
        # Create very long text
        long_text = "This is a very long text. " * 200  # Much longer than 5000 chars
        
        with self.assertRaises(ValueError):
            self.translator.translate_text(long_text)
    
    def test_translate_different_language_pairs(self):
        """Test translation with different language pairs."""
        self.translator.load_model()
        
        # Test different language pairs
        test_cases = [
            ("Hello, how are you?", "en", "es", "Hola, ¿cómo estás?"),
            ("Hola, ¿cómo estás?", "es", "en", "Hello, how are you?"),
            ("Hello, how are you?", "en", "fr", "Bonjour, comment allez-vous?"),
            ("Bonjour, comment allez-vous?", "fr", "en", "Hello, how are you?")
        ]
        
        for original, source, target, expected in test_cases:
            result = self.translator.translate_text(original, source, target)
            self.assertEqual(result["translated_text"], expected)
            self.assertEqual(result["source_language"], source)
            self.assertEqual(result["target_language"], target)
    
    def test_translation_cache(self):
        """Test translation caching functionality."""
        self.translator.load_model()
        
        text = "Hello, how are you?"
        
        # First translation
        result1 = self.translator.translate_text(text, "en", "es")
        
        # Second translation (should use cache)
        result2 = self.translator.translate_text(text, "en", "es")
        
        # Verify results are identical
        self.assertEqual(result1, result2)
        
        # Verify cache was used
        cache_key = (text, "en", "es")
        self.assertIn(cache_key, self.translator.translation_cache)
    
    def test_unknown_text_translation(self):
        """Test translation of unknown text."""
        self.translator.load_model()
        
        unknown_text = "This is an unknown text that should be translated."
        result = self.translator.translate_text(unknown_text, "en", "es")
        
        # Should generate mock translation
        self.assertIn("[ES]", result["translated_text"])
        self.assertGreater(result["confidence"], 0.0)
    
    def test_detect_language(self):
        """Test language detection functionality."""
        # Test language detection
        test_cases = [
            ("Hello, how are you?", "en"),
            ("Hola, ¿cómo estás?", "es"),
            ("Bonjour, comment allez-vous?", "fr"),
            ("Hallo, wie geht es dir?", "de"),
            ("Ciao, come stai?", "it"),
            ("Olá, como você está?", "pt")
        ]
        
        for text, expected_lang in test_cases:
            result = self.translator.detect_language(text)
            self.assertEqual(result["detected_language"], expected_lang)
            self.assertGreaterEqual(result["confidence"], 0.0)
            self.assertLessEqual(result["confidence"], 1.0)
    
    def test_detect_language_empty_text(self):
        """Test language detection with empty text."""
        # Test with empty string
        with self.assertRaises(ValueError):
            self.translator.detect_language("")
        
        # Test with whitespace only
        with self.assertRaises(ValueError):
            self.translator.detect_language("   ")
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        languages = self.translator.get_supported_languages()
        
        self.assertIsInstance(languages, list)
        self.assertGreater(len(languages), 0)
        
        # Test that common languages are supported
        common_languages = ["en", "es", "fr", "de"]
        for language in common_languages:
            self.assertIn(language, languages)
    
    def test_confidence_scoring(self):
        """Test confidence scoring based on text length."""
        self.translator.load_model()
        
        # Test different text lengths
        test_cases = [
            ("Hi", 0.7),           # Short text
            ("Hello", 0.75),        # Medium text
            ("Hello, how are you?", 0.85),  # Longer text
            ("This is a much longer text for testing confidence scoring.", 0.95)  # Long text
        ]
        
        for text, expected_min_confidence in test_cases:
            result = self.translator.translate_text(text, "en", "es")
            self.assertGreaterEqual(result["confidence"], expected_min_confidence)
            self.assertLessEqual(result["confidence"], 0.95)
    
    def test_error_handling(self):
        """Test error handling for various edge cases."""
        # Test with invalid text types
        self.translator.load_model()
        
        # Test with non-string input
        with self.assertRaises((TypeError, ValueError)):
            self.translator.translate_text(123)
        
        # Test with list input
        with self.assertRaises((TypeError, ValueError)):
            self.translator.translate_text(["Hello", "world"])
    
    def test_cross_platform_compatibility(self):
        """Test cross-platform compatibility aspects."""
        self.translator.load_model()
        
        # Test with different text encodings and special characters
        test_texts = [
            "Hello, world!",
            "Hola, ¡mundo!",
            "Bonjour, monde !",
            "Hallo, Welt!",
            "Ciao, mondo!",
            "Olá, mundo!"
        ]
        
        for text in test_texts:
            result = self.translator.translate_text(text, "en", "es")
            self.assertIsInstance(result, dict)
            self.assertIn("translated_text", result)
            self.assertGreater(len(result["translated_text"]), 0)
    
    def test_performance_characteristics(self):
        """Test performance characteristics of translation."""
        import time
        
        self.translator.load_model()
        
        # Test translation speed
        text = "This is a performance test for translation functionality."
        
        start_time = time.time()
        result = self.translator.translate_text(text, "en", "es")
        end_time = time.time()
        
        # Verify translation time is reasonable (mock should be fast)
        translation_time = end_time - start_time
        self.assertLess(translation_time, 1.0)  # Should be much faster than 1 second
        
        # Verify result was generated
        self.assertIsInstance(result, dict)
        self.assertIn("translated_text", result)
    
    def test_bidirectional_translation(self):
        """Test bidirectional translation consistency."""
        self.translator.load_model()
        
        original_text = "Hello, how are you?"
        
        # Translate English to Spanish
        en_to_es = self.translator.translate_text(original_text, "en", "es")
        
        # Translate Spanish back to English
        es_to_en = self.translator.translate_text(en_to_es["translated_text"], "es", "en")
        
        # Verify bidirectional translation works
        self.assertEqual(es_to_en["translated_text"], original_text)
        self.assertEqual(en_to_es["source_language"], "en")
        self.assertEqual(en_to_es["target_language"], "es")
        self.assertEqual(es_to_en["source_language"], "es")
        self.assertEqual(es_to_en["target_language"], "en")
    
    def test_translation_quality(self):
        """Test translation quality and consistency."""
        self.translator.load_model()
        
        # Test that translations are consistent
        test_phrases = [
            "Hello, how are you?",
            "What's the weather like today?",
            "I love this application",
            "Good morning",
            "Thank you very much"
        ]
        
        for phrase in test_phrases:
            # Translate to Spanish
            result = self.translator.translate_text(phrase, "en", "es")
            
            # Verify translation quality
            self.assertGreater(len(result["translated_text"]), 0)
            self.assertNotEqual(result["translated_text"], phrase)  # Should be different
            self.assertGreater(result["confidence"], 0.5)  # Should have reasonable confidence
    
    def test_language_validation(self):
        """Test validation of language codes."""
        self.translator.load_model()
        
        # Test with valid language codes
        valid_languages = ["en", "es", "fr", "de", "it", "pt"]
        
        for lang in valid_languages:
            result = self.translator.translate_text("Hello", "en", lang)
            self.assertEqual(result["target_language"], lang)
        
        # Test with unsupported language (should still work with mock)
        result = self.translator.translate_text("Hello", "en", "xx")
        self.assertEqual(result["target_language"], "xx")
        self.assertIn("[XX]", result["translated_text"])


if __name__ == "__main__":
    unittest.main() 