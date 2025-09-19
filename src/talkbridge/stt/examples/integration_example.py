#!/usr/bin/env python3
"""
TalkBridge STT - Integration Example
====================================

Integration example module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- openai-whisper
======================================================================
Functions:
- example_basic_transcription: Example of basic audio transcription.
- example_file_transcription: Example of file-based transcription.
- example_model_management: Example of model management.
- example_error_handling: Example of error handling.
- example_language_support: Example of language support.
- example_integration_with_talkbridge: Example of integration with TalkBridge components.
- main: Run all examples.
======================================================================
"""

import os
from pathlib import Path

from talkbridge.logging_config import get_logger
from talkbridge.stt import (
    transcribe_audio,
    transcribe_file,
    load_model,
    get_model_info,
    get_supported_languages,
    create_test_audio
)

logger = get_logger(__name__)

def example_basic_transcription():
    """Example of basic audio transcription."""
    logger.info("=== Basic Transcription Example ===")
    
    # Create test audio
    logger.info("Creating test audio...")
    audio_bytes = create_test_audio(duration=2.0)
    
    # Transcribe audio
    logger.info("Transcribing audio...")
    try:
        text = transcribe_audio(audio_bytes, language="es")
        logger.info("Transcribed text: %s", text)
    except Exception as e:
        logger.error("Transcription failed: %s", e)
    
    logger.info("Basic transcription example completed")

def example_file_transcription():
    """Example of file-based transcription."""
    logger.info("=== File Transcription Example ===")
    
    # Create test audio file
    logger.info("Creating test audio file...")
    audio_bytes = create_test_audio(duration=3.0)
    
    # Save to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(audio_bytes)
        temp_file = f.name
    
    try:
        # Transcribe file
        logger.info("Transcribing audio file...")
        text = transcribe_file(temp_file, language="en")
        logger.info("Transcribed text: %s", text)
    except Exception as e:
        logger.error("File transcription failed: %s", e)
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    logger.info("File transcription example completed")

def example_model_management():
    """Example of model management."""
    logger.info("=== Model Management Example ===")
    
    # Load model explicitly
    logger.info("Loading Whisper model...")
    success = load_model("base")
    logger.info("Model loading: %s", "Success" if success else "Failed")
    
    # Get model information
    info = get_model_info()
    logger.info("Model info: %s", info)
    
    # Get supported languages
    languages = get_supported_languages()
    logger.info("Supported languages: %s...", languages[:5])  # Show first 5
    
    logger.info("Model management example completed")

def example_error_handling():
    """Example of error handling."""
    logger.info("=== Error Handling Example ===")
    
    # Test with invalid audio
    logger.info("Testing with invalid audio data...")
    try:
        text = transcribe_audio(b"", language="es")
        logger.info("Result: %s", text)
    except ValueError as e:
        logger.warning("Expected error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
    
    # Test with small audio
    logger.info("Testing with small audio data...")
    try:
        text = transcribe_audio(b"small", language="es")
        logger.info("Result: %s", text)
    except ValueError as e:
        logger.warning("Expected error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
    
    logger.info("Error handling example completed")

def example_language_support():
    """Example of language support."""
    logger.info("=== Language Support Example ===")
    
    from talkbridge.stt import is_language_supported
    
    # Test different languages
    test_languages = ["en", "es", "fr", "de", "invalid"]
    
    for lang in test_languages:
        supported = is_language_supported(lang)
        logger.info("Language '%s': %s", lang, 'Supported' if supported else 'Not supported')
    
    logger.info("Language support example completed")

def example_integration_with_talkbridge():
    """Example of integration with TalkBridge components."""
    logger.info("=== TalkBridge Integration Example ===")
    
    # Simulate integration with STT API
    try:
        from talkbridge.web.api.stt_api import STTAPI
        
        # Create STT API instance
        stt_api = STTAPI()
        
        # Test transcription
        audio_bytes = create_test_audio(duration=1.5)
        text = stt_api.transcribe_audio(audio_bytes, language="es")
        logger.info("STT API transcription: %s", text)
        
        # Test supported languages
        languages = stt_api.get_supported_languages()
        logger.info("STT API languages: %d supported", len(languages))
        
        # Test engine status
        status = stt_api.get_engine_status()
        logger.info("Engine status: %s", status)
        
    except ImportError as e:
        logger.warning("Could not import STT API: %s", e)
    except Exception as e:
        logger.error("Integration test failed: %s", e)
    
    logger.info("TalkBridge integration example completed")

def main():
    """Run all examples."""
    logger.info("STT Module Integration Examples")
    logger.info("=" * 50)
    
    # Run examples
    example_basic_transcription()
    example_file_transcription()
    example_model_management()
    example_error_handling()
    example_language_support()
    example_integration_with_talkbridge()
    
    logger.info("All examples completed!")

if __name__ == "__main__":
    main() 