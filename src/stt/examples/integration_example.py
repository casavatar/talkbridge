#!/usr/bin/env python3
"""
TalkBridge STT - Integration Example
====================================

Módulo integration_example para TalkBridge

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

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.stt import (
    transcribe_audio,
    transcribe_file,
    load_model,
    get_model_info,
    get_supported_languages,
    create_test_audio
)


def example_basic_transcription():
    """Example of basic audio transcription."""
    print("=== Basic Transcription Example ===")
    
    # Create test audio
    print("Creating test audio...")
    audio_bytes = create_test_audio(duration=2.0)
    
    # Transcribe audio
    print("Transcribing audio...")
    try:
        text = transcribe_audio(audio_bytes, language="es")
        print(f"Transcribed text: {text}")
    except Exception as e:
        print(f"Transcription failed: {e}")
    
    print()


def example_file_transcription():
    """Example of file-based transcription."""
    print("=== File Transcription Example ===")
    
    # Create test audio file
    print("Creating test audio file...")
    audio_bytes = create_test_audio(duration=3.0)
    
    # Save to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(audio_bytes)
        temp_file = f.name
    
    try:
        # Transcribe file
        print("Transcribing audio file...")
        text = transcribe_file(temp_file, language="en")
        print(f"Transcribed text: {text}")
    except Exception as e:
        print(f"File transcription failed: {e}")
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    print()


def example_model_management():
    """Example of model management."""
    print("=== Model Management Example ===")
    
    # Load model explicitly
    print("Loading Whisper model...")
    success = load_model("base")
    print(f"Model loading: {'Success' if success else 'Failed'}")
    
    # Get model information
    info = get_model_info()
    print(f"Model info: {info}")
    
    # Get supported languages
    languages = get_supported_languages()
    print(f"Supported languages: {languages[:5]}...")  # Show first 5
    
    print()


def example_error_handling():
    """Example of error handling."""
    print("=== Error Handling Example ===")
    
    # Test with invalid audio
    print("Testing with invalid audio data...")
    try:
        text = transcribe_audio(b"", language="es")
        print(f"Result: {text}")
    except ValueError as e:
        print(f"Expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Test with small audio
    print("Testing with small audio data...")
    try:
        text = transcribe_audio(b"small", language="es")
        print(f"Result: {text}")
    except ValueError as e:
        print(f"Expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    print()


def example_language_support():
    """Example of language support."""
    print("=== Language Support Example ===")
    
    from src.stt import is_language_supported
    
    # Test different languages
    test_languages = ["en", "es", "fr", "de", "invalid"]
    
    for lang in test_languages:
        supported = is_language_supported(lang)
        print(f"Language '{lang}': {'Supported' if supported else 'Not supported'}")
    
    print()


def example_integration_with_talkbridge():
    """Example of integration with TalkBridge components."""
    print("=== TalkBridge Integration Example ===")
    
    # Simulate integration with STT API
    try:
        from src.ui.api.stt_api import STTAPI
        
        # Create STT API instance
        stt_api = STTAPI()
        
        # Test transcription
        audio_bytes = create_test_audio(duration=1.5)
        text = stt_api.transcribe_audio(audio_bytes, language="es")
        print(f"STT API transcription: {text}")
        
        # Test supported languages
        languages = stt_api.get_supported_languages()
        print(f"STT API languages: {len(languages)} supported")
        
        # Test engine status
        status = stt_api.get_engine_status()
        print(f"Engine status: {status}")
        
    except ImportError as e:
        print(f"Could not import STT API: {e}")
    except Exception as e:
        print(f"Integration test failed: {e}")
    
    print()


def main():
    """Run all examples."""
    print("STT Module Integration Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_transcription()
    example_file_transcription()
    example_model_management()
    example_error_handling()
    example_language_support()
    example_integration_with_talkbridge()
    
    print("All examples completed!")


if __name__ == "__main__":
    main() 