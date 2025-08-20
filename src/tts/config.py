#! /usr/bin/env python3
"""
TalkBridge TTS - Config
=======================

Configuración del módulo

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- TTS
======================================================================
Functions:
- get_config: Get the complete configuration dictionary.
- get_model_config: Get configuration for a specific model.
- update_config: Update configuration with new values.
- create_directories: Create necessary directories for the TTS module.
- validate_config: Validate the current configuration.
======================================================================
"""

import os
from typing import Dict, Any

# Default TTS model configuration
DEFAULT_MODEL = "tts_models/multilingual/multi-dataset/your_tts"

# Audio configuration
AUDIO_CONFIG = {
    "sample_rate": 22050,
    "bit_depth": 16,
    "channels": 1,
    "format": "wav"
}

# Voice cloning configuration
VOICE_CLONING_CONFIG = {
    "min_sample_duration": 1.0,  # Minimum duration in seconds
    "max_sample_duration": 30.0,  # Maximum duration in seconds
    "preferred_sample_duration": 5.0,  # Preferred duration in seconds
    "supported_formats": [".wav", ".mp3", ".flac", ".m4a"],
    "min_samples": 1,
    "max_samples": 5
}

# Performance configuration
PERFORMANCE_CONFIG = {
    "use_gpu": True,
    "batch_size": 1,
    "max_text_length": 500,  # Maximum characters per synthesis
    "enable_caching": True,
    "cache_size": 10  # Number of cached results
}

# Language configuration
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish", 
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese"
}

# Error handling configuration
ERROR_CONFIG = {
    "retry_attempts": 3,
    "retry_delay": 1.0,  # seconds
    "log_level": "INFO",
    "raise_exceptions": True
}

# File paths configuration
PATHS_CONFIG = {
    "model_cache_dir": os.path.expanduser("~/.cache/tts_models"),
    "temp_dir": os.path.join(os.getcwd(), "temp"),
    "output_dir": os.path.join(os.getcwd(), "output")
}

# Model-specific configurations
MODEL_CONFIGS = {
    "tts_models/multilingual/multi-dataset/your_tts": {
        "supports_voice_cloning": True,
        "supports_multilingual": True,
        "default_language": "en",
        "max_text_length": 500
    },
    "tts_models/en/ljspeech/tacotron2-DDC": {
        "supports_voice_cloning": False,
        "supports_multilingual": False,
        "default_language": "en",
        "max_text_length": 1000
    }
}

def get_config() -> Dict[str, Any]:
    """
    Get the complete configuration dictionary.
    
    Returns:
        Dict[str, Any]: Complete configuration dictionary
    """
    return {
        "default_model": DEFAULT_MODEL,
        "audio": AUDIO_CONFIG,
        "voice_cloning": VOICE_CLONING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "languages": SUPPORTED_LANGUAGES,
        "error_handling": ERROR_CONFIG,
        "paths": PATHS_CONFIG,
        "models": MODEL_CONFIGS
    }

def get_model_config(model_name: str = None) -> Dict[str, Any]:
    """
    Get configuration for a specific model.
    
    Args:
        model_name: Name of the model. If None, uses default model.
        
    Returns:
        Dict[str, Any]: Model-specific configuration
    """
    if model_name is None:
        model_name = DEFAULT_MODEL
    
    return MODEL_CONFIGS.get(model_name, MODEL_CONFIGS[DEFAULT_MODEL])

def update_config(updates: Dict[str, Any]) -> None:
    """
    Update configuration with new values.
    
    Args:
        updates: Dictionary of configuration updates
    """
    global DEFAULT_MODEL, AUDIO_CONFIG, VOICE_CLONING_CONFIG, PERFORMANCE_CONFIG
    
    if "default_model" in updates:
        DEFAULT_MODEL = updates["default_model"]
    
    if "audio" in updates:
        AUDIO_CONFIG.update(updates["audio"])
    
    if "voice_cloning" in updates:
        VOICE_CLONING_CONFIG.update(updates["voice_cloning"])
    
    if "performance" in updates:
        PERFORMANCE_CONFIG.update(updates["performance"])

def create_directories() -> None:
    """Create necessary directories for the TTS module."""
    paths = PATHS_CONFIG.values()
    for path in paths:
        if path and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

def validate_config() -> bool:
    """
    Validate the current configuration.
    
    Returns:
        bool: True if configuration is valid
    """
    try:
        # Check if default model exists in model configs
        if DEFAULT_MODEL not in MODEL_CONFIGS:
            return False
        
        # Check if sample rate is valid
        if AUDIO_CONFIG["sample_rate"] <= 0:
            return False
        
        # Check if performance settings are valid
        if PERFORMANCE_CONFIG["batch_size"] <= 0:
            return False
        
        return True
        
    except Exception:
        return False 