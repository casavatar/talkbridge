#!/usr/bin/env python3
"""
TalkBridge - Error Handling and Logging Tests
============================================

Comprehensive tests to verify the unified error handling and logging system.
Tests error scenarios, logging output, and UI integration.

Author: TalkBridge Team
Date: 2025-09-18
Version: 1.0

Test Categories:
- Logging system initialization and configuration
- Custom exception creation and handling
- Error propagation through service layers
- UI error notification integration
- Log file creation and rotation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging
import os

# Add src to path for imports
.parent.parent))

from talkbridge.logging_config import (
    configure_logging, get_logger, log_exception, get_log_statistics,
    setup_development_logging, setup_production_logging, reset_logging_for_testing
)
from talkbridge.utils.exceptions import (
    TalkBridgeError, AudioCaptureError, STTError, TTSError, 
    TranslationError, UIError, PipelineError, DeviceError,
    create_audio_capture_error, create_stt_error, create_tts_error,
    ErrorSeverity, ErrorCategory
)

class TestLoggingSystem(unittest.TestCase):
    """Test the centralized logging system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp()
        # Reset logging to ensure clean test state
        reset_logging_for_testing()
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary log directory
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        # Reset logging after test
        reset_logging_for_testing()
    
    def test_logging_configuration(self):
        """Test basic logging configuration."""
        # Configure logging with test directory
        configure_logging(
            console_level="DEBUG",
            file_level="INFO",
            log_dir=self.test_log_dir,
            development_mode=True
        )
        
        # Get logger and test basic functionality
        logger = get_logger("test.module")
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Check log file was created
        log_file = Path(self.test_log_dir) / "talkbridge.log"
        self.assertTrue(log_file.exists(), "Log file should be created")
        
        # Check log file content
        log_content = log_file.read_text()
        self.assertIn("Test info message", log_content)
        self.assertIn("Test warning message", log_content)
        self.assertIn("Test error message", log_content)
    
    def test_log_statistics(self):
        """Test log statistics gathering."""
        configure_logging(log_dir=self.test_log_dir)
        
        stats = get_log_statistics()
        
        self.assertIn("configured", stats)
        self.assertIn("log_dir", stats)
        self.assertIn("console_level", stats)
        self.assertIn("file_level", stats)
        self.assertTrue(stats["configured"])
        self.assertEqual(stats["log_dir"], self.test_log_dir)
    
    def test_development_logging(self):
        """Test development logging setup."""
        with patch('src.logging_config.configure_logging') as mock_config:
            setup_development_logging()
            
            mock_config.assert_called_once_with(
                console_level="DEBUG",
                file_level="DEBUG", 
                development_mode=True
            )
    
    def test_production_logging(self):
        """Test production logging setup."""
        test_log_dir = "/tmp/test_logs"
        
        with patch('src.logging_config.configure_logging') as mock_config:
            setup_production_logging(test_log_dir)
            
            mock_config.assert_called_once_with(
                console_level="WARNING",
                file_level="INFO",
                log_dir=test_log_dir,
                development_mode=False
            )

class TestCustomExceptions(unittest.TestCase):
    """Test custom exception hierarchy."""
    
    def test_base_exception(self):
        """Test TalkBridgeError base class."""
        error = TalkBridgeError(
            message="Test error",
            user_message="User-friendly message",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SYSTEM,
            context={"key": "value"}
        )
        
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.user_message, "User-friendly message")
        self.assertEqual(error.severity, ErrorSeverity.HIGH)
        self.assertEqual(error.category, ErrorCategory.SYSTEM)
        self.assertEqual(error.context["key"], "value")
        self.assertTrue(error.recoverable)
        self.assertTrue(error.error_code.startswith("TB_"))
    
    def test_audio_capture_error(self):
        """Test AudioCaptureError specialization."""
        error = AudioCaptureError(
            message="Microphone not found",
            device_name="USB Microphone"
        )
        
        self.assertIn("USB Microphone", error.user_message)
        self.assertEqual(error.device_name, "USB Microphone")
        self.assertEqual(error.category, ErrorCategory.HARDWARE)
        self.assertEqual(error.error_code, "TB_AUDIO_CAPTURE_ERROR")
    
    def test_stt_error(self):
        """Test STTError specialization."""
        error = STTError(
            message="Whisper model failed",
            model_name="whisper-large",
            language="en"
        )
        
        self.assertIn("whisper-large", error.user_message)
        self.assertEqual(error.model_name, "whisper-large")
        self.assertEqual(error.language, "en")
        self.assertEqual(error.category, ErrorCategory.SERVICE)
    
    def test_translation_error(self):
        """Test TranslationError specialization."""
        error = TranslationError(
            message="Translation API failed",
            source_language="en",
            target_language="es",
            service_name="LibreTranslate"
        )
        
        self.assertIn("en", error.user_message)
        self.assertIn("es", error.user_message)
        self.assertEqual(error.service_name, "LibreTranslate")
    
    def test_convenience_functions(self):
        """Test convenience functions for creating errors."""
        audio_error = create_audio_capture_error(
            "Device error",
            device_name="Test Device"
        )
        self.assertIsInstance(audio_error, AudioCaptureError)
        self.assertEqual(audio_error.device_name, "Test Device")
        
        stt_error = create_stt_error(
            "STT failed",
            model_name="test-model"
        )
        self.assertIsInstance(stt_error, STTError)
        self.assertEqual(stt_error.model_name, "test-model")
    
    def test_error_serialization(self):
        """Test error to dictionary conversion."""
        error = AudioCaptureError(
            message="Test error",
            device_name="Test Device"
        )
        
        error_dict = error.to_dict()
        
        self.assertEqual(error_dict["error_type"], "AudioCaptureError")
        self.assertEqual(error_dict["message"], "Test error")
        self.assertEqual(error_dict["severity"], ErrorSeverity.MEDIUM.value)
        self.assertEqual(error_dict["category"], ErrorCategory.HARDWARE.value)
        self.assertTrue(error_dict["recoverable"])

