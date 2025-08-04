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
# - setup_voice_cloning: Set up voice cloning with reference samples
# - get_synthesis_info: Get information about the current synthesis setup
#-------------------------------------------------------------------------------------------------

from .voice_cloner import VoiceCloner
from .synthesizer import synthesize_voice, setup_voice_cloning, get_synthesis_info

__all__ = [
    'VoiceCloner', 
    'synthesize_voice',
    'setup_voice_cloning',
    'get_synthesis_info'
] 