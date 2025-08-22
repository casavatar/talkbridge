#!/usr/bin/env python3  
"""
TalkBridge Animation - Package Initialization
=============================================

Animation package with robust camera management and face tracking capabilities.

Author: TalkBridge Team
Date: 2025-08-21
Version: 1.1

Requirements:
- mediapipe
- opencv-python
- numpy
======================================================================
Modules:
- audio_visualizer: Audio visualization components
- loading_animation: Loading and progress animations  
- interactive_animations: Interactive animation elements
- face_sync: Face tracking and lip sync functionality
- camera_manager: Robust camera management system (NEW)
- camera_integration_example: Integration examples (NEW)
======================================================================
"""

from .audio_visualizer import AudioVisualizer
from .loading_animation import LoadingAnimation
from .interactive_animations import InteractiveAnimations
from .face_sync import FaceSync
from .camera_manager import CameraManager, create_camera_manager, get_best_camera

__all__ = [
    'AudioVisualizer',
    'LoadingAnimation', 
    'InteractiveAnimations',
    'FaceSync',
    'CameraManager',
    'create_camera_manager',
    'get_best_camera'
] 