"""
Audio Adapters for TalkBridge

This module provides adapter implementations that wrap existing engine classes
to conform to the port interfaces defined in ports.py.
"""

from .capture_adapter import AudioCaptureAdapter
from .stt_adapter import WhisperSTTAdapter
from .translation_adapter import TranslationAdapter
from .tts_adapter import TTSAdapter
from .player_adapter import AudioPlayerAdapter

__all__ = [
    'AudioCaptureAdapter',
    'WhisperSTTAdapter', 
    'TranslationAdapter',
    'TTSAdapter',
    'AudioPlayerAdapter'
]