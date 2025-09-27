#!/usr/bin/env python3
"""
TalkBridge Desktop - Avatar Tab (CustomTkinter)
===============================================

Avatar display and animation tab with CustomTkinter and thread-safe UI operations.

Author: TalkBridge Team
Date: 2025-09-26
Version: 2.1 - Enhanced with thread-safe UI operations

Thread Safety Features:
- All UI updates from background threads use ui_thread_call()
- Camera initialization runs in daemon thread with safe UI callbacks
- Error handling preserves UI thread safety
- Proper UI root registration for reliable thread-safe operations

Requirements:
- customtkinter
- tkinter
- opencv-python (optional)
- mediapipe (optional)

Threading Best Practices Implemented:
1. UI operations are always performed on the main thread via ui_thread_call()
2. Background threads only handle computation, not UI updates  
3. Camera operations use dedicated helper methods for UI updates
4. Error handling maintains thread safety throughout the application
"""

# Import core modules
import asyncio
import threading
import time
import logging
from typing import Optional, Tuple, Any
from pathlib import Path

# Import GUI framework
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

# Import centralized logging and exception handling
from src.logging_config import get_logger, log_exception
from src.utils.exceptions import UIError, create_ui_error

# Import new error recovery system (available for future migration)
# from src.utils.error_recovery import safe_ui_operation, RecoveryLevel

# Import desktop components
from src.desktop.ui.events import EventBus, emit_event, register_handler
from src.desktop.ui.theme import ThemeManager
from src.desktop.ui.controls import create_button, create_frame
from src.desktop.ui.utilities import ui_thread_call, schedule_ui_update, register_ui_root

# Optional imports with fallbacks
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None

# Get logger for this module
logger = get_logger(__name__)

# Check for modern systems capabilities
try:
    import numpy as np
    MODERN_SYSTEMS_AVAILABLE = True
except ImportError:
    MODERN_SYSTEMS_AVAILABLE = False
    logger.warning("NumPy not available. Some animation features will be disabled.")

# Handle missing dependencies gracefully
if not OPENCV_AVAILABLE:
    logger.warning("OpenCV not available. Camera features will be disabled.")

if not MEDIAPIPE_AVAILABLE:
    logger.warning("MediaPipe not available. Face detection will be disabled.")

# Constants and global variables
DEFAULT_AVATAR_SIZE = (400, 300)
CAMERA_FPS = 30
DEFAULT_BACKGROUND_COLOR = "#2B2B2B"

# Face detection models
mp_face_detection = None
mp_drawing = None
try:
    if MEDIAPIPE_AVAILABLE and mp is not None:
        mp_face_detection = getattr(mp, 'solutions', None)
        if mp_face_detection:
            mp_face_detection = getattr(mp_face_detection, 'face_detection', None)
            mp_drawing = getattr(getattr(mp, 'solutions', None), 'drawing_utils', None)
except Exception as e:
    logger.error(f"Error initializing MediaPipe components: {e}")

# Global utility functions and error handling
ERROR_HANDLING_AVAILABLE = False

# Simple error categories
class ErrorCategory:
    CAMERA = "camera"
    MEDIAPIPE = "mediapipe"
    UI = "ui"
    ASYNC = "async"

def handle_user_facing_error(error, category=None, context=None):
    """Simple fallback error handler."""
    logger = get_logger(__name__)
    logger.error(f"Error: {error}")

ASYNC_UTILS_AVAILABLE = False

def run_async(task_func, *args, on_success=None, on_error=None, on_progress=None, task_name=None):
    """Simple fallback for async operations."""
    try:
        result = task_func(*args)
        if on_success:
            on_success(result)
        return "task_completed"
    except Exception as e:
        if on_error:
            on_error(e)
        raise

# ui_thread_call is imported from src.desktop.ui.utilities - no local fallback needed

LOGGING_UTILS_AVAILABLE = False

def add_error_context(logger, context=""):
    """Simple fallback for adding error context."""
    logger.info(f"Context: {context}")

# Handle missing MediaPipe gracefully
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("Warning: MediaPipe not available. Face detection will be disabled.")

# Use fallback systems only to avoid import conflicts
MODERN_SYSTEMS_AVAILABLE = False
LOGGING_UTILS_AVAILABLE = False

# Fallback notification functions
def notify_error(message):
    logger = get_logger(__name__)
    logger.error(message)

def notify_warn(message):
    logger = get_logger(__name__)
    logger.warning(message)

def notify_info(message):
    logger = get_logger(__name__)
    logger.info(message)

# Import UI utilities and theme
THEME_AVAILABLE = False
clean_text = None
ComponentThemes = None
Typography = None
ColorPalette = None
try:
    from src.desktop.ui.ui_utils import clean_text
    from src.desktop.ui.theme import ComponentThemes, Typography, ColorPalette
    THEME_AVAILABLE = True
except ImportError:
    pass

