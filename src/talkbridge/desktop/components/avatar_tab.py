#!/usr/bin/env python3
"""
TalkBridge Desktop - Avatar Tab (CustomTkinter)
===============================================

Avatar display and animation tab with CustomTkinter

Author: TalkBridge Team
Date: 2025-09-03
Version: 2.0

Requirements:
- customtkinter
- tkinter
- opencv-python (opti    def show_camera_unavailable_message(self):
        """Display camera unavailable message to user."""
        try:
            # Update UI on main thread
            self.update_status("Camera not available")
            if hasattr(self, 'start_camera_button'):
                self.start_camera_button.configure(text="Camera Unavailable", state="disabled")
        except Exception as e:
            self.logger.error(f"Failed to update camera unavailable message: {e}")
    
    def _retry_frame_read_async(self, retry_count: int = 3):
        """Retry frame reading asynchronously without blocking UI."""
        def retry_read():
            for retry in range(retry_count):
                if not self.cap or not self.cap.isOpened():
                    return False
                    
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    # Schedule frame processing on UI thread
                    ui_thread_call(self._process_successful_frame, frame)
                    return True
                    
                # Small delay between retries (in background thread)
                import threading
                threading.Event().wait(0.01)
            
            # All retries failed
            return False
        
        def on_retry_complete(success):
            if not success:
                self.logger.error("Multiple frame read failures - stopping camera")
                self.stop_camera()
                self._show_camera_fallback("Camera read error")
                if MODERN_SYSTEMS_AVAILABLE:
                    handle_user_facing_error(
                        ErrorCategory.AUDIO_DEVICE_ERROR,  # Using closest category
                        details="Camera frame read failures",
                        context="Camera"
                    )
        
        def on_retry_error(error):
            self.logger.error(f"Error during frame read retry: {error}")
            self.stop_camera()
            self._show_camera_fallback("Camera error")
        
        # Run retry logic asynchronously
        if MODERN_SYSTEMS_AVAILABLE:
            run_async(
                retry_read,
                on_success=on_retry_complete,
                on_error=on_retry_error,
                task_name="camera_frame_retry"
            )
        else:
            # Fallback: run in separate thread
            threading.Thread(target=lambda: on_retry_complete(retry_read()), daemon=True).start()
    
    def _process_successful_frame(self, frame):
        """Process a successfully read frame (called on UI thread)."""
        try:
            # Flip frame horizontally for mirror effect
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
                frame = cv2.resize(frame, (400, 300))
            except Exception as resize_error:
                self.logger.error(f"Frame resize error: {resize_error}")
                return
            
            # Convert to display format
            self._display_frame(frame)
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")ediapipe (optional)
======================================================================
"""

import logging
import time
import threading
from typing import Optional
import tkinter as tk
import customtkinter as ctk

# Import notification and error handling systems
try:
    from talkbridge.ui.notifier import notify_error, notify_warn, notify_info
    from talkbridge.errors import ErrorCategory, handle_user_facing_error
    from talkbridge.utils.async_runner import run_async, ui_thread_call
    MODERN_SYSTEMS_AVAILABLE = True
except ImportError:
    MODERN_SYSTEMS_AVAILABLE = False

# Import logging utilities
try:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from talkbridge.logging_config import get_logger, log_exception, add_error_context
    LOGGING_UTILS_AVAILABLE = True
except ImportError:
    LOGGING_UTILS_AVAILABLE = False

