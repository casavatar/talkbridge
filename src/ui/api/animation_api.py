#! /usr/bin/env python3 
#-------------------------------------------------------------------------------------------------
# description: Animation API Module
#-------------------------------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#-------------------------------------------------------------------------------------------------

# requirements:
# - streamlit Python package
# - pathlib Python package
# - typing Python package
# - logging Python package
#-------------------------------------------------------------------------------------------------
# functions:
# - AnimationAPI: Animation API class
# - initialize_face_sync: Initialize face sync
# - start_animation: Start animation
# - stop_animation: Stop animation
# - get_animation_status: Get animation status
# - update_animation_settings: Update animation settings
# - detect_facial_landmarks: Detect facial landmarks
# - get_avatar_types: Get list of available avatar types
# - set_avatar_type: Set avatar type and path
# - check_webcam_availability: Check if webcam is available
# - get_animation_quality_score: Get animation quality score
# - get_current_settings: Get current animation settings
# - validate_audio_file: Validate audio file
#-------------------------------------------------------------------------------------------------

import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Add src to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from animation import FaceSync
    ANIMATION_AVAILABLE = True
except ImportError:
    logging.warning("Animation module not available")
    ANIMATION_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnimationAPI:
    """API interface for animation functionality."""
    
    def __init__(self):
        """Initialize the Animation API."""
        self.face_sync = None
        self.animation_settings = {
            "use_webcam": True,
            "avatar_path": None,
            "lip_sync": True,
            "eye_blink": True,
            "head_movement": False,
            "fps": 30
        }
        self.is_animating = False
    
    def initialize_face_sync(self, use_webcam: bool = True, avatar_path: str = None) -> bool:
        """
        Initialize the face sync system.
        
        Args:
            use_webcam: Whether to use webcam input
            avatar_path: Path to avatar image (if not using webcam)
            
        Returns:
            True if initialization successful
        """
        try:
            if not ANIMATION_AVAILABLE:
                logger.error("Animation module not available")
                return False
                
            self.face_sync = FaceSync(use_webcam=use_webcam, avatar_path=avatar_path)
            self.animation_settings["use_webcam"] = use_webcam
            self.animation_settings["avatar_path"] = avatar_path
            
            logger.info("Face sync initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize face sync: {e}")
            return False
    
    def start_animation(self, audio_path: str) -> bool:
        """
        Start facial animation with audio.
        
        Args:
            audio_path: Path to audio file for lip sync
            
        Returns:
            True if animation started successfully
        """
        try:
            if not self.face_sync:
                logger.error("Face sync not initialized")
                return False
            
            if not Path(audio_path).exists():
                logger.error(f"Audio file not found: {audio_path}")
                return False
            
            # Start animation
            success = self.face_sync.run_face_sync(audio_path)
            
            if success:
                self.is_animating = True
                logger.info("Animation started successfully")
            else:
                self.is_animating = False
                logger.error("Animation failed to start")
            
            return success
            
        except Exception as e:
            logger.error(f"Animation start failed: {e}")
            self.is_animating = False
            return False
    
    def stop_animation(self) -> None:
        """Stop the current animation."""
        try:
            if self.face_sync:
                self.face_sync.stop()
            
            self.is_animating = False
            logger.info("Animation stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop animation: {e}")
    
    def get_animation_status(self) -> Dict[str, Any]:
        """
        Get current animation status.
        
        Returns:
            Dictionary containing animation status
        """
        return {
            "is_animating": self.is_animating,
            "face_sync_available": self.face_sync is not None,
            "animation_settings": self.animation_settings,
            "webcam_available": self._check_webcam_availability()
        }
    
    def update_animation_settings(self, lip_sync: bool = True, eye_blink: bool = True,
                                head_movement: bool = False, fps: int = 30) -> None:
        """
        Update animation settings.
        
        Args:
            lip_sync: Enable lip sync
            eye_blink: Enable eye blinking
            head_movement: Enable head movement
            fps: Animation frame rate
        """
        self.animation_settings.update({
            "lip_sync": lip_sync,
            "eye_blink": eye_blink,
            "head_movement": head_movement,
            "fps": max(15, min(60, fps))  # Clamp FPS between 15 and 60
        })
        
        logger.info(f"Updated animation settings: {self.animation_settings}")
    
    def detect_facial_landmarks(self, frame_data: bytes = None) -> Optional[Dict[str, Any]]:
        """
        Detect facial landmarks from frame data.
        
        Args:
            frame_data: Frame data as bytes (optional)
            
        Returns:
            Facial landmark data or None if failed
        """
        try:
            if not self.face_sync:
                logger.error("Face sync not initialized")
                return None
            
            # Get current frame
            frame = self.face_sync.get_frame()
            if frame is None:
                logger.warning("No frame available for landmark detection")
                return None
            
            # Detect landmarks
            landmarks_data = self.face_sync.detect_facial_landmarks(frame)
            
            if landmarks_data:
                logger.info("Facial landmarks detected successfully")
                return landmarks_data
            else:
                logger.warning("No facial landmarks detected")
                return None
                
        except Exception as e:
            logger.error(f"Facial landmark detection failed: {e}")
            return None
    
    def get_avatar_types(self) -> list:
        """
        Get list of available avatar types.
        
        Returns:
            List of avatar type options
        """
        return [
            {"id": "webcam", "name": "Webcam", "description": "Real-time webcam input"},
            {"id": "static", "name": "Static Image", "description": "Static avatar image"},
            {"id": "animated", "name": "Animated Character", "description": "Animated character avatar"}
        ]
    
    def set_avatar_type(self, avatar_type: str, avatar_path: str = None) -> bool:
        """
        Set the avatar type and path.
        
        Args:
            avatar_type: Type of avatar to use
            avatar_path: Path to avatar file (for static/animated types)
            
        Returns:
            True if avatar set successfully
        """
        try:
            if avatar_type == "webcam":
                return self.initialize_face_sync(use_webcam=True)
            elif avatar_type in ["static", "animated"]:
                if not avatar_path or not Path(avatar_path).exists():
                    logger.error(f"Avatar file not found: {avatar_path}")
                    return False
                return self.initialize_face_sync(use_webcam=False, avatar_path=avatar_path)
            else:
                logger.error(f"Unknown avatar type: {avatar_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set avatar type: {e}")
            return False
    
    def _check_webcam_availability(self) -> bool:
        """
        Check if webcam is available.
        
        Returns:
            True if webcam is available
        """
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Webcam availability check failed: {e}")
            return False
    
    def get_animation_quality_score(self, landmarks_data: Dict[str, Any]) -> float:
        """
        Get a quality score for the animation based on landmark data.
        
        Args:
            landmarks_data: Facial landmark data
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            if not landmarks_data:
                return 0.0
            
            score = 0.0
            
            # Check if landmarks are detected
            if 'landmarks' in landmarks_data and landmarks_data['landmarks']:
                score += 0.3
            
            # Check lip landmarks
            if 'lip_landmarks' in landmarks_data and landmarks_data['lip_landmarks']:
                score += 0.2
            
            # Check eye landmarks
            if 'left_eye_landmarks' in landmarks_data and landmarks_data['left_eye_landmarks']:
                score += 0.2
            
            if 'right_eye_landmarks' in landmarks_data and landmarks_data['right_eye_landmarks']:
                score += 0.2
            
            # Check mouth opening value
            if 'mouth_open' in landmarks_data:
                mouth_open = landmarks_data['mouth_open']
                if 0.0 <= mouth_open <= 1.0:
                    score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Failed to calculate animation quality: {e}")
            return 0.5
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current animation settings.
        
        Returns:
            Dictionary containing current settings
        """
        return {
            "animation_settings": self.animation_settings,
            "is_animating": self.is_animating,
            "face_sync_available": self.face_sync is not None,
            "webcam_available": self._check_webcam_availability(),
            "avatar_types": self.get_avatar_types()
        }
    
    def validate_audio_file(self, audio_path: str) -> bool:
        """
        Validate audio file for animation.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if audio file is valid
        """
        try:
            if not audio_path:
                return False
            
            audio_file = Path(audio_path)
            if not audio_file.exists():
                return False
            
            # Check file size (reasonable limit)
            if audio_file.stat().st_size > 50 * 1024 * 1024:  # 50MB limit
                return False
            
            # Check file extension
            valid_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
            if audio_file.suffix.lower() not in valid_extensions:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Audio file validation failed: {e}")
            return False 