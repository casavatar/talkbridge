#!/usr/bin/env python3  
#----------------------------------------------------------------------------------------------------------------------------
# description: Animation module for TalkBridge application.
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - numpy Python package
# - matplotlib Python package
# - sounddevice Python package
# - soundfile Python package
# - scipy Python package
# - seaborn Python package
# - mediapipe Python package
# - opencv-python Python package
# - pygame Python package
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - AudioVisualizer: Audio visualization animations
# - LoadingAnimation: Loading animations
# - InteractiveAnimations: Interactive visualizations
# - FaceSync: Real-time facial animation and lip sync
#----------------------------------------------------------------------------------------------------------------------------

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