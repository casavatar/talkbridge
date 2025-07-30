#! /usr/bin/env python3
#-------------------------------------------------------------------------------------------------
# description: TTS (Text-to-Speech) Module for Voice Cloning
#-------------------------------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#
# requirements:
# - voice_cloner.py
# - synthesizer.py
#-------------------------------------------------------------------------------------------------
# functions:
# - VoiceCloner: Voice cloning class
# - synthesize_voice: Main function to synthesize speech from text using voice cloning
#-------------------------------------------------------------------------------------------------

from .voice_cloner import VoiceCloner
from .synthesizer import synthesize_voice

__all__ = ['VoiceCloner', 'synthesize_voice'] 