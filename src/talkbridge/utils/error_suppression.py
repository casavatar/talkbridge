#!/usr/bin/env python3
"""
TalkBridge - Error Suppression
=============================

Settings to suppress warnings and non-critical logs
from MediaPipe, TensorFlow and other ML libraries

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- None
======================================================================
Functions:
- suppress_ml_warnings: Suppress ML library warnings
- configure_camera_fallback: Configure graceful camera error handling
- find_available_cameras: Find available cameras robustly
- create_robust_camera_capture: Create robust VideoCapture with error handling
- setup_qt_thread_cleanup: Configure automatic Qt thread cleanup
- create_safe_qthread: Create QThread safely with automatic cleanup
======================================================================
"""

import os
import warnings
import logging
import sys
import subprocess
from talkbridge.logging_config import get_logger

logger = get_logger(__name__)
import cv2
from typing import List, Optional, Tuple

def suppress_ml_warnings():
    """Suppresses warnings from ML libraries that are not critical during development"""
    
    # Early TensorFlow/MediaPipe configuration before any import
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Only fatal errors from TF
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneNN optimizations that cause warnings
    os.environ['MEDIAPIPE_DISABLE_GPU'] = '1'  # Disable GPU if it causes problems
    
    # Specific configuration for absl logging (Google) - EARLY INIT
    os.environ['GLOG_minloglevel'] = '3'  # Only fatal messages
    os.environ['GLOG_stderrthreshold'] = '3'  # Redirect only fatal to stderr
    os.environ['GLOG_v'] = '0'  # Verbose level 0
    os.environ['GLOG_logtostderr'] = '0'  # Don't log to stderr by default
    
    # Suppress the "Logging before flag parsing" warning
    os.environ['GLOG_alsologtostderr'] = '0'
    
    # Configuration for spaCy to suppress model loading messages
    os.environ['SPACY_WARNING_IGNORE'] = 'W008,W033,W036'  # Ignore common spaCy warnings
    os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning:spacy'
    
    # Configuration for TensorFlow Lite
    os.environ['TFLITE_LOG_LEVEL'] = 'ERROR'
    
    # Initialize absl logging early if available - VERY EARLY
    try:
        import absl.logging
        import absl.flags
        # Parse flags if not already parsed to avoid the warning
        try:
            absl.flags.FLAGS(['program_name'])
        except absl.flags.Error:
            pass  # Flags already parsed
        
        absl.logging.set_verbosity(absl.logging.ERROR)
        absl.logging.set_stderrthreshold(absl.logging.FATAL)
        absl.logging.use_absl_handler()  # Use absl handler
        logger.debug("🔧 absl logging initialized")
    except ImportError:
        pass
    
    # Configure MediaPipe logging after importing
    try:
        import mediapipe as mp
        if hasattr(mp.logging, 'absl'):
            mp.logging.absl.logging.set_verbosity(mp.logging.absl.logging.ERROR)
    except (ImportError, AttributeError):
        pass
    
    # Configure TensorFlow logging after importing
    try:
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')
        tf.autograph.set_verbosity(0)
        
        # Additional absl configuration if available
        try:
            import absl.logging
            absl.logging.set_verbosity(absl.logging.ERROR)
            absl.logging.set_stderrthreshold(absl.logging.FATAL)
        except ImportError:
            pass
            
    except ImportError:
        pass
    
    # Suppress specific common warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='.*mediapipe.*')
    warnings.filterwarnings('ignore', category=UserWarning, module='.*tensorflow.*')
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='.*tflite.*')
    warnings.filterwarnings('ignore', category=FutureWarning, module='.*tensorflow.*')
    
    # Suppress spaCy-related warnings and model loading messages
    warnings.filterwarnings('ignore', category=UserWarning, module='.*spacy.*')
    warnings.filterwarnings('ignore', message='.*Looking for cached.*')
    warnings.filterwarnings('ignore', message='.*spacy.*model.*')
    warnings.filterwarnings('ignore', message='.*xx_sent_ud_sm.*')
    
    # Suppress translation library warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='.*argostranslate.*')
    warnings.filterwarnings('ignore', category=UserWarning, module='.*transformers.*')
    
    # Suppress specific warnings from inference feedback manager
    warnings.filterwarnings('ignore', message='.*feedback.*tensors.*')
    warnings.filterwarnings('ignore', message='.*signature.*inference.*')
    
    # Configure OpenCV logging to reduce camera warnings
    cv2_logger = logging.getLogger('cv2')
    cv2_logger.setLevel(logging.ERROR)
    
    logger.debug("🔇 ML warnings suppression configured")
    warnings.filterwarnings('ignore', category=UserWarning, module='.*tensorflow.*')
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='.*tflite.*')
    
    # Configure OpenCV logging to reduce camera warnings
    cv2_logger = logging.getLogger('cv2')
    cv2_logger.setLevel(logging.ERROR)
    
    logger.debug("🔇 ML warnings suppression configured")

