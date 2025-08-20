#!/usr/bin/env python3  
"""
TalkBridge Animation -   Init   - Package Initialization
========================================================

Inicialización del paquete

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- mediapipe
- opencv-python
"""

from .audio_visualizer import AudioVisualizer
from .loading_animation import LoadingAnimation
from .interactive_animations import InteractiveAnimations
from .face_sync import FaceSync

__all__ = [
    'AudioVisualizer',
    'LoadingAnimation', 
    'InteractiveAnimations',
    'FaceSync'
] 