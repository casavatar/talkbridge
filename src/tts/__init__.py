#! /usr/bin/env python3
"""
TalkBridge TTS -   Init   - Package Initialization
==================================================

Inicialización del paquete

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- TTS
"""

from .voice_cloner import VoiceCloner
from .synthesizer import synthesize_voice, setup_voice_cloning, get_synthesis_info

__all__ = [
    'VoiceCloner', 
    'synthesize_voice',
    'setup_voice_cloning',
    'get_synthesis_info'
] 