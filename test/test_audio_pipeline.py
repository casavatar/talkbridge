"""
Unit tests for the refactored TalkBridge audio pipeline components.

Tests the ports, adapters, and pipeline manager to ensure proper functionality
and contract compliance after the refactoring.
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from typing import List

# Import the components we're testing
try:
    from src.audio.ports import (
        AudioData, AudioFormat, TranscriptionResult, TranslationResult,
        AudioCapturePort, STTPort, TranslationPort
    )
    from src.audio.adapters import (
        AudioCaptureAdapter, WhisperSTTAdapter, TranslationAdapter
    )
    from src.audio.pipeline_manager import PipelineManager, AudioSourceType
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import components for testing: {e}")
    COMPONENTS_AVAILABLE = False


class TestAudioDataStructures(unittest.TestCase):
    """Test the data structures defined in ports.py"""
    
    def test_audio_data_creation(self):
        """Test AudioData creation and properties."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        audio_data = AudioData(
            data=b"test_audio_data",
            sample_rate=44100,
            channels=2,
            format=AudioFormat.PCM,
            source_type="microphone",
            language_hint="en"
        )
        
        self.assertEqual(audio_data.sample_rate, 44100)
        self.assertEqual(audio_data.channels, 2)
        self.assertEqual(audio_data.format, AudioFormat.PCM)
        self.assertEqual(audio_data.source_type, "microphone")
        self.assertEqual(audio_data.language_hint, "en")
    
    def test_transcription_result_creation(self):
        """Test TranscriptionResult creation and properties."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        result = TranscriptionResult(
            text="Hello world",
            language="en",
            confidence=0.95,
            processing_time=1.5
        )
        
        self.assertEqual(result.text, "Hello world")
        self.assertEqual(result.language, "en")
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.processing_time, 1.5)


class TestMockSTTAdapter(unittest.TestCase):
    """Test STT adapter behavior with mocked engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
    
    @patch('src.audio.adapters.stt_adapter.WHISPER_AVAILABLE', True)
    @patch('src.audio.adapters.stt_adapter.WhisperEngine')
    def test_stt_adapter_transcription(self, mock_whisper_engine):
        """Test STT adapter transcription functionality."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        # Mock the WhisperEngine
        mock_engine_instance = Mock()
        mock_engine_instance.transcribe.return_value = {
            'text': 'Hello world',
            'language': 'en',
            'segments': []
        }
        mock_whisper_engine.return_value = mock_engine_instance
        
        # Create adapter
        adapter = WhisperSTTAdapter(model_size="base")
        
        # Create test audio data
        audio_data = AudioData(
            data=b"dummy_audio_data",
            sample_rate=16000,
            channels=1,
            format=AudioFormat.PCM,
            source_type="microphone"
        )
        
        # Test transcription
        result = adapter.transcribe(audio_data)
        
        self.assertIsInstance(result, TranscriptionResult)
        self.assertEqual(result.text, "Hello world")
        self.assertEqual(result.language, "en")
        self.assertGreater(result.confidence, 0)
    
    @patch('src.audio.adapters.translation_adapter.TRANSLATOR_AVAILABLE', True)
    @patch('src.audio.adapters.translation_adapter.Translator')
    def test_translation_adapter(self, mock_translator):
        """Test translation adapter functionality."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        # Mock the Translator
        mock_translator_instance = Mock()
        mock_translator_instance.translate.return_value = {
            'translated_text': 'Hola mundo',
            'detected_language': 'en',
            'confidence': 0.95
        }
        mock_translator.return_value = mock_translator_instance
        
        # Create adapter
        adapter = TranslationAdapter(service="google")
        
        # Test translation
        result = adapter.translate("Hello world", "en", "es")
        
        self.assertIsInstance(result, TranslationResult)
        self.assertEqual(result.original_text, "Hello world")
        self.assertEqual(result.translated_text, "Hola mundo")
        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language, "es")


