#!/usr/bin/env python3
"""
Test module for STT Module

Tests the new STT module functionality including:
- Module import and initialization
- Configuration loading
- Audio utilities
- Engine initialization
- Basic transcription workflow

Author: TalkBridge QA Team
Date: 2024-01-01
"""
import pytest
from talkbridge.stt import STTEngine


import unittest
import tempfile
import os

# Add src to path for imports

class TestSTTModule(unittest.TestCase):
    """Test cases for the STT module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_module_import(self):
        """Test that the STT module can be imported."""
        try:
            from stt import (
                transcribe_audio,
                transcribe_file,
                load_model,
                get_model_info,
                get_supported_languages
            )
            self.assertTrue(True, "STT module imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import STT module: {e}")
    
    def test_config_import(self):
        """Test that configuration can be imported."""
        try:
            from stt.config import (
                MODEL_NAME,
                DEFAULT_LANGUAGE,
                SUPPORTED_LANGUAGES,
                DEVICE
            )
            self.assertEqual(MODEL_NAME, "base")
            self.assertEqual(DEFAULT_LANGUAGE, "es")
            self.assertIsInstance(SUPPORTED_LANGUAGES, list)
            self.assertIn("en", SUPPORTED_LANGUAGES)
            self.assertIn("es", SUPPORTED_LANGUAGES)
        except ImportError as e:
            self.fail(f"Failed to import STT config: {e}")
    
    def test_audio_utils_import(self):
        """Test that audio utilities can be imported."""
        try:
            from stt.audio_utils import (
                validate_audio_bytes,
                validate_audio_file,
                create_test_audio
            )
            self.assertTrue(True, "Audio utilities imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import audio utilities: {e}")
    
    def test_whisper_engine_import(self):
        """Test that Whisper engine can be imported."""
        try:
            from stt.whisper_engine import WhisperEngine, get_whisper_engine
            self.assertTrue(True, "Whisper engine imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import Whisper engine: {e}")
    
    def test_interface_import(self):
        """Test that interface functions can be imported."""
        try:
            from stt.interface import (
                transcribe_audio,
                transcribe_file,
                load_model,
                get_model_info
            )
            self.assertTrue(True, "Interface functions imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import interface functions: {e}")
    
    def test_audio_validation(self):
        """Test audio validation functions."""
        from stt.audio_utils import validate_audio_bytes, validate_audio_file
        
        # Test empty audio bytes
        self.assertFalse(validate_audio_bytes(b""))
        self.assertFalse(validate_audio_bytes(None))
        
        # Test small audio bytes
        self.assertFalse(validate_audio_bytes(b"small"))
        
        # Test valid audio bytes (minimum size)
        valid_audio = b"x" * 1024
        self.assertTrue(validate_audio_bytes(valid_audio))
        
        # Test file validation
        non_existent_file = "nonexistent.wav"
        self.assertFalse(validate_audio_file(non_existent_file))
    
    def test_test_audio_creation(self):
        """Test test audio creation."""
        from stt.audio_utils import create_test_audio
        
        # Create test audio
        audio_bytes = create_test_audio(duration=1.0)
        
        # Verify it's valid
        self.assertIsInstance(audio_bytes, bytes)
        self.assertGreater(len(audio_bytes), 0)
        
        # Verify it can be validated
        from stt.audio_utils import validate_audio_bytes
        self.assertTrue(validate_audio_bytes(audio_bytes))
    
    def test_whisper_engine_initialization(self):
        """Test Whisper engine initialization."""
        from stt.whisper_engine import WhisperEngine
        
        # Test engine creation
        engine = WhisperEngine("base", "cpu")
        self.assertEqual(engine.model_name, "base")
        self.assertEqual(engine.device, "cpu")
        self.assertFalse(engine.is_loaded)
        
        # Test device detection
        device = engine._detect_device("cpu")
        self.assertEqual(device, "cpu")
    
    def test_supported_languages(self):
        """Test supported languages functionality."""
        from stt import get_supported_languages, is_language_supported
        
        languages = get_supported_languages()
        self.assertIsInstance(languages, list)
        self.assertGreater(len(languages), 0)
        
        # Test specific languages
        self.assertTrue(is_language_supported("en"))
        self.assertTrue(is_language_supported("es"))
        self.assertFalse(is_language_supported("invalid"))
    
    def test_model_info(self):
        """Test model information retrieval."""
        from stt import get_model_info, get_engine_status
        
        # Test model info
        info = get_model_info()
        self.assertIsInstance(info, dict)
        self.assertIn("model_name", info)
        self.assertIn("device", info)
        self.assertIn("is_loaded", info)
        
        # Test engine status
        status = get_engine_status()
        self.assertIsInstance(status, dict)
        self.assertIn("model_loaded", status)
        self.assertIn("model_name", status)
        self.assertIn("device", status)
    
    def test_interface_functions(self):
        """Test interface function availability."""
        from stt import (
            transcribe_audio,
            transcribe_file,
            load_model,
            unload_model,
            get_model_info,
            get_supported_languages,
            is_language_supported,
            is_model_ready,
            get_engine_status
        )
        
        # All functions should be callable
        self.assertTrue(callable(transcribe_audio))
        self.assertTrue(callable(transcribe_file))
        self.assertTrue(callable(load_model))
        self.assertTrue(callable(unload_model))
        self.assertTrue(callable(get_model_info))
        self.assertTrue(callable(get_supported_languages))
        self.assertTrue(callable(is_language_supported))
        self.assertTrue(callable(is_model_ready))
        self.assertTrue(callable(get_engine_status))
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        from stt import transcribe_audio
        
        # Test with invalid audio bytes
        with self.assertRaises(ValueError):
            transcribe_audio(b"")
        
        with self.assertRaises(ValueError):
            transcribe_audio(b"too_small")
    
    def test_configuration_access(self):
        """Test that configuration values are accessible."""
        from stt.config import (
            MODEL_NAME,
            DEFAULT_LANGUAGE,
            SUPPORTED_LANGUAGES,
            DEVICE,
            SAMPLE_RATE,
            CHANNELS,
            MAX_AUDIO_DURATION
        )
        
        # Test configuration values
        self.assertIsInstance(MODEL_NAME, str)
        self.assertIsInstance(DEFAULT_LANGUAGE, str)
        self.assertIsInstance(SUPPORTED_LANGUAGES, list)
        self.assertIsInstance(DEVICE, str)
        self.assertIsInstance(SAMPLE_RATE, int)
        self.assertIsInstance(CHANNELS, int)
        self.assertIsInstance(MAX_AUDIO_DURATION, int)
        
        # Test specific values
        self.assertEqual(DEFAULT_LANGUAGE, "es")
        self.assertEqual(SAMPLE_RATE, 16000)
        self.assertEqual(CHANNELS, 1)
        self.assertGreater(MAX_AUDIO_DURATION, 0)

if __name__ == "__main__":
    unittest.main() 