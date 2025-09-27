#!/usr/bin/env python3
"""
Config
======================================================================

Module configuration

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- None
======================================================================
Functions:
- get_config: Get configuration for a specific environment.
- ensure_directories: Ensure all required directories exist.
- get_path: Get a path from PATH_CONFIG.
- get_setting: Get a setting from a specific configuration category.
- is_demo_mode: Check if demo mode is enabled.
- is_debug_mode: Check if debug mode is enabled.
- is_development_mode: Check if development mode is enabled.
======================================================================
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from .logging_config import get_logger

logger = get_logger(__name__)


def _get_required_env_var(var_name: str) -> str:
    """
    Get a required environment variable or raise an error.

    This function ensures that critical security settings like session secrets
    are not allowed to have unsafe defaults.

    Args:
        var_name: Name of the environment variable

    Returns:
        Value of the environment variable

    Raises:
        RuntimeError: If the environment variable is not set
    """
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(
            f"CRITICAL SECURITY ERROR: Required environment variable '{var_name}' is not set. "
            f"This is required for secure operation and has no default value. "
            f"Please set this environment variable before starting the application."
        )
    return value


def _generate_session_secret() -> str:
    """
    Generate a secure session secret if none is provided.

    This is a fallback for development only and should never be used in production.

    Returns:
        A cryptographically secure random session secret
    """
    import secrets
    import warnings

    warnings.warn(
        "SECURITY WARNING: Generating random session secret because SESSION_SECRET "
        "environment variable is not set. This is only acceptable for development. "
        "In production, you MUST set SESSION_SECRET environment variable.",
        RuntimeWarning,
        stacklevel=2
    )

    # Generate 64 bytes of random data and encode as hex
    return secrets.token_hex(64)


# Get the project root directory using robust resolver
from .utils.project_root import get_project_root, get_data_dir

PROJECT_ROOT = get_project_root()
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = get_data_dir()  # Uses environment override if available
DOCS_DIR = PROJECT_ROOT / "doc"
TEST_DIR = PROJECT_ROOT / "test"

# System Configuration
SYSTEM_CONFIG = {
    # Application settings
    "app_name": "TalkBridge",
    "app_version": "1.0.0",
    "app_description": "Offline AI Voice Assistant",
    
    # Debug and logging
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    
    # Demo mode (FIXED: was inverted logic)
    "demo_mode": os.getenv("DEMO_MODE", "false").lower() == "true",
    "demo_files_dir": SRC_DIR / "demo" / "samples",
    
    # Performance settings
    "max_workers": int(os.getenv("MAX_WORKERS", "4")),
    "chunk_size": int(os.getenv("CHUNK_SIZE", "1024")),
    "buffer_size": int(os.getenv("BUFFER_SIZE", "4096")),
    
    # Timeout settings
    "request_timeout": float(os.getenv("REQUEST_TIMEOUT", "30.0")),
    "audio_timeout": float(os.getenv("AUDIO_TIMEOUT", "10.0")),
    "model_timeout": float(os.getenv("MODEL_TIMEOUT", "60.0")),
}

# Path Configuration
PATH_CONFIG = {
    # Core directories
    "project_root": PROJECT_ROOT,
    "src_dir": SRC_DIR,
    "data_dir": DATA_DIR,
    "docs_dir": DOCS_DIR,
    "test_dir": TEST_DIR,
    
    # Data subdirectories
    "audio_dir": DATA_DIR / "audio",
    "models_dir": DATA_DIR / "models",
    "avatars_dir": DATA_DIR / "avatars",
    "logs_dir": DATA_DIR / "logs",
    "temp_dir": DATA_DIR / "temp",
    
    # Module directories
    "audio_module": SRC_DIR / "audio",
    "ollama_module": SRC_DIR / "ollama",
    "translation_module": SRC_DIR / "translation",
    "animation_module": SRC_DIR / "animation",
    "ui_module": SRC_DIR / "ui",
    "demo_module": SRC_DIR / "demo",
    "demo_files_dir": SRC_DIR / "demo" / "samples",
    "utils_module": SRC_DIR / "utils",
    
    # Configuration files
    "config_file": SRC_DIR / "config.py",
    "requirements_file": PROJECT_ROOT / "requirements.txt",
    "readme_file": PROJECT_ROOT / "README.md",
    
    # Log files
    "app_log": DATA_DIR /  "logs"  / "app.log",
    "error_log": DATA_DIR / "logs" / "errors.log",
    "demo_log": DATA_DIR / "logs" / "demo.log",
    "conversation_log": DATA_DIR / "logs" / "conversations.jsonl",
}

# Audio Configuration
AUDIO_CONFIG = {
    # Audio capture settings
    "sample_rate": int(os.getenv("SAMPLE_RATE", "22050")),
    "channels": int(os.getenv("AUDIO_CHANNELS", "1")),
    "chunk_duration": float(os.getenv("CHUNK_DURATION", "5.0")),
    "format": os.getenv("AUDIO_FORMAT", "wav"),
    "bit_depth": int(os.getenv("AUDIO_BIT_DEPTH", "16")),
    
    # Audio processing
    "noise_reduction": os.getenv("NOISE_REDUCTION", "true").lower() == "true",
    "echo_cancellation": os.getenv("ECHO_CANCELLATION", "true").lower() == "true",
    "normalization": os.getenv("AUDIO_NORMALIZATION", "true").lower() == "true",
    
    # Audio devices
    "input_device": os.getenv("AUDIO_INPUT_DEVICE", "default"),
    "output_device": os.getenv("AUDIO_OUTPUT_DEVICE", "default"),
    "auto_detect_devices": os.getenv("AUTO_DETECT_DEVICES", "true").lower() == "true",
}

# STT (Speech-to-Text) Configuration
STT_CONFIG = {
    # Model settings
    "model_name": os.getenv("STT_MODEL", "whisper-1"),
    "model_size": os.getenv("STT_MODEL_SIZE", "base"),
    "language": os.getenv("STT_LANGUAGE", "en"),
    
    # Processing settings
    "chunk_length": int(os.getenv("STT_CHUNK_LENGTH", "30")),
    "overlap": int(os.getenv("STT_OVERLAP", "5")),
    "temperature": float(os.getenv("STT_TEMPERATURE", "0.0")),
    
    # Performance settings
    "use_gpu": os.getenv("STT_USE_GPU", "false").lower() == "true",
    "batch_size": int(os.getenv("STT_BATCH_SIZE", "1")),
    "num_workers": int(os.getenv("STT_NUM_WORKERS", "1")),
}

# TTS (Text-to-Speech) Configuration
TTS_CONFIG = {
    # Model settings
    "model_name": os.getenv("TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC"),
    "voice_cloning": os.getenv("TTS_VOICE_CLONING", "true").lower() == "true",
    "voice_samples_dir": DATA_DIR / "voice_samples",
    
    # Synthesis settings
    "speaking_rate": float(os.getenv("TTS_SPEAKING_RATE", "1.0")),
    "pitch": float(os.getenv("TTS_PITCH", "0.0")),
    "volume": float(os.getenv("TTS_VOLUME", "1.0")),
    
    # Performance settings
    "use_gpu": os.getenv("TTS_USE_GPU", "false").lower() == "true",
    "batch_size": int(os.getenv("TTS_BATCH_SIZE", "1")),
    "num_workers": int(os.getenv("TTS_NUM_WORKERS", "1")),
}

# LLM (Language Model) Configuration
LLM_CONFIG = {
    # Model settings
    "model_name": os.getenv("LLM_MODEL", "llama2"),
    "model_size": os.getenv("LLM_MODEL_SIZE", "7b"),
    "context_length": int(os.getenv("LLM_CONTEXT_LENGTH", "4096")),
    
    # Generation settings
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "512")),
    "top_p": float(os.getenv("LLM_TOP_P", "0.9")),
    "top_k": int(os.getenv("LLM_TOP_K", "40")),
    
    # Ollama settings
    "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    "ollama_timeout": float(os.getenv("OLLAMA_TIMEOUT", "30.0")),
    "streaming": os.getenv("LLM_STREAMING", "true").lower() == "true",
}

# Translation Configuration
TRANSLATION_CONFIG = {
    # Model settings
    "model_name": os.getenv("TRANSLATION_MODEL", "Helsinki-NLP/opus-mt-en-es"),
    "source_language": os.getenv("SOURCE_LANGUAGE", "en"),
    "target_language": os.getenv("TARGET_LANGUAGE", "es"),
    
    # Processing settings
    "batch_size": int(os.getenv("TRANSLATION_BATCH_SIZE", "1")),
    "max_length": int(os.getenv("TRANSLATION_MAX_LENGTH", "512")),
    "use_gpu": os.getenv("TRANSLATION_USE_GPU", "false").lower() == "true",
    
    # Supported languages
    "supported_languages": ["en", "es", "fr", "de", "it", "pt"],
}

# Animation Configuration
ANIMATION_CONFIG = {
    # Avatar settings
    "avatar_type": os.getenv("AVATAR_TYPE", "static"),  # static, webcam, animated
    "avatar_path": DATA_DIR / "avatars" / "default_avatar.jpg",
    "webcam_device": int(os.getenv("WEBCAM_DEVICE", "0")),
    
    # Animation settings
    "fps": int(os.getenv("ANIMATION_FPS", "30")),
    "resolution": tuple(map(int, os.getenv("ANIMATION_RESOLUTION", "640,480").split(","))),
    "lip_sync": os.getenv("LIP_SYNC", "true").lower() == "true",
    "eye_blink": os.getenv("EYE_BLINK", "true").lower() == "true",
    
    # Performance settings
    "use_gpu": os.getenv("ANIMATION_USE_GPU", "false").lower() == "true",
    "buffer_size": int(os.getenv("ANIMATION_BUFFER_SIZE", "10")),
}

# Web Interface Configuration
UI_CONFIG = {
    # Server settings
    "host": os.getenv("UI_HOST", "localhost"),
    "port": int(os.getenv("UI_PORT", "8501")),
    "debug": os.getenv("UI_DEBUG", "false").lower() == "true",
    
    # Authentication settings
    "auth_enabled": os.getenv("AUTH_ENABLED", "true").lower() == "true",
    "session_timeout": int(os.getenv("SESSION_TIMEOUT", "3600")),
    "max_login_attempts": int(os.getenv("MAX_LOGIN_ATTEMPTS", "3")),
    
    # UI settings
    "theme": os.getenv("UI_THEME", "light"),
    "sidebar_state": os.getenv("SIDEBAR_STATE", "expanded"),
    "page_title": "TalkBridge - Offline AI Voice Assistant",
    
    # File paths
    "css_file": SRC_DIR / "ui" / "assets" / "style.css",
    # Note: users.json is deprecated - authentication now uses secure SQLite database
    # "users_file": SRC_DIR / "json" / "users.json",  # DEPRECATED
}

# Demo Configuration
DEMO_CONFIG = {
    # Demo mode settings
    "enabled": SYSTEM_CONFIG["demo_mode"],
    "simulate_delays": os.getenv("DEMO_SIMULATE_DELAYS", "true").lower() == "true",
    
    # Delay settings (seconds)
    "delay_audio_processing": float(os.getenv("DEMO_AUDIO_DELAY", "1.5")),
    "delay_transcription": float(os.getenv("DEMO_TRANSCRIPTION_DELAY", "2.0")),
    "delay_translation": float(os.getenv("DEMO_TRANSLATION_DELAY", "1.0")),
    "delay_llm_response": float(os.getenv("DEMO_LLM_DELAY", "3.0")),
    "delay_voice_synthesis": float(os.getenv("DEMO_TTS_DELAY", "2.5")),
    "delay_avatar_animation": float(os.getenv("DEMO_ANIMATION_DELAY", "0.5")),
    
    # Demo files
    "input_audio_file": PATH_CONFIG["demo_files_dir"] / "input_audio.wav",
    "transcribed_file": PATH_CONFIG["demo_files_dir"] / "transcribed.txt",
    "translation_file": PATH_CONFIG["demo_files_dir"] / "translation.txt",
    "response_file": PATH_CONFIG["demo_files_dir"] / "response.txt",
    "voice_output_file": PATH_CONFIG["demo_files_dir"] / "voice_output.wav",
    "avatar_file": PATH_CONFIG["demo_files_dir"] / "mock_avatar.jpg",
}

# Security Configuration
SECURITY_CONFIG = {
    # Password settings (INCREASED minimum length for security)
    "password_min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "16")),
    "password_require_special": os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true",
    "password_require_numbers": os.getenv("PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true",
    
    # Session settings (SECURE: Generate if not provided, warn about insecurity)
    "session_secret": os.getenv("SESSION_SECRET") or _generate_session_secret(),
    "session_timeout": int(os.getenv("SESSION_TIMEOUT", "3600")),
    "max_sessions_per_user": int(os.getenv("MAX_SESSIONS_PER_USER", "1")),
    
    # File permissions
    "log_file_permissions": 0o600,
    "config_file_permissions": 0o644,
    "data_file_permissions": 0o644,
}

# Development Configuration
DEV_CONFIG = {
    # Development settings
    "development_mode": os.getenv("DEVELOPMENT_MODE", "false").lower() == "true",
    "auto_reload": os.getenv("AUTO_RELOAD", "true").lower() == "true",
    "verbose_logging": os.getenv("VERBOSE_LOGGING", "false").lower() == "true",
    
    # Testing settings
    "test_mode": os.getenv("TEST_MODE", "false").lower() == "true",
    "test_data_dir": TEST_DIR / "data",
    "test_logs_dir": TEST_DIR / "logs",
    
    # Debug settings
    "debug_audio": os.getenv("DEBUG_AUDIO", "false").lower() == "true",
    "debug_models": os.getenv("DEBUG_MODELS", "false").lower() == "true",
    "debug_ui": os.getenv("DEBUG_UI", "false").lower() == "true",
}

# Environment-specific configurations
def get_config(env: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration for a specific environment.
    
    Args:
        env: Environment name (development, production, testing)
    
    Returns:
        Dictionary containing environment-specific configuration
    """
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")
    
    base_config = {
        "system": SYSTEM_CONFIG,
        "paths": PATH_CONFIG,
        "audio": AUDIO_CONFIG,
        "stt": STT_CONFIG,
        "tts": TTS_CONFIG,
        "llm": LLM_CONFIG,
        "translation": TRANSLATION_CONFIG,
        "animation": ANIMATION_CONFIG,
        "ui": UI_CONFIG,
        "demo": DEMO_CONFIG,
        "security": SECURITY_CONFIG,
        "dev": DEV_CONFIG,
    }
    
    if env == "production":
        # Production overrides
        base_config["system"]["debug"] = False
        base_config["system"]["log_level"] = "WARNING"
        base_config["ui"]["debug"] = False
        base_config["dev"]["development_mode"] = False
        base_config["dev"]["auto_reload"] = False
    
    elif env == "testing":
        # Testing overrides
        base_config["system"]["demo_mode"] = True
        base_config["system"]["log_level"] = "DEBUG"
        base_config["ui"]["auth_enabled"] = False
        base_config["dev"]["test_mode"] = True
    
    return base_config