# Try to import video processing modules
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("Warning: OpenCV not available. Avatar features will be limited.")

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("Warning: MediaPipe not available. Face detection will be disabled.")

class AvatarTab:
    """
    Avatar interface tab with CustomTkinter.
    
    Features:
    - Avatar display area
    - Webcam integration (if available)
    - Animation controls
    - Face sync settings
    - Interactive animations
    - Quality settings
    """

    def __init__(self, parent, state_manager=None, core_bridge=None):
        """Initialize the avatar tab."""
        self.parent = parent
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        
        # Register UI root for thread-safe operations
        try:
            # Try to get the toplevel window for UI thread operations
            ui_root = parent.winfo_toplevel() if hasattr(parent, 'winfo_toplevel') else parent
            register_ui_root(ui_root)
        except Exception as e:
            self.logger.debug(f"Could not register UI root: {e}")
        
        # Logger with enhanced error handling
        self.logger = logging.getLogger("talkbridge.desktop.avatar")
        
        # Add error context for better debugging
        if LOGGING_UTILS_AVAILABLE and add_error_context:
            add_error_context(self.logger, "AvatarTab")
        
        # Video capture
        if CV2_AVAILABLE and cv2:
            self.cap: Optional[Any] = None  # cv2.VideoCapture type when available
        else:
            self.cap = None
        self.face_mesh = None
        
        # UI elements
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.avatar_canvas: Optional[tk.Canvas] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.start_camera_button: Optional[ctk.CTkButton] = None
        self.animation_button: Optional[ctk.CTkButton] = None
        
        # Control elements
        self.sensitivity_slider: Optional[ctk.CTkSlider] = None
        self.quality_combo: Optional[ctk.CTkComboBox] = None
        self.show_landmarks_var: Optional[tk.BooleanVar] = None
        self.show_mesh_var: Optional[tk.BooleanVar] = None
        
        # State
        self.camera_active = False
        self.animation_enabled = False
        self.face_detected = False
        
        # Settings
        self.sensitivity = 0.5
        self.quality = "Medium"
        self.show_landmarks = False
        self.show_mesh = False
        
        # Setup UI
        self.setup_ui()
        self.initialize_components()

    def setup_ui(self) -> None:
        """Set up the avatar interface with comprehensive controls."""
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_text = "Avatar & Animation"
        if THEME_AVAILABLE and clean_text:
            title_text = clean_text("Avatar & Animation")
        
        title_label = ctk.CTkLabel(
            self.main_frame,
            text=title_text,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Main content frame
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left panel - Video display
        video_frame = ctk.CTkFrame(content_frame)
        video_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        video_text = "Video Display"
        if THEME_AVAILABLE and clean_text:
            video_text = clean_text("Video Display")
        
        video_label = ctk.CTkLabel(
            video_frame,
            text=video_text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        video_label.pack(pady=(10, 5))
        
        # Video canvas
        self.avatar_canvas = tk.Canvas(
            video_frame,
            width=400,
            height=300,
            bg="#2b2b2b",
            highlightthickness=0
        )
        self.avatar_canvas.pack(padx=10, pady=10)
        
        # Video controls
        video_controls = ctk.CTkFrame(video_frame)
        video_controls.pack(fill="x", padx=10, pady=(0, 10))
        
        start_camera_text = "Start Camera"
        if THEME_AVAILABLE and clean_text:
            start_camera_text = clean_text("Start Camera")
        
        self.start_camera_button = ctk.CTkButton(
            video_controls,
            text=start_camera_text,
            command=self.toggle_camera,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.start_camera_button.pack(side="left", padx=5, pady=5)
        
        animation_text = "Start Animation"
        if THEME_AVAILABLE and clean_text:
            animation_text = clean_text("Start Animation")
        
        self.animation_button = ctk.CTkButton(
            video_controls,
            text=animation_text,
            command=self.toggle_animation,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        self.animation_button.pack(side="left", padx=5, pady=5)
        
        # Right panel - Controls
        controls_frame = ctk.CTkFrame(content_frame)
        controls_frame.pack(side="right", fill="y", padx=(5, 10), pady=10)
        
        controls_text = "Controls"
        if THEME_AVAILABLE and clean_text:
            controls_text = clean_text("Controls")
        
        controls_label = ctk.CTkLabel(
            controls_frame,
            text=controls_text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        controls_label.pack(pady=(10, 5))
        
        # Quality settings
        quality_frame = ctk.CTkFrame(controls_frame)
        quality_frame.pack(fill="x", padx=10, pady=5)
        
        quality_text = "Quality:"
        if THEME_AVAILABLE and clean_text:
            quality_text = clean_text("Quality:")
        ctk.CTkLabel(quality_frame, text=quality_text).pack(pady=(10, 5))
        self.quality_combo = ctk.CTkComboBox(
            quality_frame,
            values=["Low", "Medium", "High", "Ultra"],
            command=self.on_quality_changed
        )
        self.quality_combo.set("Medium")
        self.quality_combo.pack(pady=(0, 10))
        
        # Sensitivity settings
        sensitivity_frame = ctk.CTkFrame(controls_frame)
        sensitivity_frame.pack(fill="x", padx=10, pady=5)
        
        sensitivity_text = "Sensitivity:"
        if THEME_AVAILABLE and clean_text:
            sensitivity_text = clean_text("Sensitivity:")
        ctk.CTkLabel(sensitivity_frame, text=sensitivity_text).pack(pady=(10, 5))
        self.sensitivity_slider = ctk.CTkSlider(
            sensitivity_frame,
            from_=0,
            to=1,
            command=self.on_sensitivity_changed
        )
        self.sensitivity_slider.set(0.5)
        self.sensitivity_slider.pack(pady=(0, 10))
        
        # Display options
        display_frame = ctk.CTkFrame(controls_frame)
        display_frame.pack(fill="x", padx=10, pady=5)
        
        display_text = "Display Options:"
        if THEME_AVAILABLE and clean_text:
            display_text = clean_text("Display Options:")
        ctk.CTkLabel(display_frame, text=display_text).pack(pady=(10, 5))
        
        self.show_landmarks_var = tk.BooleanVar()
        landmarks_text = "Show Landmarks"
        if THEME_AVAILABLE and clean_text:
            landmarks_text = clean_text("Show Landmarks")
        
        landmarks_check = ctk.CTkCheckBox(
            display_frame,
            text=landmarks_text,
            variable=self.show_landmarks_var,
            command=self.on_landmarks_changed
        )
        landmarks_check.pack(pady=2)
        
        self.show_mesh_var = tk.BooleanVar()
        mesh_text = "Show Face Mesh"
        if THEME_AVAILABLE and clean_text:
            mesh_text = clean_text("Show Face Mesh")
        
        mesh_check = ctk.CTkCheckBox(
            display_frame,
            text=mesh_text,
            variable=self.show_mesh_var,
            command=self.on_mesh_changed
        )
        mesh_check.pack(pady=2)
        
        # Status area
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Camera: Inactive | Animation: Disabled",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.status_label.pack(pady=10)
        
        self.logger.info("Avatar tab UI setup completed")

    def initialize_components(self) -> None:
        """Initialize avatar components."""
        if MEDIAPIPE_AVAILABLE and mp:
            try:
                # Try to access MediaPipe FaceMesh - handle different versions
                if hasattr(mp, 'solutions') and mp.solutions and hasattr(mp.solutions, 'face_mesh'):
                    face_mesh_module = getattr(mp.solutions, 'face_mesh', None)
                    if face_mesh_module and hasattr(face_mesh_module, 'FaceMesh'):
                        self.face_mesh = face_mesh_module.FaceMesh(
                            max_num_faces=1,
                            refine_landmarks=True,
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5
                        )
                    else:
                        self.logger.warning("FaceMesh class not found in MediaPipe")
                        self.face_mesh = None
                else:
                    self.logger.warning("MediaPipe solutions.face_mesh not available")
                    self.face_mesh = None
            except Exception as e:
                self.logger.error(f"Failed to initialize MediaPipe face mesh: {e}")
                self.face_mesh = None
            self.logger.info("MediaPipe face mesh initialized")
        else:
            self.logger.warning("MediaPipe not available - face detection disabled")

    def toggle_camera(self) -> None:
        """Toggle camera on/off."""
        if self.camera_active:
            self.stop_camera()
        else:
            threading.Thread(target=self.start_camera_safe, daemon=True).start()

    def start_camera_safe(self):
        """Safely start camera in background thread with error handling."""
        try:
            self.start_camera()
        except Exception as e:
            self.logger.warning(f"Camera init failed: {e}")
            self.show_camera_unavailable_message()

    def show_camera_unavailable_message(self):
        """Display camera unavailable message to user."""
        # Use ui_thread_call to ensure UI updates happen on main thread
        ui_thread_call(self._update_camera_unavailable_ui)

    def _update_camera_unavailable_ui(self):
        """Update UI components to show camera unavailable (runs on main thread)."""
        try:
            self.update_status("Camera not available")
            if hasattr(self, 'start_camera_button') and self.start_camera_button:
                self.start_camera_button.configure(text="Camera Unavailable", state="disabled")
        except Exception as e:
            self.logger.debug(f"Could not update camera UI: {e}")

    def _update_camera_failed_ui(self, error_message: str):
        """Update UI components when camera initialization fails (runs on main thread)."""
        try:
            self.update_status("No camera found")
            self._show_camera_fallback(error_message)
        except Exception as e:
            self.logger.debug(f"Could not update camera failed UI: {e}")

    def _update_camera_started_ui(self):
        """Update UI components when camera starts successfully (runs on main thread)."""
        try:
            if hasattr(self, 'start_camera_button') and self.start_camera_button:
                self.start_camera_button.configure(text="📹 Stop Camera", fg_color="red")
            self.update_status("Camera: Active")
            
            # Start video loop on main thread
            self.update_video_frame()
        except Exception as e:
            self.logger.debug(f"Could not update camera started UI: {e}")

    def _update_camera_error_ui(self, error_message: str):
        """Update UI components when camera encounters an error (runs on main thread)."""
        try:
            self.update_status(error_message)
            self._show_camera_fallback(error_message)
        except Exception as e:
            self.logger.debug(f"Could not update camera error UI: {e}")

    def start_camera(self) -> None:
        """Start camera capture with robust error handling and fallback options."""
        # Check OpenCV availability
        if not CV2_AVAILABLE:
            self.update_status("Camera not available (OpenCV not installed)")
            self.logger.warning("OpenCV not available - camera functionality disabled")
            return
            
        try:
            self.logger.info("Attempting to start camera...")
            
            # Try multiple camera indices (0, 1, 2) to find working camera
            camera_indices = [0, 1, 2]
            camera_opened = False
            
            for idx in camera_indices:
                try:
                    self.logger.info(f"Trying camera index {idx}")
                    if cv2 is None:
                        self.logger.error("OpenCV not available")
                        break
                    
                    self.cap = cv2.VideoCapture(idx)
                    
                    # Set camera properties for better compatibility
                    if hasattr(cv2, 'CAP_PROP_FRAME_WIDTH'):
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    if hasattr(cv2, 'CAP_PROP_FRAME_HEIGHT'):
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    if hasattr(cv2, 'CAP_PROP_FPS'):
                        self.cap.set(cv2.CAP_PROP_FPS, 30)
                    
                    # Test if camera is actually working
                    if self.cap.isOpened():
                        ret, test_frame = self.cap.read()
                        if ret and test_frame is not None:
                            self.logger.info(f"Camera {idx} opened successfully")
                            camera_opened = True
                            break
                        else:
                            self.logger.warning(f"Camera {idx} opened but no frame received")
                            self.cap.release()
                    else:
                        self.logger.warning(f"Camera {idx} could not be opened")
                        
                except Exception as camera_error:
                    self.logger.warning(f"Camera {idx} failed: {camera_error}")
                    if self.cap:
                        self.cap.release()
                        self.cap = None
            
            if not camera_opened:
                # All camera attempts failed - handle gracefully instead of raising
                error_msg = "Could not open any camera (indices 0-2 tested)"
                self.logger.warning(f"[AvatarTab] No camera available: {error_msg}")
                
                # Set camera as inactive and show fallback (thread-safe)
                self.camera_active = False
                ui_thread_call(self._update_camera_failed_ui, "No camera found. Please connect a camera device.")
                return  # Exit gracefully instead of raising
                
            # Camera successfully opened - update UI on main thread
            self.camera_active = True
            ui_thread_call(self._update_camera_started_ui)
            
            self.logger.info("Camera started successfully")
            
        except Exception as e:
            # Handle all camera errors gracefully
            if LOGGING_UTILS_AVAILABLE:
                log_exception(self.logger, e, "Camera startup")
            else:
                self.logger.exception("Failed to start camera:")
            
            # Clean up any partial initialization
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()
                self.cap = None
            
            self.camera_active = False
            
            # Provide user-friendly error messages
            if "permission" in str(e).lower():
                error_message = "Camera access denied. Please check permissions."
            elif "busy" in str(e).lower() or "in use" in str(e).lower():
                error_message = "Camera is being used by another application."
            elif "not found" in str(e).lower() or "could not open" in str(e).lower():
                error_message = "No camera found. Please connect a camera device."
            else:
                error_message = f"Camera error: {str(e)[:50]}..."
            
            # Update UI on main thread
            ui_thread_call(self._update_camera_error_ui, error_message)

    def stop_camera(self) -> None:
        """Stop camera capture."""
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.camera_active = False
        if hasattr(self, 'start_camera_button') and self.start_camera_button:
            self.start_camera_button.configure(text="📹 Start Camera", fg_color="#4CAF50")
        
        # Clear canvas
        if hasattr(self, 'avatar_canvas') and self.avatar_canvas:
            self.avatar_canvas.delete("all")
            self.avatar_canvas.create_text(
                200, 150,
                text="Camera Inactive",
                fill="white",
                font=("Arial", 16)
            )
        
        self.update_status("Camera: Inactive")
        self.logger.info("Camera stopped")

    def _show_camera_fallback(self, error_message: str) -> None:
        """Display fallback content when camera is not available."""
        try:
            # Clear canvas
            if hasattr(self, 'avatar_canvas') and self.avatar_canvas:
                self.avatar_canvas.delete("all")
                
                # Show error icon and message
                self.avatar_canvas.create_text(
                    200, 120,
                    text="📷",
                    fill="#ff6b6b",
                    font=("Arial", 24)
                )
            
                self.avatar_canvas.create_text(
                    200, 160,
                    text="Camera Not Available",
                    fill="white",
                    font=("Arial", 12, "bold")
                )
            
            # Show error details (truncated)
                error_text = error_message[:40] + "..." if len(error_message) > 40 else error_message
                self.avatar_canvas.create_text(
                    200, 180,
                    text=error_text,
                    fill="#cccccc",
                    font=("Arial", 9)
                )
                
                # Show suggestions
                self.avatar_canvas.create_text(
                    200, 210,
                    text="• Check camera connections",
                    fill="#aaaaaa",
                    font=("Arial", 8)
                )
                
                self.avatar_canvas.create_text(
                    200, 225,
                    text="• Close other camera apps",
                    fill="#aaaaaa",
                    font=("Arial", 8)
                )
                
                self.avatar_canvas.create_text(
                    200, 240,
                    text="• Grant camera permissions",
                    fill="#aaaaaa",
                    font=("Arial", 8)
                )
            
        except Exception as fallback_error:
            self.logger.error(f"Failed to show camera fallback: {fallback_error}")
            # Basic fallback if even the fallback fails
            if hasattr(self, 'avatar_canvas') and self.avatar_canvas:
                self.avatar_canvas.delete("all")
                self.avatar_canvas.create_text(
                    200, 150,
                    text="Camera Error",
                    fill="red",
                    font=("Arial", 14)
                )
        
        self.update_status("Camera: Inactive")
        self.logger.info("Camera stopped")

    def update_video_frame(self) -> None:
        """Update video frame in canvas with robust error handling."""
        if not self.camera_active or not self.cap:
            return
            
        try:
            # Check if camera is still available
            if not self.cap.isOpened():
                self.logger.warning("Camera disconnected during operation")
                self.stop_camera()
                self._show_camera_fallback("Camera disconnected")
                return
            
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.logger.warning("Failed to read frame from camera")
                # Try a few more times before giving up (non-blocking)
                # Simple retry without async
                for retry in range(3):
                    ret_retry, frame_retry = self.cap.read()
                    if ret_retry and frame_retry is not None:
                        frame = frame_retry
                        break
                else:
                    self.logger.error("Failed to read frame after retries - stopping camera")
                    self.stop_camera()
                    return
                
            # Flip frame horizontally for mirror effect
            if cv2 is not None:
                frame = cv2.flip(frame, 1)
            
            # Process face detection if enabled
            if self.face_mesh and MEDIAPIPE_AVAILABLE:
                try:
                    frame = self.process_face_detection(frame)
                except Exception as face_error:
                    self.logger.warning(f"Face detection error: {face_error}")
                    # Continue without face detection
            
            # Resize frame to fit canvas
            try:
                if cv2 is not None:
                    frame = cv2.resize(frame, (400, 300))
            except Exception as resize_error:
                self.logger.error(f"Frame resize error: {resize_error}")
                return
            
            # Convert to RGB and then to PhotoImage
            try:
                if cv2 is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    frame_rgb = frame
            except Exception as color_error:
                self.logger.error(f"Color conversion error: {color_error}")
                return
            
            # Convert to PIL Image and then to PhotoImage
            try:
                from PIL import Image, ImageTk
                pil_image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update canvas
                if hasattr(self, 'avatar_canvas') and self.avatar_canvas:
                    self.avatar_canvas.delete("all")
                    self.avatar_canvas.create_image(200, 150, image=photo)
                    # Store image reference to prevent garbage collection
                    if not hasattr(self, '_image_refs'):
                        self._image_refs = []
                    self._image_refs.append(photo)
                
            except ImportError:
                # Fallback without PIL - use basic text
                if hasattr(self, 'avatar_canvas') and self.avatar_canvas:
                    self.avatar_canvas.delete("all")
                    self.avatar_canvas.create_text(
                        200, 150,
                        text="Camera Active\n(PIL not available for display)",
                        fill="white",
                        font=("Arial", 12),
                        justify="center"
                    )
            except Exception as display_error:
                self.logger.error(f"Display error: {display_error}")
                return
                
            # Schedule next frame if still active
            if self.camera_active and self.cap and self.cap.isOpened():
                if hasattr(self, 'avatar_canvas') and self.avatar_canvas:
                    self.avatar_canvas.after(30, self.update_video_frame)
            else:
                self.logger.warning("Camera no longer active - stopping frame updates")
                
        except Exception as e:
            if LOGGING_UTILS_AVAILABLE:
                log_exception(self.logger, e, "Video frame update")
            else:
                self.logger.exception("Error updating video frame:")
            # On any major error, stop the camera gracefully
            self.stop_camera()
            self._show_camera_fallback(f"Video processing error: {str(e)[:30]}...")

    def process_face_detection(self, frame):
        """Process face detection and landmarks."""
        if not self.face_mesh:
            return frame
            
        try:
            # Convert BGR to RGB
            if cv2 is not None and hasattr(cv2, 'cvtColor') and hasattr(cv2, 'COLOR_BGR2RGB'):
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                rgb_frame = frame
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                self.face_detected = True
                
                for face_landmarks in results.multi_face_landmarks:
                    # Draw landmarks if enabled
                    if self.show_landmarks:
                        for landmark in face_landmarks.landmark:
                            x = int(landmark.x * frame.shape[1])
                            y = int(landmark.y * frame.shape[0])
                            if cv2 and hasattr(cv2, 'circle'):
                                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                    
                    # Draw face mesh if enabled
                    if self.show_mesh and mp and hasattr(mp, 'solutions'):
                        drawing_utils = getattr(mp.solutions, 'drawing_utils', None)
                        face_mesh_module = getattr(mp.solutions, 'face_mesh', None)
                        if drawing_utils and face_mesh_module and hasattr(drawing_utils, 'draw_landmarks'):
                            contours = getattr(face_mesh_module, 'FACEMESH_CONTOURS', None)
                            drawing_spec = getattr(drawing_utils, 'DrawingSpec', None)
                            if contours and drawing_spec:
                                drawing_utils.draw_landmarks(
                                    frame,
                                    face_landmarks,
                                    contours,
                                    landmark_drawing_spec=None,
                                    connection_drawing_spec=drawing_spec(
                                        color=(0, 255, 0), thickness=1, circle_radius=1
                                    )
                                )
            else:
                self.face_detected = False
                
        except Exception as e:
            self.logger.exception("Face detection error:")
            
        return frame



    def on_quality_changed(self, value: str) -> None:
        """Handle quality setting change."""
        self.quality = value
        self.logger.info(f"Quality changed to: {value}")

    def on_sensitivity_changed(self, value: float) -> None:
        """Handle sensitivity change."""
        self.sensitivity = value
        self.logger.info(f"Sensitivity changed to: {value:.2f}")

    def on_landmarks_changed(self) -> None:
        """Handle landmarks display toggle."""
        if self.show_landmarks_var is not None:
            self.show_landmarks = self.show_landmarks_var.get()
        self.logger.info(f"Show landmarks: {self.show_landmarks}")

    def on_mesh_changed(self) -> None:
        """Handle mesh display toggle."""
        if self.show_mesh_var is not None:
            self.show_mesh = self.show_mesh_var.get()
        self.logger.info(f"Show mesh: {self.show_mesh}")

    def update_status(self, message: str) -> None:
        """Update status label."""
        if self.status_label:
            camera_status = "Active" if self.camera_active else "Inactive"
            animation_status = "Enabled" if self.animation_enabled else "Disabled"
            face_status = "Detected" if self.face_detected else "Not Detected"
            
            status_text = f"Camera: {camera_status} | Animation: {animation_status} | Face: {face_status}"
            self.status_label.configure(text=status_text)

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.camera_active:
            self.stop_camera()
        
        self.logger.info("Avatar tab cleanup completed")
        """Sets up the avatar interface."""
        self.logger.info("Setting up avatar tab UI")
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="Avatar Display",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Avatar display area
        avatar_frame = ctk.CTkFrame(self.main_frame)
        avatar_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Canvas for avatar display
        self.avatar_canvas = tk.Canvas(
            avatar_frame,
            width=400,
            height=300,
            bg="black",
            highlightthickness=0
        )
        self.avatar_canvas.pack(expand=True, pady=20)
        
        # Add placeholder content
        self.avatar_canvas.create_text(
            200, 150,
            text="Avatar Display Area\n(3D Avatar Coming Soon)",
            fill="white",
            font=("Arial", 14),
            justify=tk.CENTER
        )
        
        # Controls frame
        controls_frame = ctk.CTkFrame(self.main_frame)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        # Avatar controls
        avatar_label = ctk.CTkLabel(
            controls_frame,
            text="Avatar Controls",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        avatar_label.pack(pady=10)
        
        # Button frame
        button_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        # Enable/Disable avatar
        self.toggle_button = ctk.CTkButton(
            button_frame,
            text="Enable Avatar",
            width=120,
            command=self.toggle_avatar
        )
        self.toggle_button.pack(side="left", padx=5)
        
        # Start/Stop animation
        self.animation_button = ctk.CTkButton(
            button_frame,
            text="Start Animation",
            width=120,
            command=self.toggle_animation,
            state="disabled"
        )
        self.animation_button.pack(side="left", padx=5)
        
        # Reset avatar
        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset",
            width=100,
            fg_color="orange",
            hover_color="darkorange",
            command=self.reset_avatar
        )
        reset_button.pack(side="left", padx=5)
        
        # Settings frame
        settings_frame = ctk.CTkFrame(controls_frame)
        settings_frame.pack(fill="x", pady=10)
        
        settings_label = ctk.CTkLabel(
            settings_frame,
            text="Animation Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_label.pack(pady=5)
        
        # Face sync option
        self.face_sync_var = tk.BooleanVar()
        face_sync_checkbox = ctk.CTkCheckBox(
            settings_frame,
            text="Enable Face Sync",
            variable=self.face_sync_var,
            command=self.on_face_sync_changed
        )
        face_sync_checkbox.pack(pady=5)
        
        # Animation speed
        speed_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        speed_frame.pack(fill="x", pady=5)
        
        speed_label = ctk.CTkLabel(
            speed_frame,
            text="Animation Speed:",
            font=ctk.CTkFont(size=12)
        )
        speed_label.pack(side="left", padx=10)
        
        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0,
            to=2,
            number_of_steps=19,
            command=self.on_speed_changed
        )
        self.speed_slider.pack(side="right", padx=10, fill="x", expand=True)
        self.speed_slider.set(1.0)
        
        self.speed_value_label = ctk.CTkLabel(
            speed_frame,
            text="1.0x",
            font=ctk.CTkFont(size=11)
        )
        self.speed_value_label.pack(side="right", padx=5)
        
        # Status frame
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Avatar system ready",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=5)

    def toggle_avatar(self) -> None:
        """Toggles avatar enable/disable."""
        self.avatar_enabled = not self.avatar_enabled
        
        if self.avatar_enabled:
            if hasattr(self, 'toggle_button') and self.toggle_button:
                self.toggle_button.configure(text="Disable Avatar")
            if hasattr(self, 'animation_button') and self.animation_button:
                self.animation_button.configure(state="normal")
            self.update_status("Avatar enabled")
            self.logger.info("Avatar enabled")
        else:
            if hasattr(self, 'toggle_button') and self.toggle_button:
                self.toggle_button.configure(text="Enable Avatar")
            if hasattr(self, 'animation_button') and self.animation_button:
                self.animation_button.configure(state="disabled")
            self.stop_animation()
            self.update_status("Avatar disabled")
            self.logger.info("Avatar disabled")

    def toggle_animation(self) -> None:
        """Toggles animation start/stop."""
        if self.animation_running:
            self.stop_animation()
        else:
            self.start_animation()

    def start_animation(self) -> None:
        """Starts avatar animation."""
        if not self.avatar_enabled:
            return
        
        self.animation_running = True
        if hasattr(self, 'animation_button') and self.animation_button:
            self.animation_button.configure(text="Stop Animation")
        self.update_status("Animation running")
        self.logger.info("Avatar animation started")
        
        # Add visual feedback to canvas
        if hasattr(self, 'avatar_canvas') and self.avatar_canvas:
            self.avatar_canvas.delete("animation")
            self.avatar_canvas.create_oval(
                150, 100, 250, 200,
                outline="green",
                width=3,
                tags="animation"
            )

    def stop_animation(self) -> None:
        """Stops avatar animation."""
        self.animation_running = False
        if hasattr(self, 'animation_button') and self.animation_button:
            self.animation_button.configure(text="Start Animation")
        self.update_status("Animation stopped")
        self.logger.info("Avatar animation stopped")
        
        # Remove animation visual feedback
        if hasattr(self, 'avatar_canvas') and self.avatar_canvas:
            self.avatar_canvas.delete("animation")

    def reset_avatar(self) -> None:
        """Resets avatar to default state."""
        self.stop_animation()
        self.avatar_enabled = False
        if hasattr(self, 'toggle_button') and self.toggle_button:
            self.toggle_button.configure(text="Enable Avatar")
        if hasattr(self, 'animation_button') and self.animation_button:
            self.animation_button.configure(state="disabled")
        if hasattr(self, 'face_sync_var') and self.face_sync_var:
            self.face_sync_var.set(False)
        if hasattr(self, 'speed_slider') and self.speed_slider:
            self.speed_slider.set(1.0)
        if hasattr(self, 'speed_value_label') and self.speed_value_label:
            self.speed_value_label.configure(text="1.0x")
        
        # Clear canvas
        if hasattr(self, 'avatar_canvas') and self.avatar_canvas:
            self.avatar_canvas.delete("all")
            self.avatar_canvas.create_text(
                200, 150,
                text="Avatar Display Area\n(3D Avatar Coming Soon)",
                fill="white",
                font=("Arial", 14),
                justify=tk.CENTER
            )
        
        self.update_status("Avatar reset to defaults")
        self.logger.info("Avatar reset")

    def on_face_sync_changed(self) -> None:
        """Handles face sync setting change."""
        enabled = self.face_sync_var.get()
        status = "enabled" if enabled else "disabled"
        self.update_status(f"Face sync {status}")
        self.logger.info(f"Face sync {status}")

    def on_speed_changed(self, value: float) -> None:
        """Handles animation speed change."""
        speed = round(value, 1)
        self.speed_value_label.configure(text=f"{speed}x")
        self.update_status(f"Animation speed: {speed}x")
        self.logger.debug(f"Animation speed changed to {speed}x")



    def get_avatar_state(self) -> dict:
        """Gets current avatar state."""
        return {
            "enabled": self.avatar_enabled,
            "animation_running": self.animation_running,
            "face_sync": self.face_sync_var.get(),
            "speed": self.speed_slider.get()
        }

    def set_avatar_state(self, state: dict) -> None:
        """Sets avatar state from dictionary."""
        if "enabled" in state:
            if state["enabled"] != self.avatar_enabled:
                self.toggle_avatar()
        
        if "face_sync" in state:
            self.face_sync_var.set(state["face_sync"])
        
        if "speed" in state:
            self.speed_slider.set(state["speed"])
            self.on_speed_changed(state["speed"])
        
        if "animation_running" in state and state["animation_running"]:
            if self.avatar_enabled and not self.animation_running:
                self.start_animation()

# Threading Best Practices Demonstration
def demonstrate_ui_thread_call_best_practices():
    """
    Demonstrate best practices for thread-safe UI operations.
    
    This function shows how to properly use ui_thread_call for:
    1. UI updates from background threads
    2. Error handling in threaded operations
    3. Proper UI root registration
    4. Safe component lifecycle management
    """
    import threading
    import time
    from src.desktop.ui.utilities import ui_thread_call, register_ui_root, get_ui_root_info
    
    logger = logging.getLogger("ui_thread_demo")
    
    logger.info("=== UI Thread Call Best Practices Demo ===")
    
    # Example 1: Safe UI update from background thread
    def background_ui_update():
        """Simulate background task that needs to update UI."""
        logger.info("Background thread starting UI update simulation")
        
        # Simulate some work
        time.sleep(0.5)
        
        # CORRECT: Use ui_thread_call for UI operations
        def update_ui():
            logger.info("UI update executed on main thread")
            # In real code, this would be widget.configure() calls
        
        ui_thread_call(update_ui)
        logger.info("Background thread finished")
    
    # Example 2: Thread-safe error handling
    def safe_operation_with_errors():
        """Show how to handle errors safely in threaded operations."""
        
        def risky_background_operation():
            """Simulate an operation that might fail."""
            time.sleep(0.2)
            if True:  # Simulate error condition
                # CORRECT: Use ui_thread_call for error UI updates
                ui_thread_call(lambda: logger.info("Error UI update on main thread"))
                raise RuntimeError("Simulated error for demo")
        
        try:
            thread = threading.Thread(target=risky_background_operation, daemon=True)
            thread.start()
            thread.join(timeout=1.0)  # Don't hang forever
        except Exception as e:
            logger.info(f"Handled background thread error: {e}")
    
    # Example 3: Check UI root info
    root_info = get_ui_root_info()
    logger.info(f"UI Root Info: {root_info['total_registered']} registered, "
               f"CustomTkinter available: {root_info['customtkinter_available']}, "
               f"On main thread: {root_info['current_thread_is_main']}")
    
    # Run demonstrations
    logger.info("Running background UI update demo...")
    bg_thread = threading.Thread(target=background_ui_update, daemon=True)
    bg_thread.start()
    bg_thread.join(timeout=2.0)
    
    logger.info("Running error handling demo...")
    safe_operation_with_errors()
    
    logger.info("=== End UI Thread Call Demo ===")

# Best Practices Summary
"""
UI Thread Call Best Practices for TalkBridge Desktop:

1. ALWAYS use ui_thread_call() for UI operations from background threads:
   ✅ ui_thread_call(self.button.configure, text="New Text")
   ❌ self.button.configure(text="New Text")  # Direct call from bg thread

2. Register UI roots early in component lifecycle:
   ✅ register_ui_root(parent.winfo_toplevel())
   
3. Create dedicated UI update methods for complex operations:
   ✅ def _update_status_ui(self, message): ...
       ui_thread_call(self._update_status_ui, message)
   
4. Handle errors safely in threaded operations:
   ✅ try: risky_operation()
       except Exception as e:
           ui_thread_call(self._show_error_ui, str(e))
           
5. Use daemon threads for background operations:
   ✅ threading.Thread(target=bg_task, daemon=True).start()
   
6. Check thread safety in error handlers:
   ✅ ui_thread_call(self._cleanup_ui) if not is_ui_thread() else self._cleanup_ui()
   
7. Avoid blocking the main thread:
   ✅ Use background threads for I/O, computation, camera operations
   ❌ time.sleep() or blocking operations on main thread

The ui_thread_call implementation automatically:
- Detects current thread context
- Schedules operations on main thread when needed
- Provides error handling and logging
- Manages UI root lifecycle safely
"""
