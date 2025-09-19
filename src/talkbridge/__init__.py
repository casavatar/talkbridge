"""
TalkBridge - AI-powered Translation and Voice Communication Platform
====================================================================

A comprehensive platform for real-time speech translation, text-to-speech synthesis,
and AI-powered conversation bridging multiple languages and modalities.

Version: 0.1.0
Author: TalkBridge Team
"""

__version__ = "0.1.0"
__author__ = "TalkBridge Team"

# Core modules - these should always be available
from . import auth
from . import stt
from . import translation
from . import web
from . import utils
from . import ollama

# Optional modules with graceful fallback
try:
    from . import audio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    from . import desktop
    DESKTOP_AVAILABLE = True
except ImportError:
    DESKTOP_AVAILABLE = False

try:
    from . import tts
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Application entry point - make optional for now
try:
    from .app import main as run_app
    APP_AVAILABLE = True
except ImportError:
    run_app = None
    APP_AVAILABLE = False

__all__ = [
    'auth',
    'stt', 
    'translation',
    'ui',
    'utils',
    'ollama',
    'AUDIO_AVAILABLE',
    'DESKTOP_AVAILABLE', 
    'TTS_AVAILABLE',
    'APP_AVAILABLE',
    '__version__',
    '__author__'
]

# Add optional modules if available
if AUDIO_AVAILABLE:
    __all__.append('audio')
if DESKTOP_AVAILABLE:
    __all__.append('desktop')
if TTS_AVAILABLE:
    __all__.append('tts')
if APP_AVAILABLE:
    __all__.append('run_app')