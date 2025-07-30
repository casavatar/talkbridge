#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: This script implements the configuration for the STT module.
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
# - get_model_name(): Get the name of the model
# - get_default_language(): Get the default language
# - get_supported_languages(): Get the supported languages
# - get_device(): Get the device
# - get_auto_device(): Get the auto device setting
# - get_sample_rate(): Get the sample rate
# - get_channels(): Get the channels
# - get_chunk_size(): Get the chunk size    
# - get_temp_audio_path(): Get the temporary audio path 
# - get_cache_dir(): Get the cache directory
# - get_batch_size(): Get the batch size
# - get_compute_type(): Get the compute type
# - get_load_model_on_startup(): Get the load model on startup setting
# - get_model_cache_enabled(): Get the model cache enabled setting
# - get_supported_formats(): Get the supported formats
# - get_max_audio_duration(): Get the maximum audio duration
# - get_log_level(): Get the log level
# - get_log_transcription(): Get the log transcription setting
# - get_retry_attempts(): Get the retry attempts
# - get_timeout_seconds(): Get the timeout seconds
# - get_confidence_threshold(): Get the confidence threshold
# - get_word_timestamps(): Get the word timestamps setting
# - get_language_detection(): Get the language detection setting
# - get_debug_mode(): Get the debug mode setting
# - get_save_audio_samples(): Get the save audio samples setting
#----------------------------------------------------------------------------------------------------------------------------

import os
from pathlib import Path

# Model Configuration
MODEL_NAME = "base"  # Options: "tiny", "base", "small", "medium", "large"
DEFAULT_LANGUAGE = "es"  # Default language for transcription
SUPPORTED_LANGUAGES = [
    "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
    "ar", "hi", "nl", "pl", "sv", "tr", "vi", "th", "cs", "da"
]

# Device Configuration
DEVICE = "cpu"  # Options: "cpu", "cuda", "mps" (for Apple Silicon)
AUTO_DEVICE = True  # Automatically detect best available device

# Audio Processing Settings
SAMPLE_RATE = 16000  # Standard sample rate for Whisper
CHANNELS = 1  # Mono audio
CHUNK_SIZE = 1024  # Audio chunk size for processing

# File Paths
TEMP_AUDIO_PATH = "tmp_input.wav"  # Temporary file for audio processing
CACHE_DIR = Path.home() / ".cache" / "talkbridge" / "whisper_models"

# Performance Settings
BATCH_SIZE = 1  # Number of audio segments to process at once
COMPUTE_TYPE = "float32"  # Precision for computation

# Model Loading Settings
LOAD_MODEL_ON_STARTUP = False  # Whether to load model immediately
MODEL_CACHE_ENABLED = True  # Cache downloaded models locally

# Audio Format Settings
SUPPORTED_FORMATS = [".wav", ".mp3", ".m4a", ".flac", ".ogg"]
MAX_AUDIO_DURATION = 300  # Maximum audio duration in seconds (5 minutes)

# Logging Settings
LOG_LEVEL = "INFO"  # Logging level for STT operations
LOG_TRANSCRIPTION = True  # Log transcription results

# Error Handling
RETRY_ATTEMPTS = 3  # Number of retry attempts for failed transcriptions
TIMEOUT_SECONDS = 30  # Timeout for transcription operations

# Quality Settings
CONFIDENCE_THRESHOLD = 0.0  # Minimum confidence score (0.0 to 1.0)
WORD_TIMESTAMPS = False  # Include word-level timestamps in output
LANGUAGE_DETECTION = True  # Enable automatic language detection

# Development Settings
DEBUG_MODE = False  # Enable debug mode for development
SAVE_AUDIO_SAMPLES = False  # Save audio samples for debugging


# Getter functions for configuration values
def get_model_name() -> str:
    """Get the name of the model."""
    return MODEL_NAME


def get_default_language() -> str:
    """Get the default language."""
    return DEFAULT_LANGUAGE


def get_supported_languages() -> list:
    """Get the supported languages."""
    return SUPPORTED_LANGUAGES.copy()


def get_device() -> str:
    """Get the device."""
    return DEVICE


def get_auto_device() -> bool:
    """Get the auto device setting."""
    return AUTO_DEVICE


def get_sample_rate() -> int:
    """Get the sample rate."""
    return SAMPLE_RATE


def get_channels() -> int:
    """Get the channels."""
    return CHANNELS


def get_chunk_size() -> int:
    """Get the chunk size."""
    return CHUNK_SIZE


def get_temp_audio_path() -> str:
    """Get the temporary audio path."""
    return TEMP_AUDIO_PATH


def get_cache_dir() -> Path:
    """Get the cache directory."""
    return CACHE_DIR


def get_batch_size() -> int:
    """Get the batch size."""
    return BATCH_SIZE


def get_compute_type() -> str:
    """Get the compute type."""
    return COMPUTE_TYPE


def get_load_model_on_startup() -> bool:
    """Get the load model on startup setting."""
    return LOAD_MODEL_ON_STARTUP


def get_model_cache_enabled() -> bool:
    """Get the model cache enabled setting."""
    return MODEL_CACHE_ENABLED


def get_supported_formats() -> list:
    """Get the supported formats."""
    return SUPPORTED_FORMATS.copy()


def get_max_audio_duration() -> int:
    """Get the maximum audio duration."""
    return MAX_AUDIO_DURATION


def get_log_level() -> str:
    """Get the log level."""
    return LOG_LEVEL


def get_log_transcription() -> bool:
    """Get the log transcription setting."""
    return LOG_TRANSCRIPTION


def get_retry_attempts() -> int:
    """Get the retry attempts."""
    return RETRY_ATTEMPTS


def get_timeout_seconds() -> int:
    """Get the timeout seconds."""
    return TIMEOUT_SECONDS


def get_confidence_threshold() -> float:
    """Get the confidence threshold."""
    return CONFIDENCE_THRESHOLD


def get_word_timestamps() -> bool:
    """Get the word timestamps setting."""
    return WORD_TIMESTAMPS


def get_language_detection() -> bool:
    """Get the language detection setting."""
    return LANGUAGE_DETECTION


def get_debug_mode() -> bool:
    """Get the debug mode setting."""
    return DEBUG_MODE


def get_save_audio_samples() -> bool:
    """Get the save audio samples setting."""
    return SAVE_AUDIO_SAMPLES 