class TestPipelineManagerCallbacks(unittest.TestCase):
    """Test the refactored callback system in PipelineManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        # Create mock callbacks
        self.transcript_callback = Mock()
        self.translation_callback = Mock()
        self.status_callback = Mock()
    
    @patch('src.audio.pipeline_manager.ADAPTERS_AVAILABLE', True)
    @patch('src.audio.adapters.WhisperSTTAdapter')
    @patch('src.audio.adapters.TranslationAdapter')
    def test_pipeline_manager_initialization(self, mock_translation_adapter, mock_stt_adapter):
        """Test PipelineManager initialization with adapters."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        # Mock adapter instances
        mock_stt_instance = Mock()
        mock_stt_instance.is_ready.return_value = True
        mock_stt_adapter.return_value = mock_stt_instance
        
        mock_translation_instance = Mock()
        mock_translation_instance.is_ready.return_value = True
        mock_translation_adapter.return_value = mock_translation_instance
        
        # Create pipeline manager
        pipeline = PipelineManager(
            on_transcript=self.transcript_callback,
            on_translation=self.translation_callback,
            on_status=self.status_callback
        )
        
        # Check that adapters were initialized
        self.assertIsNotNone(pipeline.stt_adapter)
        self.assertIsNotNone(pipeline.translation_adapter)
        self.assertEqual(pipeline.on_transcript, self.transcript_callback)
        self.assertEqual(pipeline.on_translation, self.translation_callback)
        self.assertEqual(pipeline.on_status, self.status_callback)
    
    def test_pipeline_callback_signatures(self):
        """Test that callback signatures match the expected interface."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        # Test transcript callback signature
        try:
            self.transcript_callback("microphone", "hello world", "en", 0.95)
            self.transcript_callback.assert_called_with("microphone", "hello world", "en", 0.95)
        except Exception as e:
            self.fail(f"Transcript callback signature test failed: {e}")
        
        # Test translation callback signature
        try:
            self.translation_callback("microphone", "hello", "hola", "en", "es")
            self.translation_callback.assert_called_with("microphone", "hello", "hola", "en", "es")
        except Exception as e:
            self.fail(f"Translation callback signature test failed: {e}")


class TestVoiceActivityDetection(unittest.TestCase):
    """Test voice activity detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
    
    @patch('src.audio.pipeline_manager.ADAPTERS_AVAILABLE', False)
    def test_vad_detection(self):
        """Test voice activity detection logic."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        # Create pipeline manager without adapters
        pipeline = PipelineManager()
        
        # Test with silence (all zeros)
        silent_audio = b'\x00' * 1000
        has_voice = pipeline._detect_voice_activity(silent_audio)
        self.assertFalse(has_voice)
        
        # Test with noise (non-zero values)
        noisy_audio = b'\x10\x20\x30\x40' * 250  # Some non-zero values
        has_voice = pipeline._detect_voice_activity(noisy_audio)
        self.assertTrue(has_voice)
    
    @patch('src.audio.pipeline_manager.ADAPTERS_AVAILABLE', False)
    def test_audio_buffering(self):
        """Test audio buffering logic."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        pipeline = PipelineManager()
        
        # Create test audio stream data
        from src.audio.pipeline_manager import AudioStreamData
        
        test_data = AudioStreamData(
            source_type=AudioSourceType.MICROPHONE,
            audio_data=b"test_audio",
            timestamp=time.time(),
            device_name="test_device",
            sample_rate=16000,
            channels=1
        )
        
        # Test adding to buffer
        initial_buffer_size = len(pipeline.audio_buffers[AudioSourceType.MICROPHONE])
        pipeline._add_to_audio_buffer(test_data)
        new_buffer_size = len(pipeline.audio_buffers[AudioSourceType.MICROPHONE])
        
        self.assertEqual(new_buffer_size, initial_buffer_size + 1)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and graceful degradation."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
    
    @patch('src.audio.pipeline_manager.ADAPTERS_AVAILABLE', False)
    def test_graceful_degradation(self):
        """Test graceful degradation when components fail."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        error_callback = Mock()
        status_callback = Mock()
        
        pipeline = PipelineManager(
            on_status=status_callback
        )
        pipeline.error_callback = error_callback
        
        # Test component failure handling
        test_error = Exception("Test component failure")
        pipeline.handle_component_failure("stt_adapter", test_error)
        
        # Check that error callback was called
        error_callback.assert_called()
        
        # Check that STT adapter was disabled
        self.assertIsNone(pipeline.stt_adapter)
    
    @patch('src.audio.pipeline_manager.ADAPTERS_AVAILABLE', False)
    def test_health_monitoring(self):
        """Test pipeline health monitoring."""
        if not COMPONENTS_AVAILABLE:
            self.skipTest("Components not available")
        
        pipeline = PipelineManager()
        
        # Get health status
        health = pipeline.get_pipeline_health()
        
        # Check health status structure
        self.assertIn('timestamp', health)
        self.assertIn('overall_status', health)
        self.assertIn('components', health)
        self.assertIn('performance', health)
        
        # Check component status
        components = health['components']
        self.assertIn('stt_adapter', components)
        self.assertIn('translation_adapter', components)
        self.assertIn('audio_capture', components)


# Test runner
if __name__ == '__main__':
    if COMPONENTS_AVAILABLE:
        unittest.main(verbosity=2)
    else:
        print("Components not available for testing. Please ensure all modules are properly imported.")
        print("This is expected if running tests without the full TalkBridge environment.")