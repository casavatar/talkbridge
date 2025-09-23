"""
TalkBridge - AI-powered Translation and Voice Communication Platform
====================================================================

A comprehensive platform for real-time speech translation, text-to-speech synthesis,
and AI-powered conversation bridging multiple languages and modalities.

Version: 0.1.0
Author: TalkBridge Team
"""

# Suppress noisy TensorFlow Lite warnings early
try:
    import absl.logging
    absl.logging.set_verbosity(absl.logging.ERROR)
except ImportError:
    # absl may not be available in all environments
    pass

# Also suppress other common ML warnings
try:
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Only errors
except:
    pass

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

# Configure exception handling to capture unhandled exceptions
import sys
import logging

# Initialize logging early to ensure error handler is ready
from .logging_config import configure_logging
configure_logging(development_mode=True)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions by logging them to errors.log"""
    logger = logging.getLogger("talkbridge")
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupts - they're user-initiated
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Set the exception handler
sys.excepthook = handle_exception

# Configure stderr redirection to capture external library errors
class StderrLogger:
    """Redirect stderr output to logger for external libraries like PortAudio/ALSA"""
    
    def __init__(self):
        self.logger = logging.getLogger("external_libs")
        self.original_stderr = sys.stderr
        
    def write(self, message):
        """Write stderr messages to logger"""
        if message.strip():
            # Filter out common noise but keep real errors
            msg = message.strip()
            if any(keyword in msg.lower() for keyword in [
                'error', 'failed', 'exception', 'warning', 'critical',
                'portaudio', 'alsa', 'tensorflow', 'invalid'
            ]):
                self.logger.error(msg)
                
    def flush(self):
        """Required for file-like interface"""
        pass
        
    def restore(self):
        """Restore original stderr"""
        sys.stderr = self.original_stderr

# Initialize stderr redirection
_stderr_logger = StderrLogger()
sys.stderr = _stderr_logger