def configure_camera_fallback():
    """Configure graceful handling for camera errors"""
    
    # Environment variables to reduce OpenCV warnings
    os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
    os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
    
    # Configure specific variables for UVC (USB Video Class)
    os.environ['OPENCV_VIDEOIO_PRIORITY_V4L2'] = '0'  # Reduce V4L2 priority
    os.environ['OPENCV_VIDEOIO_PRIORITY_GSTREAMER'] = '0'  # Reduce GStreamer priority
    
    logger.debug("📹 Camera fallback configured")

def find_available_cameras(max_cameras=5):
    """
    Find available cameras robustly
    
    Returns:
        list: List of available camera indices
    """
    import cv2
    available_cameras = []
    
    # Temporarily configure logging to suppress warnings
    old_level = os.environ.get('OPENCV_LOG_LEVEL', 'INFO')
    os.environ['OPENCV_LOG_LEVEL'] = 'FATAL'  # Only fatal errors
    
    try:
        for i in range(max_cameras):
            cap = None
            try:
                # Create VideoCapture with timeout
                cap = cv2.VideoCapture(i, cv2.CAP_V4L2)  # Specify V4L2 backend
                
                # Configure timeout to avoid blocking
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Test if it actually works
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        available_cameras.append(i)
                        logger.debug(f"📹 Camera found at index {i}")
                
            except Exception as e:
                # Silent logging of individual camera errors
                pass
            finally:
                if cap is not None:
                    cap.release()
                    
    finally:
        # Restore original logging level
        os.environ['OPENCV_LOG_LEVEL'] = old_level
    
    if not available_cameras:
        logger.info("🔹 No available cameras found")
    
    return available_cameras

def create_robust_camera_capture(preferred_index=0):
    """
    Create a robust VideoCapture with error handling
    
    Args:
        preferred_index: Preferred camera index
        
    Returns:
        tuple: (VideoCapture object or None, actual_index used)
    """
    import cv2
    
    # Search for available cameras
    available_cameras = find_available_cameras()
    
    if not available_cameras:
        return None, -1
    
    # Use preferred index if available
    if preferred_index in available_cameras:
        target_index = preferred_index
    else:
        target_index = available_cameras[0]
        logger.warning(f"📹 Preferred index {preferred_index} not available, using {target_index}")
    
    try:
        cap = cv2.VideoCapture(target_index, cv2.CAP_V4L2)
        
        if cap.isOpened():
            # Configure basic properties
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            return cap, target_index
        
    except Exception as e:
        logger.error(f"❌ Error creating VideoCapture: {e}")
    
    return None, -1

def setup_error_handling():
    """Configure global error handling for the application"""
    
    # Suppress pygame warnings
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    
    # Configure basic logging
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # )
    
    logger.debug("⚙️ Error handling configured")

def setup_qt_thread_cleanup():
    """Configure automatic Qt thread cleanup when closing the application"""
    import atexit
    import signal
    import sys
    
    active_threads = []
    
    def cleanup_threads():
        """Clean up all active threads before closing"""
        print("🧹 Cleaning up active threads...")
        
        for thread in active_threads:
            if thread and thread.isRunning():
                print(f"🔄 Closing thread: {thread}")
                thread.quit()
                if not thread.wait(3000):  # Wait 3 seconds
                    print(f"⚠️ Thread didn't respond, terminating: {thread}")
                    thread.terminate()
                    thread.wait(1000)  # Wait 1 more second
        
        active_threads.clear()
        print("✅ Threads cleaned up")
    
    def signal_handler(signum, frame):
        """Handle system signals for cleanup"""
        print(f"🚨 Signal received: {signum}, starting cleanup...")
        cleanup_threads()
        sys.exit(0)
    
    # Register automatic cleanup
    atexit.register(cleanup_threads)
    
    # Register signal handling
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination
    
    print("🔧 Qt thread cleanup configured")
    
    return active_threads

def create_safe_qthread(worker_class, *args, **kwargs):
    """
    Create a QThread safely with automatic cleanup
    
    Args:
        worker_class: Worker class to run in the thread
        *args, **kwargs: Arguments for the worker
        
    Returns:
        tuple: (thread, worker, cleanup_func)
    """
    try:
        from PySide6.QtCore import QThread
    except ImportError:
        try:
            from PyQt6.QtCore import QThread
        except ImportError:
            raise ImportError("Neither PySide6 nor PyQt6 are available")
    
    # Create thread and worker
    thread = QThread()
    worker = worker_class(*args, **kwargs)
    worker.moveToThread(thread)
    
    # Configure basic connections
    thread.started.connect(worker.run if hasattr(worker, 'run') else lambda: None)
    thread.finished.connect(thread.deleteLater)
    worker.finished.connect(thread.quit) if hasattr(worker, 'finished') else None
    
    def cleanup():
        """Specific cleanup function for this thread"""
        if thread.isRunning():
            thread.quit()
            if not thread.wait(2000):
                thread.terminate()
                thread.wait(1000)
    
    return thread, worker, cleanup

if __name__ == "__main__":
    print("🔧 Configuring warning suppression...")
    suppress_ml_warnings()
    configure_camera_fallback()
    setup_error_handling()
    print("✅ Configuration completed")
