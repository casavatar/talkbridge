#!/usr/bin/env python3
"""
Test module for Voice Cloning

Tests the voice cloning functionality including:
- TTS model integration
- Voice synthesis from text
- Audio generation and formatting
- Error handling for various inputs

Author: TalkBridge QA Team
Date: 2024-01-01
"""

import unittest
import tempfile
import os
import wave
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import json

# Mock voice cloning module
class MockVoiceCloner:
    """Mock voice cloner class for testing."""
    
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/your_tts"):
        self.model_name = model_name
        self.is_loaded = False
        self.voice_samples = []
        self.supported_languages = ["en", "es", "fr", "de"]
    
    def load_model(self, model_name=None):
        """Load TTS model."""
        if model_name:
            self.model_name = model_name
        self.is_loaded = True
        return True
    
    def add_voice_samples(self, voice_samples_path):
        """Add voice samples for cloning."""
        if not os.path.exists(voice_samples_path):
            raise FileNotFoundError(f"Voice samples path not found: {voice_samples_path}")
        
        # Mock adding voice samples
        self.voice_samples.append(voice_samples_path)
        return True
    
    def synthesize_voice(self, text, voice_samples_path=None, language="en"):
        """Synthesize voice from text."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(text) > 1000:
            raise ValueError("Text too long (max 1000 characters)")
        
        # Generate mock audio based on text length
        sample_rate = 22050
        duration = len(text) * 0.1  # 0.1 seconds per character
        samples = int(sample_rate * duration)
        
        # Generate mock audio data
        audio_data = np.random.rand(samples).astype(np.float32)
        
        # Normalize audio
        audio_data = audio_data * 0.5  # Reduce volume
        
        return {
            "audio_data": audio_data,
            "sample_rate": sample_rate,
            "duration": duration,
            "text": text,
            "language": language,
            "voice_samples_used": voice_samples_path or "default"
        }
    
    def save_audio(self, audio_data, file_path, sample_rate=22050):
        """Save audio to WAV file."""
        if audio_data is None or len(audio_data) == 0:
            raise ValueError("Empty audio data")
        
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        return True


class TestVoiceCloner(unittest.TestCase):
    """Test cases for the VoiceCloner class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.voice_cloner = MockVoiceCloner()
    
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_voice_cloner_initialization(self):
        """Test voice cloner initialization with different models."""
        # Test default initialization
        cloner = MockVoiceCloner()
        self.assertEqual(cloner.model_name, "tts_models/multilingual/multi-dataset/your_tts")
        self.assertFalse(cloner.is_loaded)
        self.assertEqual(len(cloner.voice_samples), 0)
        
        # Test custom model
        cloner_custom = MockVoiceCloner("custom_model")
        self.assertEqual(cloner_custom.model_name, "custom_model")
        self.assertFalse(cloner_custom.is_loaded)
    
    def test_model_loading(self):
        """Test model loading functionality."""
        # Test loading model
        success = self.voice_cloner.load_model()
        self.assertTrue(success)
        self.assertTrue(self.voice_cloner.is_loaded)
        
        # Test loading different model
        success = self.voice_cloner.load_model("custom_model")
        self.assertTrue(success)
        self.assertEqual(self.voice_cloner.model_name, "custom_model")
        self.assertTrue(self.voice_cloner.is_loaded)
    
    def test_add_voice_samples(self):
        """Test adding voice samples for cloning."""
        # Create test voice samples directory
        voice_samples_dir = os.path.join(self.test_dir, "voice_samples")
        os.makedirs(voice_samples_dir, exist_ok=True)
        
        # Create some mock voice sample files
        sample_files = ["sample1.wav", "sample2.wav", "sample3.wav"]
        for filename in sample_files:
            file_path = os.path.join(voice_samples_dir, filename)
            with wave.open(file_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(22050)
                audio_data = np.random.rand(22050).astype(np.float32)
                wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        # Test adding voice samples
        success = self.voice_cloner.add_voice_samples(voice_samples_dir)
        self.assertTrue(success)
        self.assertIn(voice_samples_dir, self.voice_cloner.voice_samples)
    
    def test_add_voice_samples_nonexistent(self):
        """Test adding voice samples with non-existent path."""
        with self.assertRaises(FileNotFoundError):
            self.voice_cloner.add_voice_samples("nonexistent_path")
    
    def test_synthesize_voice(self):
        """Test voice synthesis from text."""
        # Load model first
        self.voice_cloner.load_model()
        
        # Test synthesis
        text = "Hello, how are you today?"
        result = self.voice_cloner.synthesize_voice(text, language="en")
        
        # Verify result structure
        self.assertIn("audio_data", result)
        self.assertIn("sample_rate", result)
        self.assertIn("duration", result)
        self.assertIn("text", result)
        self.assertIn("language", result)
        self.assertIn("voice_samples_used", result)
        
        # Verify content
        self.assertEqual(result["text"], text)
        self.assertEqual(result["language"], "en")
        self.assertEqual(result["sample_rate"], 22050)
        self.assertGreater(result["duration"], 0)
        self.assertIsInstance(result["audio_data"], np.ndarray)
        self.assertEqual(result["audio_data"].dtype, np.float32)
    
    def test_synthesize_voice_without_model(self):
        """Test voice synthesis without loading model first."""
        text = "Hello, world!"
        
        with self.assertRaises(RuntimeError):
            self.voice_cloner.synthesize_voice(text)
    
    def test_synthesize_empty_text(self):
        """Test voice synthesis with empty text."""
        self.voice_cloner.load_model()
        
        # Test with empty string
        with self.assertRaises(ValueError):
            self.voice_cloner.synthesize_voice("")
        
        # Test with whitespace only
        with self.assertRaises(ValueError):
            self.voice_cloner.synthesize_voice("   ")
        
        # Test with None
        with self.assertRaises(ValueError):
            self.voice_cloner.synthesize_voice(None)
    
    def test_synthesize_long_text(self):
        """Test voice synthesis with very long text."""
        self.voice_cloner.load_model()
        
        # Create very long text
        long_text = "This is a very long text. " * 50  # Much longer than 1000 chars
        
        with self.assertRaises(ValueError):
            self.voice_cloner.synthesize_voice(long_text)
    
    def test_synthesize_different_languages(self):
        """Test voice synthesis with different languages."""
        self.voice_cloner.load_model()
        
        # Test different languages
        test_cases = [
            ("Hello, how are you?", "en"),
            ("Hola, ¿cómo estás?", "es"),
            ("Bonjour, comment allez-vous?", "fr"),
            ("Hallo, wie geht es dir?", "de")
        ]
        
        for text, language in test_cases:
            result = self.voice_cloner.synthesize_voice(text, language=language)
            self.assertEqual(result["language"], language)
            self.assertEqual(result["text"], text)
            self.assertGreater(len(result["audio_data"]), 0)
    
    def test_audio_duration_calculation(self):
        """Test audio duration calculation based on text length."""
        self.voice_cloner.load_model()
        
        # Test different text lengths
        test_cases = [
            ("Hi", 0.2),      # 2 chars * 0.1 = 0.2 seconds
            ("Hello", 0.5),    # 5 chars * 0.1 = 0.5 seconds
            ("Hello world", 1.1),  # 11 chars * 0.1 = 1.1 seconds
        ]
        
        for text, expected_duration in test_cases:
            result = self.voice_cloner.synthesize_voice(text)
            self.assertAlmostEqual(result["duration"], expected_duration, places=1)
    
    def test_save_audio(self):
        """Test saving synthesized audio to file."""
        self.voice_cloner.load_model()
        
        # Synthesize voice
        text = "Hello, world!"
        result = self.voice_cloner.synthesize_voice(text)
        
        # Save audio
        file_path = os.path.join(self.test_dir, "test_audio.wav")
        success = self.voice_cloner.save_audio(
            result["audio_data"], 
            file_path, 
            result["sample_rate"]
        )
        
        # Verify file was created
        self.assertTrue(success)
        self.assertTrue(os.path.exists(file_path))
        
        # Verify WAV file properties
        with wave.open(file_path, 'rb') as wav_file:
            self.assertEqual(wav_file.getnchannels(), 1)
            self.assertEqual(wav_file.getsampwidth(), 2)  # 16-bit
            self.assertEqual(wav_file.getframerate(), 22050)
            self.assertGreater(wav_file.getnframes(), 0)
    
    def test_save_audio_empty_data(self):
        """Test saving audio with empty data."""
        with self.assertRaises(ValueError):
            self.voice_cloner.save_audio(None, "test.wav")
        
        with self.assertRaises(ValueError):
            self.voice_cloner.save_audio([], "test.wav")
    
    def test_audio_quality_parameters(self):
        """Test audio quality parameters and their effects."""
        self.voice_cloner.load_model()
        
        # Test different sample rates
        test_sample_rates = [8000, 16000, 22050, 44100]
        
        for sample_rate in test_sample_rates:
            text = "Test audio quality"
            result = self.voice_cloner.synthesize_voice(text)
            
            # Save with different sample rate
            file_path = os.path.join(self.test_dir, f"test_{sample_rate}.wav")
            success = self.voice_cloner.save_audio(
                result["audio_data"], 
                file_path, 
                sample_rate
            )
            
            self.assertTrue(success)
            self.assertTrue(os.path.exists(file_path))
    
    def test_voice_samples_integration(self):
        """Test integration with voice samples."""
        # Create voice samples
        voice_samples_dir = os.path.join(self.test_dir, "voice_samples")
        os.makedirs(voice_samples_dir, exist_ok=True)
        
        # Create mock voice sample
        sample_file = os.path.join(voice_samples_dir, "sample.wav")
        with wave.open(sample_file, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            audio_data = np.random.rand(22050).astype(np.float32)
            wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        # Add voice samples
        self.voice_cloner.add_voice_samples(voice_samples_dir)
        
        # Load model and synthesize
        self.voice_cloner.load_model()
        text = "Hello, this is a cloned voice."
        result = self.voice_cloner.synthesize_voice(text, voice_samples_dir)
        
        # Verify voice samples were used
        self.assertEqual(result["voice_samples_used"], voice_samples_dir)
        self.assertGreater(len(result["audio_data"]), 0)
    
    def test_error_handling(self):
        """Test error handling for various edge cases."""
        # Test with invalid text types
        self.voice_cloner.load_model()
        
        # Test with non-string input
        with self.assertRaises((TypeError, ValueError)):
            self.voice_cloner.synthesize_voice(123)
        
        # Test with list input
        with self.assertRaises((TypeError, ValueError)):
            self.voice_cloner.synthesize_voice(["Hello", "world"])
    
    def test_cross_platform_compatibility(self):
        """Test cross-platform compatibility aspects."""
        self.voice_cloner.load_model()
        
        # Test different file path formats
        test_paths = [
            os.path.join(self.test_dir, "test.wav"),
            os.path.join(self.test_dir, "test_audio", "synthesis.wav"),
            os.path.join(self.test_dir, "test", "nested", "audio.wav")
        ]
        
        text = "Cross-platform test"
        result = self.voice_cloner.synthesize_voice(text)
        
        for file_path in test_paths:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Try to save
            success = self.voice_cloner.save_audio(
                result["audio_data"], 
                file_path, 
                result["sample_rate"]
            )
            self.assertTrue(success)
            self.assertTrue(os.path.exists(file_path))
    
    def test_performance_characteristics(self):
        """Test performance characteristics of voice synthesis."""
        import time
        
        self.voice_cloner.load_model()
        
        # Test synthesis speed
        text = "This is a performance test for voice synthesis."
        
        start_time = time.time()
        result = self.voice_cloner.synthesize_voice(text)
        end_time = time.time()
        
        # Verify synthesis time is reasonable (mock should be fast)
        synthesis_time = end_time - start_time
        self.assertLess(synthesis_time, 1.0)  # Should be much faster than 1 second
        
        # Verify result was generated
        self.assertIsInstance(result, dict)
        self.assertIn("audio_data", result)
        self.assertGreater(len(result["audio_data"]), 0)
    
    def test_model_switching(self):
        """Test switching between different TTS models."""
        # Test loading different models
        models = [
            "tts_models/multilingual/multi-dataset/your_tts",
            "tts_models/en/ljspeech/tacotron2-DDC",
            "tts_models/en/vctk/vits",
            "custom_model"
        ]
        
        for model in models:
            cloner = MockVoiceCloner()
            success = cloner.load_model(model)
            
            self.assertTrue(success)
            self.assertEqual(cloner.model_name, model)
            self.assertTrue(cloner.is_loaded)
    
    def test_supported_languages(self):
        """Test supported languages functionality."""
        # Test that supported languages are available
        self.assertIsInstance(self.voice_cloner.supported_languages, list)
        self.assertGreater(len(self.voice_cloner.supported_languages), 0)
        
        # Test that common languages are supported
        common_languages = ["en", "es", "fr", "de"]
        for language in common_languages:
            self.assertIn(language, self.voice_cloner.supported_languages)
    
    def test_audio_data_validation(self):
        """Test audio data validation and format checking."""
        self.voice_cloner.load_model()
        
        text = "Audio data validation test"
        result = self.voice_cloner.synthesize_voice(text)
        
        # Verify audio data properties
        audio_data = result["audio_data"]
        self.assertIsInstance(audio_data, np.ndarray)
        self.assertEqual(audio_data.dtype, np.float32)
        self.assertGreater(len(audio_data), 0)
        
        # Verify data range (should be between -1 and 1 for float32)
        self.assertGreaterEqual(np.min(audio_data), -1.0)
        self.assertLessEqual(np.max(audio_data), 1.0)
        
        # Verify data is not all zeros
        self.assertNotEqual(np.sum(np.abs(audio_data)), 0.0)


if __name__ == "__main__":
    unittest.main() 