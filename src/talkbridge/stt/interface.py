#!/usr/bin/env python3
"""
TalkBridge STT - Interface
==========================

Module interface

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- openai-whisper
======================================================================
Functions:
- _get_engine: Get or create the global Whisper engine instance.
- transcribe_audio: Transcribe audio bytes to text using offline Whisper model.
- transcribe_file: Transcribe audio file to text.
- transcribe_with_metadata: Transcribe audio file with detailed metadata.
- load_model: Load Whisper model explicitly.
- unload_model: Unload the Whisper model to free memory.
- get_model_info: Get information about the current model.
- get_supported_languages: Get list of supported languages.
- is_language_supported: Check if language is supported.
- is_model_ready: Check if the model is loaded and ready for transcription.
======================================================================
"""

import logging
from typing import Optional, Dict, Any

from .whisper_engine import WhisperEngine, get_whisper_engine, is_model_loaded
from .config import DEFAULT_LANGUAGE, MODEL_NAME, DEVICE
from .audio_utils import validate_audio_bytes, validate_audio_file

# Set up logging
logger = logging.getLogger(__name__)

# Global engine instance (singleton)
_engine = None

def _get_engine() -> WhisperEngine:
    """
    Get or create the global Whisper engine instance.
    
    Returns:
        WhisperEngine instance
    """
    global _engine
    
    if _engine is None:
        _engine = get_whisper_engine(MODEL_NAME, DEVICE)
    
    return _engine

def transcribe_audio(audio_bytes: bytes, language: Optional[str] = None) -> str:
    """
    Transcribe audio bytes to text using offline Whisper model.
    
    This is the main public function for transcription. It handles:
    - Audio validation
    - Model loading (if needed)
    - Transcription with error handling
    - Clean text output
    
    Args:
        audio_bytes: Raw audio data as bytes
        language: Language code for transcription (default: "es")
        
    Returns:
        Transcribed text as string
        
    Raises:
        ValueError: If audio data is invalid
        RuntimeError: If model loading fails
        Exception: For other transcription errors
    """
    try:
        # Validate audio bytes
        if not validate_audio_bytes(audio_bytes):
            raise ValueError("Invalid audio bytes provided")
        
        # Get engine and ensure model is loaded
        engine = _get_engine()
        if not engine.is_loaded:
            if not engine.load_model():
                raise RuntimeError("Failed to load Whisper model")
        
        # Use default language if none specified
        if language is None:
            language = DEFAULT_LANGUAGE
        
        logger.info(f"Transcribing {len(audio_bytes)} bytes of audio data")
        
        # Perform transcription
        result = engine.transcribe_audio_bytes(audio_bytes, language)
        
        logger.info(f"Transcription completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise

def transcribe_file(file_path: str, language: Optional[str] = None) -> str:
    """
    Transcribe audio file to text.
    
    Args:
        file_path: Path to audio file
        language: Language code for transcription (default: "es")
        
    Returns:
        Transcribed text as string
    """
    try:
        # Validate audio file
        if not validate_audio_file(file_path):
            raise ValueError(f"Invalid audio file: {file_path}")
        
        # Get engine and ensure model is loaded
        engine = _get_engine()
        if not engine.is_loaded:
            if not engine.load_model():
                raise RuntimeError("Failed to load Whisper model")
        
        # Use default language if none specified
        if language is None:
            language = DEFAULT_LANGUAGE
        
        logger.info(f"Transcribing audio file: {file_path}")
        
        # Perform transcription
        result = engine.transcribe_file(file_path, language)
        
        logger.info(f"File transcription completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"File transcription failed: {e}")
        raise

def transcribe_with_metadata(file_path: str, 
                           language: Optional[str] = None) -> Dict[str, Any]:
    """
    Transcribe audio file with detailed metadata.
    
    Args:
        file_path: Path to audio file
        language: Language code for transcription (default: "es")
        
    Returns:
        Dictionary with transcription result and metadata
    """
    try:
        # Validate audio file
        if not validate_audio_file(file_path):
            raise ValueError(f"Invalid audio file: {file_path}")
        
        # Get engine and ensure model is loaded
        engine = _get_engine()
        if not engine.is_loaded:
            if not engine.load_model():
                raise RuntimeError("Failed to load Whisper model")
        
        # Use default language if none specified
        if language is None:
            language = DEFAULT_LANGUAGE
        
        logger.info(f"Transcribing file with metadata: {file_path}")
        
        # Perform transcription with metadata
        result = engine.transcribe_with_metadata(file_path, language)
        
        logger.info(f"File transcription with metadata completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"File transcription with metadata failed: {e}")
        raise

def load_model(model_name: Optional[str] = None) -> bool:
    """
    Load Whisper model explicitly.
    
    Args:
        model_name: Optional model name to load
        
    Returns:
        True if model loaded successfully, False otherwise
    """
    try:
        engine = _get_engine()
        return engine.load_model(model_name)
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False

def unload_model() -> None:
    """
    Unload the Whisper model to free memory.
    """
    global _engine
    
    if _engine:
        _engine.unload_model()
        _engine = None
        logger.info("Model unloaded and memory freed")

def get_model_info() -> Dict[str, Any]:
    """
    Get information about the current model.
    
    Returns:
        Dictionary with model information
    """
    engine = _get_engine()
    return engine.get_model_info()

def get_supported_languages() -> list:
    """
    Get list of supported languages.
    
    Returns:
        List of supported language codes
    """
    engine = _get_engine()
    return engine.get_supported_languages()

def is_language_supported(language: str) -> bool:
    """
    Check if language is supported.
    
    Args:
        language: Language code to check
        
    Returns:
        True if language is supported, False otherwise
    """
    engine = _get_engine()
    return engine.is_language_supported(language)

def is_model_ready() -> bool:
    """
    Check if the model is loaded and ready for transcription.
    
    Returns:
        True if model is ready, False otherwise
    """
    return is_model_loaded()

def get_engine_status() -> Dict[str, Any]:
    """
    Get comprehensive status of the STT engine.
    
    Returns:
        Dictionary with engine status information
    """
    engine = _get_engine()
    
    return {
        "model_loaded": engine.is_loaded,
        "model_name": engine.model_name,
        "device": engine.device,
        "supported_languages": engine.get_supported_languages(),
        "default_language": DEFAULT_LANGUAGE
    } 