#!/usr/bin/env python3
"""
TalkBridge Animation - Face Sync
================================

Face sync module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- mediapipe
- opencv-python
======================================================================
Functions:
- __init__: Initialize the face sync system.
- load_audio: Load audio file for lip sync.
- _extract_audio_features: Extract audio features for lip sync animation.
- detect_facial_landmarks: Detect facial landmarks using MediaPipe.
- _calculate_mouth_opening: Calculate mouth opening based on lip landmarks.
- _calculate_eye_blink: Calculate eye blink based on eye landmarks.
- update_animation_state: Update animation state based on audio features.
- get_frame: Get current frame from webcam or avatar.
- process_frame: Process frame with facial animation overlays.
- _draw_landmarks: Draw facial landmarks on frame.
======================================================================
"""

import cv2
import numpy as np
import mediapipe as mp
import pygame
import threading
import time
import logging
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path
import soundfile as sf
import librosa

# Configure logging
# Logging configuration is handled by src/desktop/logging_config.py
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

class FaceSync:
    """Real-time facial animation and lip sync class."""
    
    def __init__(self, use_webcam: bool = True, avatar_path: Optional[str] = None):
        """Initialize the face sync system."""
        self.use_webcam = use_webcam
        self.avatar_path = avatar_path
        self.is_running = False
        self.audio_data = None
        self.audio_sample_rate = None
        
        # Initialize MediaPipe face mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize video capture
        if use_webcam:
            try:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    self.logger.warning("Webcam not available, falling back to avatar mode")
                    self.use_webcam = False
                    self.cap = None
                    # Use default avatar if no avatar_path specified
                    if not avatar_path:
                        avatar_path = Path(__file__).parent / "resources" / "default_avatar.png"
                    if not Path(avatar_path).exists():
                        self.logger.error(f"Avatar image not found: {avatar_path}")
                        self.avatar_image = None
                    else:
                        self.avatar_image = cv2.imread(str(avatar_path))
                else:
                    self.logger.info("Webcam initialized successfully")
            except Exception as e:
                self.logger.error(f"Error initializing webcam: {e}")
                self.use_webcam = False
                self.cap = None
                self.avatar_image = None
        else:
            if not avatar_path or not Path(avatar_path).exists():
                self.logger.error(f"Avatar image not found: {avatar_path}")
                self.avatar_image = None
            else:
                self.avatar_image = cv2.imread(str(avatar_path))
            self.cap = None
        
        # Initialize pygame for audio
        pygame.mixer.init()
        
        # Facial landmark indices
        self.LIP_LANDMARKS = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        self.EYE_LANDMARKS = {
            'left_eye': [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387],
            'right_eye': [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158]
        }
        
        # Animation state
        self.animation_state = {
            'mouth_open': 0.0,
            'eye_blink': 0.0,
            'expression': 'neutral'
        }
    
    def load_audio(self, audio_path: str) -> bool:
        """Load audio file for lip sync."""
        try:
            logger.info(f"Loading audio: {audio_path}")
            self.audio_data, self.audio_sample_rate = librosa.load(audio_path, sr=None, mono=True)
            self.audio_features = self._extract_audio_features()
            return True
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            return False
    
    def _extract_audio_features(self) -> Dict[str, np.ndarray]:
        """Extract audio features for lip sync animation."""
        if self.audio_data is None:
            return {}
        
        frame_duration = 1.0 / 30.0  # 30 FPS
        samples_per_frame = int(self.audio_sample_rate * frame_duration)
        
        energy = []
        for i in range(0, len(self.audio_data), samples_per_frame):
            frame_data = self.audio_data[i:i + samples_per_frame]
            if len(frame_data) > 0:
                frame_energy = np.sqrt(np.mean(frame_data ** 2))
                energy.append(frame_energy)
            else:
                energy.append(0.0)
        
        energy = np.array(energy)
        if len(energy) > 0 and np.max(energy) > 0:
            energy = energy / np.max(energy)
        
        return {
            'energy': energy,
            'samples_per_frame': samples_per_frame,
            'total_frames': len(energy)
        }
    
    def detect_facial_landmarks(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """Detect facial landmarks using MediaPipe."""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                h, w = frame.shape[:2]
                landmark_coords = []
                
                for landmark in landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    z = landmark.z
                    landmark_coords.append((x, y, z))
                
                lip_landmarks = [landmark_coords[i] for i in self.LIP_LANDMARKS]
                left_eye_landmarks = [landmark_coords[i] for i in self.EYE_LANDMARKS['left_eye']]
                right_eye_landmarks = [landmark_coords[i] for i in self.EYE_LANDMARKS['right_eye']]
                
                mouth_open = self._calculate_mouth_opening(lip_landmarks)
                eye_blink = self._calculate_eye_blink(left_eye_landmarks)
                
                return {
                    'landmarks': landmark_coords,
                    'lip_landmarks': lip_landmarks,
                    'left_eye_landmarks': left_eye_landmarks,
                    'right_eye_landmarks': right_eye_landmarks,
                    'mouth_open': mouth_open,
                    'eye_blink': eye_blink
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Facial landmark detection failed: {e}")
            return None
    
    def _calculate_mouth_opening(self, lip_landmarks: List[Tuple[int, int, float]]) -> float:
        """Calculate mouth opening based on lip landmarks."""
        if len(lip_landmarks) < 4:
            return 0.0
        
        try:
            upper_lip_y = lip_landmarks[13][1] if len(lip_landmarks) > 13 else lip_landmarks[0][1]
            lower_lip_y = lip_landmarks[14][1] if len(lip_landmarks) > 14 else lip_landmarks[1][1]
            
            mouth_height = abs(upper_lip_y - lower_lip_y)
            normalized_opening = min(mouth_height / 100.0, 1.0)
            
            return normalized_opening
            
        except Exception as e:
            logger.warning(f"Mouth opening calculation failed: {e}")
            return 0.0
    
    def _calculate_eye_blink(self, eye_landmarks: List[Tuple[int, int, float]]) -> float:
        """Calculate eye blink based on eye landmarks."""
        if len(eye_landmarks) < 6:
            return 0.0
        
        try:
            p1, p2, p3, p4, p5, p6 = eye_landmarks[:6]
            
            A = np.linalg.norm(np.array(p2) - np.array(p6))
            B = np.linalg.norm(np.array(p3) - np.array(p5))
            C = np.linalg.norm(np.array(p1) - np.array(p4))
            
            ear = (A + B) / (2.0 * C)
            normalized_blink = max(0.0, min(1.0, (0.3 - ear) / 0.2))
            
            return normalized_blink
            
        except Exception as e:
            logger.warning(f"Eye blink calculation failed: {e}")
            return 0.0
    
    def update_animation_state(self, frame_index: int) -> Dict[str, Any]:
        """Update animation state based on audio features."""
        if not hasattr(self, 'audio_features') or frame_index >= len(self.audio_features.get('energy', [])):
            return self.animation_state
        
        energy = self.audio_features['energy'][frame_index]
        
        self.animation_state['mouth_open'] = min(1.0, energy * 2.0)
        
        # Natural blinking
        blink_interval = 3.0
        blink_duration = 0.15
        current_time = frame_index / 30.0
        
        if (current_time % blink_interval) < blink_duration:
            self.animation_state['eye_blink'] = 1.0
        else:
            self.animation_state['eye_blink'] = 0.0
        
        if energy > 0.7:
            self.animation_state['expression'] = 'speaking'
        elif energy > 0.3:
            self.animation_state['expression'] = 'neutral'
        else:
            self.animation_state['expression'] = 'quiet'
        
        return self.animation_state
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame from webcam or avatar."""
        if self.use_webcam and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                return frame
        elif not self.use_webcam and hasattr(self, 'avatar_image'):
            return self.avatar_image.copy()
        
        return None
    
    def process_frame(self, frame: np.ndarray, animation_state: Dict[str, Any]) -> np.ndarray:
        """Process frame with facial animation overlays."""
        try:
            landmarks_data = self.detect_facial_landmarks(frame)
            
            if landmarks_data:
                frame = self._draw_landmarks(frame, landmarks_data)
                frame = self._apply_lip_sync(frame, landmarks_data, animation_state)
                frame = self._apply_eye_blink(frame, landmarks_data, animation_state)
            
            return frame
            
        except Exception as e:
            logger.error(f"Frame processing failed: {e}")
            return frame
    
    def _draw_landmarks(self, frame: np.ndarray, landmarks_data: Dict[str, Any]) -> np.ndarray:
        """Draw facial landmarks on frame."""
        try:
            for landmark in landmarks_data['lip_landmarks']:
                cv2.circle(frame, (landmark[0], landmark[1]), 2, (0, 255, 0), -1)
            
            for landmark in landmarks_data['left_eye_landmarks']:
                cv2.circle(frame, (landmark[0], landmark[1]), 2, (255, 0, 0), -1)
            
            for landmark in landmarks_data['right_eye_landmarks']:
                cv2.circle(frame, (landmark[0], landmark[1]), 2, (255, 0, 0), -1)
            
            return frame
            
        except Exception as e:
            logger.warning(f"Landmark drawing failed: {e}")
            return frame
    
    def _apply_lip_sync(self, frame: np.ndarray, landmarks_data: Dict[str, Any], 
                        animation_state: Dict[str, Any]) -> np.ndarray:
        """Apply lip sync animation to frame."""
        try:
            mouth_open = animation_state['mouth_open']
            
            if mouth_open > 0.1:
                lip_landmarks = landmarks_data['lip_landmarks']
                if len(lip_landmarks) >= 4:
                    x_coords = [p[0] for p in lip_landmarks]
                    y_coords = [p[1] for p in lip_landmarks]
                    
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    cv2.rectangle(frame, (x_min-5, y_min-5), (x_max+5, y_max+5), 
                                (0, 255, 255), 2)
                    
                    cv2.putText(frame, f"Mouth: {mouth_open:.2f}", 
                              (x_min, y_min-10), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.5, (0, 255, 255), 1)
            
            return frame
            
        except Exception as e:
            logger.warning(f"Lip sync application failed: {e}")
            return frame
    
    def _apply_eye_blink(self, frame: np.ndarray, landmarks_data: Dict[str, Any], 
                         animation_state: Dict[str, Any]) -> np.ndarray:
        """Apply eye blink animation to frame."""
        try:
            eye_blink = animation_state['eye_blink']
            
            if eye_blink > 0.5:
                left_eye = landmarks_data['left_eye_landmarks']
                right_eye = landmarks_data['right_eye_landmarks']
                
                if len(left_eye) >= 4 and len(right_eye) >= 4:
                    for eye_landmarks in [left_eye, right_eye]:
                        x_coords = [p[0] for p in eye_landmarks]
                        y_coords = [p[1] for p in eye_landmarks]
                        
                        x_min, x_max = min(x_coords), max(x_coords)
                        y_min, y_max = min(y_coords), max(y_coords)
                        
                        cv2.rectangle(frame, (x_min-3, y_min-3), (x_max+3, y_max+3), 
                                    (255, 0, 255), 2)
            
            return frame
            
        except Exception as e:
            logger.warning(f"Eye blink application failed: {e}")
            return frame
    
    def run_face_sync(self, audio_path: str) -> bool:
        """Main function to run face sync with audio."""
        try:
            logger.info(f"Starting face sync with audio: {audio_path}")
            
            if not self.load_audio(audio_path):
                return False
            
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            audio_duration = len(self.audio_data) / self.audio_sample_rate
            total_frames = int(audio_duration * 30)  # 30 FPS
            frame_delay = 1.0 / 30.0
            
            logger.info(f"Audio duration: {audio_duration:.2f}s, Total frames: {total_frames}")
            
            self.is_running = True
            start_time = time.time()
            
            for frame_index in range(total_frames):
                if not self.is_running:
                    break
                
                frame = self.get_frame()
                if frame is None:
                    continue
                
                animation_state = self.update_animation_state(frame_index)
                processed_frame = self.process_frame(frame, animation_state)
                
                cv2.imshow('Face Sync', processed_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                elapsed_time = time.time() - start_time
                expected_time = frame_index * frame_delay
                if elapsed_time < expected_time:
                    time.sleep(expected_time - elapsed_time)
            
            pygame.mixer.music.stop()
            cv2.destroyAllWindows()
            self.is_running = False
            
            logger.info("Face sync completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Face sync failed: {e}")
            self.is_running = False
            return False
    
    def stop(self):
        """Stop the face sync process."""
        self.is_running = False
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        pygame.mixer.quit()
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop() 