# Import UI utilities and theme
try:
    from talkbridge.desktop.ui.ui_utils import clean_text
    from talkbridge.desktop.ui.theme import ComponentThemes, Typography, ColorPalette
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

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
        
        # Logger with enhanced error handling
        self.logger = logging.getLogger("talkbridge.desktop.avatar")
        
        # Add error context for better debugging
        if LOGGING_UTILS_AVAILABLE:
            add_error_context(self.logger, "AvatarTab")
        
        # Video capture
        self.cap: Optional[cv2.VideoCapture] = None if not CV2_AVAILABLE else None
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
        title_label = ctk.CTkLabel(
            self.main_frame,
            text=clean_text("Avatar & Animation") if THEME_AVAILABLE else "Avatar & Animation",
            **ComponentThemes.get_label_theme("title") if THEME_AVAILABLE else {"font": ctk.CTkFont(size=18, weight="bold")}
        )
        title_label.pack(pady=(10, 5))
        
        # Main content frame
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left panel - Video display
        video_frame = ctk.CTkFrame(content_frame)
        video_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        video_label = ctk.CTkLabel(
            video_frame,
            text=clean_text("Video Display") if THEME_AVAILABLE else "Video Display",
            **ComponentThemes.get_label_theme("subtitle") if THEME_AVAILABLE else {"font": ctk.CTkFont(size=14, weight="bold")}
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
        
        self.start_camera_button = ctk.CTkButton(
            video_controls,
            text=clean_text("Start Camera") if THEME_AVAILABLE else "Start Camera",
            command=self.toggle_camera,
            **ComponentThemes.get_button_theme("success") if THEME_AVAILABLE else {"fg_color": "#4CAF50", "hover_color": "#45a049"}
        )
        self.start_camera_button.pack(side="left", padx=5, pady=5)
        
        self.animation_button = ctk.CTkButton(
            video_controls,
            text=clean_text("Start Animation") if THEME_AVAILABLE else "Start Animation",
            command=self.toggle_animation,
            **ComponentThemes.get_button_theme() if THEME_AVAILABLE else {"fg_color": "#2196F3", "hover_color": "#1976D2"}
        )
        self.animation_button.pack(side="left", padx=5, pady=5)
        
        # Right panel - Controls
        controls_frame = ctk.CTkFrame(content_frame)
        controls_frame.pack(side="right", fill="y", padx=(5, 10), pady=10)
        
        controls_label = ctk.CTkLabel(
            controls_frame,
            text=clean_text("Controls") if THEME_AVAILABLE else "Controls",
            **ComponentThemes.get_label_theme("subtitle") if THEME_AVAILABLE else {"font": ctk.CTkFont(size=14, weight="bold")}
        )
        controls_label.pack(pady=(10, 5))
        
        # Quality settings
        quality_frame = ctk.CTkFrame(controls_frame)
        quality_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(quality_frame, text=clean_text("Quality:") if THEME_AVAILABLE else "Quality:").pack(pady=(10, 5))
        self.quality_combo = ctk.CTkComboBox(
            quality_frame,
            values=["Low", "Medium", "High", "Ultra"],
            command=self.on_quality_changed,
            **ComponentThemes.get_combobox_theme() if THEME_AVAILABLE else {}
        )
        self.quality_combo.set("Medium")
        self.quality_combo.pack(pady=(0, 10))
        
        # Sensitivity settings
        sensitivity_frame = ctk.CTkFrame(controls_frame)
        sensitivity_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(sensitivity_frame, text=clean_text("Sensitivity:") if THEME_AVAILABLE else "Sensitivity:").pack(pady=(10, 5))
        self.sensitivity_slider = ctk.CTkSlider(
            sensitivity_frame,
            from_=0.1,
            to=1.0,
            command=self.on_sensitivity_changed
        )
        self.sensitivity_slider.set(0.5)
        self.sensitivity_slider.pack(pady=(0, 10))
        
        # Display options
        display_frame = ctk.CTkFrame(controls_frame)
        display_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(display_frame, text=clean_text("Display Options:") if THEME_AVAILABLE else "Display Options:").pack(pady=(10, 5))
        
        self.show_landmarks_var = tk.BooleanVar()
        landmarks_check = ctk.CTkCheckBox(
            display_frame,
            text=clean_text("Show Landmarks") if THEME_AVAILABLE else "Show Landmarks",
            variable=self.show_landmarks_var,
            command=self.on_landmarks_changed,
            **ComponentThemes.get_checkbox_theme() if THEME_AVAILABLE else {}
        )
        landmarks_check.pack(pady=2)
        
        self.show_mesh_var = tk.BooleanVar()
        mesh_check = ctk.CTkCheckBox(
            display_frame,
            text=clean_text("Show Face Mesh") if THEME_AVAILABLE else "Show Face Mesh",
            variable=self.show_mesh_var,
            command=self.on_mesh_changed,
            **ComponentThemes.get_checkbox_theme() if THEME_AVAILABLE else {}
        )
        mesh_check.pack(pady=2)
        
        # Status area
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Camera: Inactive | Animation: Disabled",
            **ComponentThemes.get_label_theme("caption") if THEME_AVAILABLE else {"font": ctk.CTkFont(size=10), "text_color": "gray"}
        )
        self.status_label.pack(pady=10)
        
        self.logger.info("Avatar tab UI setup completed")

    def initialize_components(self) -> None:
        """Initialize avatar components."""
        if MEDIAPIPE_AVAILABLE:
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
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
        try:
            # Update UI on main thread
            self.update_status("Camera not available")
            if hasattr(self, 'start_camera_button'):
                self.start_camera_button.configure(text="Camera Unavailable", state="disabled")
        except Exception as e:
            self.logger.debug(f"Could not update camera UI: {e}")

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
                    self.cap = cv2.VideoCapture(idx)
                    
                    # Set camera properties for better compatibility
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
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
                
                # Set camera as inactive and show fallback
                self.camera_active = False
                self.update_status("No camera found")
                self._show_camera_fallback("No camera found. Please connect a camera device.")
                return  # Exit gracefully instead of raising
                
            # Camera successfully opened
            self.camera_active = True
            self.start_camera_button.configure(text="📹 Stop Camera", fg_color="red")
            self.update_status("Camera: Active")
            
            # Start video loop
            self.update_video_frame()
            
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
            
            self.update_status(error_message)
            
            # Show fallback content
            self._show_camera_fallback(error_message)

    def stop_camera(self) -> None:
        """Stop camera capture."""
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.camera_active = False
        self.start_camera_button.configure(text="📹 Start Camera", fg_color="#4CAF50")
        
        # Clear canvas
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
                self._retry_frame_read_async(retry_count=3)
                return
                
            # Flip frame horizontally for mirror effect
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
                frame = cv2.resize(frame, (400, 300))
            except Exception as resize_error:
                self.logger.error(f"Frame resize error: {resize_error}")
                return
            
            # Convert to RGB and then to PhotoImage
            try:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            except Exception as color_error:
                self.logger.error(f"Color conversion error: {color_error}")
                return
            
            # Convert to PIL Image and then to PhotoImage
            try:
                from PIL import Image, ImageTk
                pil_image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update canvas
                self.avatar_canvas.delete("all")
                self.avatar_canvas.create_image(200, 150, image=photo)
                self.avatar_canvas.image = photo  # Keep a reference
                
            except ImportError:
                # Fallback without PIL - use basic text
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
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                self.face_detected = True
                
                for face_landmarks in results.multi_face_landmarks:
                    # Draw landmarks if enabled
                    if self.show_landmarks:
                        for landmark in face_landmarks.landmark:
                            x = int(landmark.x * frame.shape[1])
                            y = int(landmark.y * frame.shape[0])
                            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                    
                    # Draw face mesh if enabled
                    if self.show_mesh:
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame,
                            face_landmarks,
                            mp.solutions.face_mesh.FACEMESH_CONTOURS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(
                                color=(0, 255, 0), thickness=1, circle_radius=1
                            )
                        )
            else:
                self.face_detected = False
                
        except Exception as e:
            self.logger.exception("Face detection error:")
            
        return frame

    def toggle_animation(self) -> None:
        """Toggle animation on/off."""
        self.animation_enabled = not self.animation_enabled
        
        if self.animation_enabled:
            self.animation_button.configure(text="Stop Animation", fg_color="red")
            self.update_status("Animation: Enabled")
        else:
            self.animation_button.configure(text="Start Animation", fg_color="#2196F3")
            self.update_status("Animation: Disabled")

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
        self.show_landmarks = self.show_landmarks_var.get()
        self.logger.info(f"Show landmarks: {self.show_landmarks}")

    def on_mesh_changed(self) -> None:
        """Handle mesh display toggle."""
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
            from_=0.1,
            to=2.0,
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
            self.toggle_button.configure(text="Disable Avatar")
            self.animation_button.configure(state="normal")
            self.update_status("Avatar enabled")
            self.logger.info("Avatar enabled")
        else:
            self.toggle_button.configure(text="Enable Avatar")
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
        self.animation_button.configure(text="Stop Animation")
        self.update_status("Animation running")
        self.logger.info("Avatar animation started")
        
        # Add visual feedback to canvas
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
        self.animation_button.configure(text="Start Animation")
        self.update_status("Animation stopped")
        self.logger.info("Avatar animation stopped")
        
        # Remove animation visual feedback
        self.avatar_canvas.delete("animation")

    def reset_avatar(self) -> None:
        """Resets avatar to default state."""
        self.stop_animation()
        self.avatar_enabled = False
        self.toggle_button.configure(text="Enable Avatar")
        self.animation_button.configure(state="disabled")
        self.face_sync_var.set(False)
        self.speed_slider.set(1.0)
        self.speed_value_label.configure(text="1.0x")
        
        # Clear canvas
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

    def update_status(self, status: str) -> None:
        """Updates the status label."""
        if self.status_label:
            self.status_label.configure(text=status)
            self.parent.update_idletasks()

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
