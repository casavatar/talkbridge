"""
Animation module for TalkBridge application.

This module provides various animation capabilities including:
- Audio visualization animations
- Loading animations
- Interactive visualizations
- Real-time data animations
"""

from .audio_visualizer import AudioVisualizer
from .loading_animation import LoadingAnimation
from .interactive_animations import InteractiveAnimations

__all__ = [
    'AudioVisualizer',
    'LoadingAnimation', 
    'InteractiveAnimations'
] 