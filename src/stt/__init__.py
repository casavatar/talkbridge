#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: This script implements the main module for the STT module.
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#
# requirements:
# - whisper Python package
# - numpy Python package
# - sounddevice Python package
# - soundfile Python package
# - scipy Python package
# - matplotlib Python package
# - pandas Python package
# - seaborn Python package
# - dataclasses Python package
#----------------------------------------------------------------------------------------------------------------------------   
# functions:
# - transcribe_audio(): Transcribe audio bytes to text
# - transcribe_file(): Transcribe audio file to text
# - transcribe_with_metadata(): Transcribe audio with metadata
# - load_model(): Load Whisper model explicitly
# - unload_model(): Unload Whisper model
# - get_model_info(): Get model information
# - get_supported_languages(): Get list of supported languages
# - is_language_supported(): Check if a language is supported
# - is_model_ready(): Check if the model is ready
# - get_engine_status(): Get engine status
#----------------------------------------------------------------------------------------------------------------------------

# Import main public interface
from .interface import (
    transcribe_audio,
    transcribe_file,
    transcribe_with_metadata,
    load_model,
    unload_model,
    get_model_info,
    get_supported_languages,
    is_language_supported,
    is_model_ready,
    get_engine_status
)

# Import configuration
from .config import (
    MODEL_NAME,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    DEVICE,
    SAMPLE_RATE,
    CHANNELS,
    # Getter functions
    get_model_name,
    get_default_language,
    get_supported_languages,
    get_device,
    get_auto_device,
    get_sample_rate,
    get_channels,
    get_chunk_size,
    get_temp_audio_path,
    get_cache_dir,
    get_batch_size,
    get_compute_type,
    get_load_model_on_startup,
    get_model_cache_enabled,
    get_supported_formats,
    get_max_audio_duration,
    get_log_level,
    get_log_transcription,
    get_retry_attempts,
    get_timeout_seconds,
    get_confidence_threshold,
    get_word_timestamps,
    get_language_detection,
    get_debug_mode,
    get_save_audio_samples
)

# Import engine for advanced usage
from .whisper_engine import WhisperEngine, get_whisper_engine

# Import utilities for advanced usage
from .audio_utils import (
    validate_audio_bytes,
    validate_audio_file,
    save_audio_bytes_to_temp,
    preprocess_audio,
    cleanup_temp_file,
    create_test_audio,
    get_audio_info
)

# Package metadata
__version__ = "1.0.0"
__author__ = "TalkBridge Development Team"
__description__ = "Offline Speech-to-Text using Whisper"

# Public API
__all__ = [
    # Main transcription functions
    "transcribe_audio",
    "transcribe_file", 
    "transcribe_with_metadata",
    
    # Model management
    "load_model",
    "unload_model",
    "get_model_info",
    "is_model_ready",
    "get_engine_status",
    
    # Language support
    "get_supported_languages",
    "is_language_supported",
    
    # Configuration
    "MODEL_NAME",
    "DEFAULT_LANGUAGE", 
    "SUPPORTED_LANGUAGES",
    "DEVICE",
    "SAMPLE_RATE",
    "CHANNELS",
    
    # Configuration getters
    "get_model_name",
    "get_default_language",
    "get_device",
    "get_auto_device",
    "get_sample_rate",
    "get_channels",
    "get_chunk_size",
    "get_temp_audio_path",
    "get_cache_dir",
    "get_batch_size",
    "get_compute_type",
    "get_load_model_on_startup",
    "get_model_cache_enabled",
    "get_supported_formats",
    "get_max_audio_duration",
    "get_log_level",
    "get_log_transcription",
    "get_retry_attempts",
    "get_timeout_seconds",
    "get_confidence_threshold",
    "get_word_timestamps",
    "get_language_detection",
    "get_debug_mode",
    "get_save_audio_samples",
    
    # Advanced usage
    "WhisperEngine",
    "get_whisper_engine",
    
    # Utilities
    "validate_audio_bytes",
    "validate_audio_file",
    "save_audio_bytes_to_temp",
    "preprocess_audio",
    "cleanup_temp_file",
    "create_test_audio",
    "get_audio_info"
] 