# Utility functions
def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        PATH_CONFIG["data_dir"],
        PATH_CONFIG["logs_dir"],
        PATH_CONFIG["audio_dir"],
        PATH_CONFIG["models_dir"],
        PATH_CONFIG["avatars_dir"],
        PATH_CONFIG["temp_dir"],
        PATH_CONFIG["demo_files_dir"],
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_path(key: str) -> Path:
    """Get a path from PATH_CONFIG."""
    return PATH_CONFIG.get(key, Path())

def get_setting(category: str, key: str, default: Any = None) -> Any:
    """Get a setting from a specific configuration category."""
    config_map = {
        "system": SYSTEM_CONFIG,
        "audio": AUDIO_CONFIG,
        "stt": STT_CONFIG,
        "tts": TTS_CONFIG,
        "llm": LLM_CONFIG,
        "translation": TRANSLATION_CONFIG,
        "animation": ANIMATION_CONFIG,
        "ui": UI_CONFIG,
        "demo": DEMO_CONFIG,
        "security": SECURITY_CONFIG,
        "dev": DEV_CONFIG,
    }
    
    config = config_map.get(category, {})
    return config.get(key, default)

def is_demo_mode() -> bool:
    """Check if demo mode is enabled."""
    return SYSTEM_CONFIG["demo_mode"]

def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return SYSTEM_CONFIG["debug"]

def is_development_mode() -> bool:
    """Check if development mode is enabled."""
    return DEV_CONFIG["development_mode"]

# Initialize configuration
if __name__ == "__main__":
    # Ensure directories exist
    ensure_directories()
    
    # Print configuration summary
    logger.info("TalkBridge Configuration")
    logger.info(f"Project Root: {PROJECT_ROOT}")
    logger.info(f"Demo Mode: {is_demo_mode()}")
    logger.info(f"Debug Mode: {is_debug_mode()}")
    logger.info(f"Development Mode: {is_development_mode()}")
    logger.info(f"Log Level: {SYSTEM_CONFIG['log_level']}")
    logger.info(f"Audio Sample Rate: {AUDIO_CONFIG['sample_rate']}")
    logger.info(f"UI Port: {UI_CONFIG['port']}")
    logger.info("=" * 40) 