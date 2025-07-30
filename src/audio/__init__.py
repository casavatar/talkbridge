#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: Audio Module
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - numpy Python package
# - sounddevice Python package
# - soundfile Python package
# - scipy Python package
# - seaborn Python package
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - AudioCapture: Audio capture class
# - AudioGenerator: Audio generation class
# - AudioSynthesizer: Audio synthesis class
# - AudioEffects: Audio effects class
# - AudioPlayer: Audio playback class
#----------------------------------------------------------------------------------------------------------------------------   

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