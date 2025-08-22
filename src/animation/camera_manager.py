#!/usr/bin/env python3
"""
TalkBridge Animation - Camera Manager
====================================

Specialized camera management system for animation modules.
Consolidates all camera-related functionality with robust error handling.

Author: TalkBridge Team
Date: 2025-08-21
Version: 1.0

Requirements:
- opencv-python
- numpy
- mediapipe
======================================================================
Features:
- Robust camera detection and initialization
- Multiple camera backend support (V4L2, DirectShow, etc.)
- Automatic fallback handling for missing cameras
- Camera health monitoring and recovery
- Frame processing optimization for animation
- MediaPipe integration for face tracking
- Thread-safe camera operations
======================================================================
"""

import cv2
import numpy as np
import threading
import time
import logging
from typing import Optional, Tuple, List, Dict, Any, Callable
from pathlib import Path
from contextlib import contextmanager
import sys

# Import camera utilities from error_suppression
sys.path.append(str(Path(__file__).parent.parent))
from utils.error_suppression import (
    configure_camera_fallback,
    find_available_cameras,
    create_robust_camera_capture,
    suppress_ml_warnings
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraManager:
    """
    Advanced camera management system for animation applications.
    
    Provides robust camera handling with automatic fallback, health monitoring,
    and optimized frame processing for real-time animation applications.
    """
    
    def __init__(self, 
                 preferred_index: int = 0,
                 fallback_avatar_path: Optional[str] = None,
                 auto_retry: bool = True,
                 health_check_interval: float = 5.0):
        """
        Initialize the camera manager.
        
        Args:
            preferred_index: Preferred camera index to use
            fallback_avatar_path: Path to fallback avatar image when no camera is available
            auto_retry: Whether to automatically retry camera connection on failure
            health_check_interval: Interval in seconds for camera health checks
        """
        # Initialize error suppression early
        suppress_ml_warnings()
        configure_camera_fallback()
        
        self.preferred_index = preferred_index
        self.fallback_avatar_path = fallback_avatar_path
        self.auto_retry = auto_retry
        self.health_check_interval = health_check_interval
        
        # Camera state
        self.cap = None
        self.current_index = -1
        self.is_camera_active = False
        self.fallback_image = None
        self.available_cameras = []
        
        # Frame processing
        self.last_frame = None
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # Threading
        self.lock = threading.RLock()
        self.health_check_thread = None
        self.health_check_running = False
        
        # Frame callbacks
        self.frame_processors: List[Callable] = []
        
        # Statistics
        self.stats = {
            'total_frames': 0,
            'failed_reads': 0,
            'camera_switches': 0,
            'uptime_start': time.time(),
            'last_successful_read': None
        }
        
        logger.info("Camera Manager initialized")
        self._initialize_camera_system()
    
    def _initialize_camera_system(self):
        """Initialize the complete camera system."""
        logger.info("Initializing camera system...")
        
        # Discover available cameras
        self.available_cameras = find_available_cameras(max_cameras=10)
        logger.info(f"Available cameras: {self.available_cameras}")
        
        # Load fallback avatar if specified
        self._load_fallback_avatar()
        
        # Attempt to initialize camera
        if self.available_cameras:
            self._connect_camera()
        else:
            logger.warning("No cameras available, using fallback mode")
            self.is_camera_active = False
        
        # Start health monitoring if auto_retry is enabled
        if self.auto_retry:
            self._start_health_monitoring()
    
    def _load_fallback_avatar(self):
        """Load fallback avatar image."""
        if self.fallback_avatar_path:
            avatar_path = Path(self.fallback_avatar_path)
            if avatar_path.exists():
                try:
                    self.fallback_image = cv2.imread(str(avatar_path))
                    if self.fallback_image is not None:
                        logger.info(f"Fallback avatar loaded: {avatar_path}")
                    else:
                        logger.error(f"Failed to load avatar image: {avatar_path}")
                except Exception as e:
                    logger.error(f"Error loading avatar: {e}")
            else:
                logger.warning(f"Avatar path does not exist: {avatar_path}")
        
        # Create default fallback if no avatar provided
        if self.fallback_image is None:
            logger.info("Creating default fallback image")
            self.fallback_image = self._create_default_avatar()
    
    def _create_default_avatar(self) -> np.ndarray:
        """Create a default avatar image."""
        # Create a simple 640x480 avatar with a face placeholder
        avatar = np.zeros((480, 640, 3), dtype=np.uint8)
        avatar.fill(64)  # Dark gray background
        
        # Draw a simple face
        center = (320, 240)
        # Face circle
        cv2.circle(avatar, center, 100, (100, 100, 100), -1)
        # Eyes
        cv2.circle(avatar, (280, 200), 15, (255, 255, 255), -1)
        cv2.circle(avatar, (360, 200), 15, (255, 255, 255), -1)
        cv2.circle(avatar, (280, 200), 8, (0, 0, 0), -1)
        cv2.circle(avatar, (360, 200), 8, (0, 0, 0), -1)
        # Mouth
        cv2.ellipse(avatar, (320, 280), (30, 15), 0, 0, 180, (255, 255, 255), 2)
        
        # Add text
        cv2.putText(avatar, "TalkBridge Avatar", (200, 400), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return avatar
    
    def _connect_camera(self) -> bool:
        """Connect to the best available camera."""
        with self.lock:
            # Release existing camera
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            
            # Try to create robust camera capture
            cap, index = create_robust_camera_capture(self.preferred_index)
            
            if cap is not None:
                self.cap = cap
                self.current_index = index
                self.is_camera_active = True
                
                # Configure camera properties for optimal performance
                self._optimize_camera_settings()
                
                logger.info(f"Camera connected successfully on index {index}")
                self.stats['camera_switches'] += 1
                return True
            else:
                logger.warning("Failed to connect to any camera")
                self.is_camera_active = False
                return False
    
    def _optimize_camera_settings(self):
        """Optimize camera settings for animation performance."""
        if self.cap is None:
            return
        
        try:
            # Set optimal resolution for real-time processing
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Set frame rate
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Reduce buffer size for lower latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Auto exposure and white balance for consistent lighting
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
            self.cap.set(cv2.CAP_PROP_AUTO_WB, 1)
            
            logger.info("Camera settings optimized for animation")
            
        except Exception as e:
            logger.warning(f"Could not optimize camera settings: {e}")
    
    def _start_health_monitoring(self):
        """Start camera health monitoring thread."""
        if self.health_check_thread is not None:
            return
        
        self.health_check_running = True
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True,
            name="CameraHealthMonitor"
        )
        self.health_check_thread.start()
        logger.info("Camera health monitoring started")
    
    def _health_check_loop(self):
        """Health check loop running in background thread."""
        while self.health_check_running:
            try:
                time.sleep(self.health_check_interval)
                
                if not self.is_camera_active and self.auto_retry:
                    logger.info("Attempting to reconnect camera...")
                    # Re-scan for cameras
                    self.available_cameras = find_available_cameras(max_cameras=10)
                    if self.available_cameras:
                        self._connect_camera()
                
                elif self.is_camera_active:
                    # Check if camera is still responsive
                    with self.lock:
                        if self.cap is not None:
                            # Quick test read
                            ret, _ = self.cap.read()
                            if not ret:
                                logger.warning("Camera became unresponsive, attempting reconnection")
                                self.is_camera_active = False
                                
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Get the next frame from camera or fallback image.
        
        Returns:
            Tuple of (success, frame). Frame is None if unsuccessful.
        """
        with self.lock:
            if self.is_camera_active and self.cap is not None:
                try:
                    ret, frame = self.cap.read()
                    
                    if ret and frame is not None:
                        self.last_frame = frame.copy()
                        self.frame_count += 1
                        self.stats['total_frames'] += 1
                        self.stats['last_successful_read'] = time.time()
                        
                        # Process frame through registered processors
                        for processor in self.frame_processors:
                            try:
                                frame = processor(frame)
                            except Exception as e:
                                logger.warning(f"Frame processor error: {e}")
                        
                        # Update FPS counter
                        self._update_fps_counter()
                        
                        return True, frame
                    else:
                        self.stats['failed_reads'] += 1
                        logger.warning("Failed to read from camera")
                        
                        # If we have a last good frame, return it
                        if self.last_frame is not None:
                            return True, self.last_frame.copy()
                        
                        # Mark camera as inactive for health check to retry
                        self.is_camera_active = False
                        
                except Exception as e:
                    logger.error(f"Camera read error: {e}")
                    self.stats['failed_reads'] += 1
                    self.is_camera_active = False
            
            # Fallback to static image
            if self.fallback_image is not None:
                return True, self.fallback_image.copy()
            
            return False, None
    
    def _update_fps_counter(self):
        """Update FPS counter for performance monitoring."""
        current_time = time.time()
        self.fps_counter += 1
        
        if current_time - self.last_fps_time >= 1.0:
            logger.debug(f"Camera FPS: {self.fps_counter}")
            self.fps_counter = 0
            self.last_fps_time = current_time
    
    def add_frame_processor(self, processor: Callable[[np.ndarray], np.ndarray]):
        """
        Add a frame processor function.
        
        Args:
            processor: Function that takes a frame and returns a processed frame
        """
        self.frame_processors.append(processor)
        logger.info(f"Added frame processor: {processor.__name__}")
    
    def remove_frame_processor(self, processor: Callable):
        """Remove a frame processor function."""
        if processor in self.frame_processors:
            self.frame_processors.remove(processor)
            logger.info(f"Removed frame processor: {processor.__name__}")
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get detailed camera information."""
        info = {
            'is_active': self.is_camera_active,
            'current_index': self.current_index,
            'available_cameras': self.available_cameras,
            'has_fallback': self.fallback_image is not None,
            'frame_processors': len(self.frame_processors),
            'stats': self.stats.copy()
        }
        
        if self.is_camera_active and self.cap is not None:
            try:
                info.update({
                    'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    'fps': self.cap.get(cv2.CAP_PROP_FPS),
                    'backend': self.cap.get(cv2.CAP_PROP_BACKEND),
                })
            except Exception as e:
                logger.warning(f"Could not get camera properties: {e}")
        
        return info
    
    def switch_camera(self, camera_index: int) -> bool:
        """
        Switch to a different camera.
        
        Args:
            camera_index: Index of the camera to switch to
            
        Returns:
            True if switch was successful
        """
        if camera_index not in self.available_cameras:
            logger.warning(f"Camera index {camera_index} not available")
            return False
        
        logger.info(f"Switching to camera {camera_index}")
        self.preferred_index = camera_index
        return self._connect_camera()
    
    def refresh_cameras(self) -> List[int]:
        """
        Refresh the list of available cameras.
        
        Returns:
            Updated list of available camera indices
        """
        logger.info("Refreshing camera list...")
        self.available_cameras = find_available_cameras(max_cameras=10)
        logger.info(f"Updated available cameras: {self.available_cameras}")
        return self.available_cameras
    
    @contextmanager
    def get_frame_context(self):
        """Context manager for frame operations with automatic error handling."""
        try:
            success, frame = self.get_frame()
            yield success, frame
        except Exception as e:
            logger.error(f"Frame context error: {e}")
            yield False, None
    
    def start_recording(self, output_path: str, fps: float = 30.0, fourcc: str = 'mp4v'):
        """
        Start recording camera feed to video file.
        
        Args:
            output_path: Path to save the video file
            fps: Recording frame rate
            fourcc: Video codec
        """
        # This would be implemented for video recording functionality
        logger.info(f"Recording functionality not yet implemented: {output_path}")
    
    def take_snapshot(self, output_path: str) -> bool:
        """
        Take a snapshot and save to file.
        
        Args:
            output_path: Path to save the snapshot
            
        Returns:
            True if snapshot was successful
        """
        success, frame = self.get_frame()
        if success and frame is not None:
            try:
                cv2.imwrite(output_path, frame)
                logger.info(f"Snapshot saved: {output_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save snapshot: {e}")
        
        return False
    
    def cleanup(self):
        """Clean up camera resources."""
        logger.info("Cleaning up camera manager...")
        
        # Stop health monitoring
        self.health_check_running = False
        if self.health_check_thread is not None:
            self.health_check_thread.join(timeout=2.0)
        
        # Release camera
        with self.lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
        
        self.is_camera_active = False
        logger.info("Camera manager cleanup completed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
    
    def __del__(self):
        """Destructor with cleanup."""
        try:
            self.cleanup()
        except:
            pass


# Convenience functions for easy integration
def create_camera_manager(preferred_index: int = 0, 
                         fallback_avatar: Optional[str] = None) -> CameraManager:
    """
    Create a camera manager with default settings.
    
    Args:
        preferred_index: Preferred camera index
        fallback_avatar: Path to fallback avatar image
        
    Returns:
        Configured CameraManager instance
    """
    return CameraManager(
        preferred_index=preferred_index,
        fallback_avatar_path=fallback_avatar,
        auto_retry=True,
        health_check_interval=5.0
    )


def get_best_camera() -> Optional[CameraManager]:
    """
    Get the best available camera automatically.
    
    Returns:
        CameraManager instance or None if no cameras available
    """
    available = find_available_cameras()
    if available:
        return CameraManager(preferred_index=available[0])
    return None


if __name__ == "__main__":
    """Demo/test the camera manager."""
    print("🎥 TalkBridge Camera Manager Demo")
    print("=" * 50)
    
    # Create camera manager
    with create_camera_manager() as cam_mgr:
        print(f"📋 Camera Info: {cam_mgr.get_camera_info()}")
        
        # Test frame capture
        for i in range(10):
            success, frame = cam_mgr.get_frame()
            if success:
                print(f"✅ Frame {i+1}: {frame.shape if frame is not None else 'None'}")
            else:
                print(f"❌ Frame {i+1}: Failed")
            time.sleep(0.1)
        
        print("📊 Final stats:", cam_mgr.stats)
    
    print("✅ Demo completed!")