class TestErrorIntegration(unittest.TestCase):
    """Test error handling integration with services."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_log_dir = tempfile.mkdtemp()
        # Reset logging to ensure clean test state
        reset_logging_for_testing()
        configure_logging(log_dir=self.test_log_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        # Reset logging after test
        reset_logging_for_testing()
    
    def test_log_exception_function(self):
        """Test log_exception utility function."""
        logger = get_logger("test.error.logging")
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            log_exception(logger, e, "Test context")
        
        # Check log file content
        log_file = Path(self.test_log_dir) / "talkbridge.log"
        log_content = log_file.read_text()
        
        self.assertIn("Test context", log_content)
        self.assertIn("ValueError", log_content)
        self.assertIn("Test error", log_content)
    
    def test_error_propagation(self):
        """Test error propagation through service layers."""
        # Mock event bus for testing
        mock_event_bus = Mock()
        
        # Import and test UI services error handling
        from talkbridge.desktop.ui.ui_services import UIServices
        
        ui_services = UIServices(mock_event_bus)
        
        # Test error handling with structured exceptions
        test_error = AudioCaptureError(
            message="Test device error",
            device_name="Test Device"
        )
        
        ui_services._handle_service_error(
            test_error, 
            "test operation",
            "Test context"
        )
        
        # Verify event bus was called with user message
        mock_event_bus.emit_status.assert_called_once()
        call_args = mock_event_bus.emit_status.call_args
        self.assertIn("Test Device", call_args[0][0])  # User message
        self.assertEqual(call_args[0][1], "error")     # Status level
    
    @patch('src.audio.pipeline_manager.AudioCapture')
    def test_pipeline_manager_error_handling(self, mock_audio_capture):
        """Test PipelineManager error handling."""
        from talkbridge.audio.pipeline_manager import PipelineManager
        
        # Configure mock to raise exception
        mock_audio_capture.side_effect = Exception("Device not found")
        
        pipeline = PipelineManager()
        
        # Test that specific exceptions are raised
        with self.assertRaises((DeviceError, AudioCaptureError)):
            pipeline.start_microphone_capture()

class TestLoggingCleanup(unittest.TestCase):
    """Test logging configuration cleanup."""
    
    def test_no_basic_config_calls(self):
        """Verify no logging.basicConfig calls remain in key modules."""
        # This is a meta-test to ensure we removed print statements
        key_modules = [
            "src/audio/pipeline_manager.py",
            "src/desktop/components/chat_tab.py", 
            "src/desktop/ui/ui_services.py"
        ]
        
        for module_path in key_modules:
            if Path(module_path).exists():
                content = Path(module_path).read_text()
                
                # Check for logging.basicConfig calls (should be removed)
                self.assertNotIn("logging.basicConfig", content, 
                               f"Found logging.basicConfig in {module_path}")
                
                # Check for proper logger imports
                self.assertIn("get_logger", content,
                            f"Should use get_logger in {module_path}")

def run_error_handling_demo():
    """
    Demonstrate the unified error handling system.
    """
    print("🧪 TalkBridge Error Handling Demo")
    print("=" * 40)
    
    # Setup logging
    configure_logging(
        console_level="DEBUG",
        development_mode=True
    )
    
    logger = get_logger("demo.error_handling")
    
    print("\n1. Testing Structured Exceptions:")
    try:
        # Simulate an audio capture error
        raise AudioCaptureError(
            message="Failed to initialize microphone device",
            device_name="USB Audio Device",
            context={"device_id": 1, "sample_rate": 44100}
        )
    except AudioCaptureError as e:
        logger.error(f"Caught audio error: {e.user_message}")
        print(f"   User Message: {e.user_message}")
        print(f"   Error Code: {e.error_code}")
        print(f"   Severity: {e.severity.value}")
        print(f"   Category: {e.category.value}")
    
    print("\n2. Testing Translation Error:")
    try:
        raise TranslationError(
            message="Translation service timeout",
            source_language="english",
            target_language="spanish",
            service_name="LibreTranslate"
        )
    except TranslationError as e:
        log_exception(logger, e, "Translation failed during demo")
        print(f"   User Message: {e.user_message}")
    
    print("\n3. Testing UI Error:")
    try:
        raise UIError(
            message="Component rendering failed",
            component_name="ChatHistory"
        )
    except UIError as e:
        logger.exception("UI component error occurred")
        print(f"   Component: {e.component_name}")
        print(f"   User Message: {e.user_message}")
    
    print("\n4. Logging Statistics:")
    stats = get_log_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Error handling demo completed!")
    print("Check logs/talkbridge.log for detailed error logs.")

if __name__ == "__main__":
    # Run the demo first
    run_error_handling_demo()
    
    print("\n" + "=" * 50)
    print("Running Unit Tests...")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)