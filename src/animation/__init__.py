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

# Optional imports with graceful fallback
try:
    from .face_sync import FaceSync
    FACE_SYNC_AVAILABLE = True
except ImportError:
    FaceSync = None
    FACE_SYNC_AVAILABLE = False

try:
    from .camera_manager import CameraManager, create_camera_manager, get_best_camera
    CAMERA_AVAILABLE = True
except ImportError:
    CameraManager = None
    create_camera_manager = None
    get_best_camera = None
    CAMERA_AVAILABLE = False

__all__ = [
    'AudioVisualizer',
    'LoadingAnimation',
    'InteractiveAnimations',
    'FACE_SYNC_AVAILABLE',
    'CAMERA_AVAILABLE'
]

if FACE_SYNC_AVAILABLE:
    __all__.append('FaceSync')
    
if CAMERA_AVAILABLE:
    __all__.extend(['CameraManager', 'create_camera_manager', 'get_best_camera']) 