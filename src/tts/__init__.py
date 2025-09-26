#! /usr/bin/env python3
"""
TalkBridge TTS -   Init   - Package Initialization
==================================================

Inicialización del paquete

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- TTS (optional)
"""

try:
    from .voice_cloner import VoiceCloner
    TTS_AVAILABLE = True
except ImportError:
    VoiceCloner = None
    TTS_AVAILABLE = False

from .synthesizer import synthesize_voice, setup_voice_cloning, get_synthesis_info

__all__ = [
    'synthesize_voice',
    'setup_voice_cloning',
    'get_synthesis_info',
    'TTS_AVAILABLE'
]

if TTS_AVAILABLE:
    __all__.append('VoiceCloner') 