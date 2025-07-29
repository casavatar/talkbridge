"""
Audio module for TalkBridge application.

This module provides comprehensive audio capabilities including:
- Audio capture and recording
- Audio synthesis and generation
- Audio processing and effects
- Audio playback and streaming
"""

from .capture import AudioCapture
from .generator import AudioGenerator
from .synthesizer import AudioSynthesizer
from .effects import AudioEffects
from .player import AudioPlayer

__all__ = [
    'AudioCapture',
    'AudioGenerator', 
    'AudioSynthesizer',
    'AudioEffects',
    'AudioPlayer'
] 