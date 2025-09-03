#!/usr/bin/env python3
"""
TalkBridge Desktop - Avatar Tab
============================================

Animated Avatar tab synchronized with audio.
This refactored version improves code organization, error handling,
and maintainability.

Author: TalkBridge Team
Date: 2025-08-28
Version: 2.0

Requirements:
- PyQt6
- mediapipe
- opencv-python
======================================================================
"""

import logging
import os
import cv2
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSlider, QGroupBox, QCheckBox, QSpinBox,
    QFrame, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Signal, QTimer, QThread, QObject, Qt, QMutex
from PySide6.QtGui import QFont, QImage, QPixmap

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.animation.face_sync import FaceSync
    from src.audio.player import AudioPlayer
    ANIMATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Animation modules not available: {e}")
    ANIMATION_AVAILABLE = False


class CameraState(Enum):
    """Camera state enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class AnimationConfig:
    """Configuration for animation parameters."""
    sensitivity: int = 50
    intensity: int = 75
    smoothing: int = 30
    enabled: bool = True


class WebcamWorker(QObject):
    """
    Worker thread to capture frames from the webcam.
    
    This class handles camera operations in a separate thread to prevent
    UI blocking and provides thread-safe communication with the main UI.
    """
    
    # Signals
    frame_ready = Signal(np.ndarray)
    error_occurred = Signal(str)
    state_changed = Signal(str)
    
    def __init__(self, camera_index: int = 0):
        super().__init__()
        self.camera_index = camera_index
        self.camera: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.face_sync: Optional[FaceSync] = None
        self.mutex = QMutex()
        self._init_logging()
    
    def _init_logging(self):
        """Initialize logging for the worker."""
        self.logger = logging.getLogger(f"{__name__}.WebcamWorker")
    
    def initialize_camera(self) -> bool:
        """
        Initialize the camera with error handling.
        
        Returns:
            bool: True if camera initialized successfully, False otherwise.
        """
        try:
            self.state_changed.emit(CameraState.STARTING.value)
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                self.error_occurred.emit("Camera not available")
                return False
            
            # Set camera properties for better performance
            self._configure_camera()
            
            # Initialize face sync if available
            if ANIMATION_AVAILABLE:
                self._initialize_face_sync()
            
            self.logger.info(f"Camera {self.camera_index} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing camera: {e}")
            self.error_occurred.emit(f"Camera initialization failed: {str(e)}")
            return False
    
    def _configure_camera(self):
        """Configure camera properties for optimal performance."""
        if self.camera:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    def _initialize_face_sync(self):
        """Initialize face synchronization module."""
        try:
            self.face_sync = FaceSync()
            self.logger.info("Face sync initialized")
        except Exception as e:
            self.logger.warning(f"Face sync initialization failed: {e}")
            self.face_sync = None
    
    def start_capture(self):
        """Start camera capture loop."""
        if not self.initialize_camera():
            return
        
        self.is_running = True
        self.state_changed.emit(CameraState.RUNNING.value)
        self._capture_loop()
    
    def _capture_loop(self):
        """Main capture loop running in separate thread."""
        timer = QTimer()
        timer.timeout.connect(self._capture_frame)
        timer.start(33)  # ~30 FPS
        
        while self.is_running and self.camera and self.camera.isOpened():
            pass
    
    def _capture_frame(self):
        """Capture and process a single frame."""
        if not self.is_running or not self.camera:
            return
        
        with QMutex():
            try:
                ret, frame = self.camera.read()
                if ret:
                    processed_frame = self._process_frame(frame)
                    self.frame_ready.emit(processed_frame)
                else:
                    self.error_occurred.emit("Failed to capture frame")
                    
            except Exception as e:
                self.logger.error(f"Frame capture error: {e}")
                self.error_occurred.emit(f"Frame processing error: {str(e)}")
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process frame with face sync if available.
        
        Args:
            frame: Raw frame from camera
            
        Returns:
            Processed frame
        """
        if self.face_sync and ANIMATION_AVAILABLE:
            try:
                return self.face_sync.process_frame(frame)
            except Exception as e:
                self.logger.warning(f"Face sync processing error: {e}")
        
        return frame
    
    def stop_capture(self):
        """Stop camera capture and cleanup resources."""
        self.is_running = False
        self.state_changed.emit(CameraState.STOPPED.value)
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        if self.face_sync:
            self.face_sync = None
        
        self.logger.info("Camera capture stopped")
    
    def update_animation_config(self, config: AnimationConfig):
        """Update animation configuration."""
        if self.face_sync and config.enabled:
            try:
                # Apply configuration to face sync
                # This would depend on the FaceSync API
                pass
            except Exception as e:
                self.logger.error(f"Failed to update animation config: {e}")


class CameraController:
    """Controller for camera operations."""
    
    def __init__(self):
        self.worker: Optional[WebcamWorker] = None
        self.thread: Optional[QThread] = None
        self.state = CameraState.STOPPED
        self.logger = logging.getLogger(f"{__name__}.CameraController")
    
    def start(self, camera_index: int = 0) -> bool:
        """Start camera capture in separate thread."""
        if self.state == CameraState.RUNNING:
            self.logger.warning("Camera already running")
            return True
        
        try:
            self.worker = WebcamWorker(camera_index)
            self.thread = QThread()
            
            # Move worker to thread
            self.worker.moveToThread(self.thread)
            
            # Connect signals
            self.thread.started.connect(self.worker.start_capture)
            self.worker.state_changed.connect(self._on_state_changed)
            
            # Start thread
            self.thread.start()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start camera: {e}")
            return False
    
    def stop(self):
        """Stop camera capture and cleanup."""
        if self.worker:
            self.worker.stop_capture()
        
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(3000)  # Wait up to 3 seconds
        
        self.worker = None
        self.thread = None
        self.state = CameraState.STOPPED
    
    def _on_state_changed(self, state: str):
        """Handle state changes from worker."""
        self.state = CameraState(state)
        self.logger.info(f"Camera state changed to: {state}")


class UIComponents:
    """Factory class for creating UI components with consistent styling."""
    
    @staticmethod
    def create_styled_button(text: str, icon: str = "") -> QPushButton:
        """Create a styled button."""
        button = QPushButton(f"{icon} {text}" if icon else text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        return button
    
    @staticmethod
    def create_status_label(text: str) -> QLabel:
        """Create a styled status label."""
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
        return label
    
    @staticmethod
    def create_control_slider(min_val: int, max_val: int, default_val: int) -> QSlider:
        """Create a styled control slider."""
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #2d2d2d;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 1px solid #1976D2;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #1976D2;
            }
        """)
        return slider


class AvatarTab(QWidget):
    """
    Main Avatar Tab widget with improved architecture.
    
    This refactored version separates concerns and improves maintainability:
    - Camera operations handled by CameraController
    - UI components created by UIComponents factory
    - Configuration managed by AnimationConfig dataclass
    - Better error handling and logging
    """
    
    # Signals
    error_occurred = Signal(str)
    audio_sync_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera_controller = CameraController()
        self.animation_config = AnimationConfig()
        self.audio_player: Optional[AudioPlayer] = None
        
        self._init_logging()
        self._init_ui()
        self._connect_signals()
        self._setup_timers()
    
    def _init_logging(self):
        """Initialize logging for the tab."""
        self.logger = logging.getLogger(f"{__name__}.AvatarTab")
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Create main components
        self._create_video_section(layout)
        self._create_controls_section(layout)
        self._create_animation_controls(layout)
        self._create_status_section(layout)
        
        # Set initial state
        self._update_ui_state(CameraState.STOPPED)
    
    def _create_video_section(self, parent_layout: QVBoxLayout):
        """Create the video display section."""
        video_group = QGroupBox("Camera Feed")
        video_layout = QVBoxLayout(video_group)
        
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 2px solid #555;
                border-radius: 10px;
                background-color: #1e1e1e;
                color: #888;
                font-size: 16px;
            }
        """)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setText("📷\nCamera disconnected\n\nClick 'Start Camera' to begin")
        
        video_layout.addWidget(self.video_label)
        parent_layout.addWidget(video_group)
    
    def _create_controls_section(self, parent_layout: QVBoxLayout):
        """Create the camera controls section."""
        controls_group = QGroupBox("Camera Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        self.start_button = UIComponents.create_styled_button("Start Camera", "📹")
        self.start_button.clicked.connect(self._toggle_camera)
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Camera 0", "Camera 1", "Camera 2"])
        self.camera_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
            }
        """)
        
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(QLabel("Camera:"))
        controls_layout.addWidget(self.camera_combo)
        controls_layout.addStretch()
        
        parent_layout.addWidget(controls_group)
    
    def _create_animation_controls(self, parent_layout: QVBoxLayout):
        """Create animation control section."""
        anim_group = QGroupBox("Animation Settings")
        anim_layout = QVBoxLayout(anim_group)
        
        # Enable/Disable animation
        self.animation_checkbox = QCheckBox("Enable Animation")
        self.animation_checkbox.setChecked(self.animation_config.enabled)
        self.animation_checkbox.toggled.connect(self._on_animation_toggled)
        anim_layout.addWidget(self.animation_checkbox)
        
        # Create parameter controls
        self._create_parameter_controls(anim_layout)
        
        parent_layout.addWidget(anim_group)
    
    def _create_parameter_controls(self, parent_layout: QVBoxLayout):
        """Create animation parameter controls."""
        params = [
            ("Sensitivity", "sensitivity", 0, 100, self.animation_config.sensitivity),
            ("Intensity", "intensity", 0, 100, self.animation_config.intensity),
            ("Smoothing", "smoothing", 0, 100, self.animation_config.smoothing)
        ]
        
        for label_text, attr_name, min_val, max_val, default_val in params:
            param_layout = QHBoxLayout()
            
            label = QLabel(f"{label_text}:")
            label.setMinimumWidth(80)
            
            slider = UIComponents.create_control_slider(min_val, max_val, default_val)
            value_label = QLabel(str(default_val))
            value_label.setMinimumWidth(30)
            
            # Store references
            setattr(self, f"{attr_name}_slider", slider)
            setattr(self, f"{attr_name}_label", value_label)
            
            # Connect signals
            slider.valueChanged.connect(
                lambda val, attr=attr_name: self._on_parameter_changed(attr, val)
            )
            
            param_layout.addWidget(label)
            param_layout.addWidget(slider)
            param_layout.addWidget(value_label)
            
            parent_layout.addLayout(param_layout)
    
    def _create_status_section(self, parent_layout: QVBoxLayout):
        """Create status display section."""
        self.status_label = UIComponents.create_status_label("✅ Ready")
        parent_layout.addWidget(self.status_label)
    
    def _connect_signals(self):
        """Connect internal signals."""
        if self.camera_controller.worker:
            self.camera_controller.worker.frame_ready.connect(self._update_frame)
            self.camera_controller.worker.error_occurred.connect(self._handle_camera_error)
    
    def _setup_timers(self):
        """Setup internal timers."""
        self.status_timer = QTimer()
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self._reset_status)
    
    def _toggle_camera(self):
        """Toggle camera on/off."""
        if self.camera_controller.state == CameraState.RUNNING:
            self._stop_camera()
        else:
            self._start_camera()
    
    def _start_camera(self):
        """Start camera capture."""
        camera_index = self.camera_combo.currentIndex()
        
        if self.camera_controller.start(camera_index):
            self._update_ui_state(CameraState.STARTING)
            self._show_status("📹 Starting camera...", "info")
        else:
            self._show_status("❌ Failed to start camera", "error")
    
    def _stop_camera(self):
        """Stop camera capture."""
        self.camera_controller.stop()
        self._update_ui_state(CameraState.STOPPED)
        self._show_status("⏹️ Camera stopped", "info")
    
    def _update_ui_state(self, state: CameraState):
        """Update UI based on camera state."""
        if state == CameraState.STOPPED:
            self.start_button.setText("📹 Start Camera")
            self.start_button.setEnabled(True)
            self.camera_combo.setEnabled(True)
            self.video_label.setText("📷\nCamera disconnected\n\nClick 'Start Camera' to begin")
            self.video_label.setPixmap(QPixmap())
            
        elif state == CameraState.STARTING:
            self.start_button.setText("⏳ Starting...")
            self.start_button.setEnabled(False)
            self.camera_combo.setEnabled(False)
            
        elif state == CameraState.RUNNING:
            self.start_button.setText("⏹️ Stop Camera")
            self.start_button.setEnabled(True)
            self.camera_combo.setEnabled(False)
            
        elif state == CameraState.ERROR:
            self.start_button.setText("📹 Start Camera")
            self.start_button.setEnabled(True)
            self.camera_combo.setEnabled(True)
    
    def _update_frame(self, frame: np.ndarray):
        """Update the displayed frame."""
        try:
            # Convert OpenCV frame to Qt format
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Scale image to fit label
            label_size = self.video_label.size()
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                label_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.logger.error(f"Error updating frame: {e}")
            self._show_status(f"❌ Frame update error: {str(e)}", "error")
    
    def _handle_camera_error(self, error_message: str):
        """Handle camera errors."""
        self.logger.error(f"Camera error: {error_message}")
        self._update_ui_state(CameraState.ERROR)
        self._show_status(f"❌ Camera error: {error_message}", "error")
        self.error_occurred.emit(error_message)
    
    def _on_animation_toggled(self, enabled: bool):
        """Handle animation enable/disable."""
        self.animation_config.enabled = enabled
        self._update_animation_config()
        
        status = "enabled" if enabled else "disabled"
        self._show_status(f"🎭 Animation {status}", "info")
    
    def _on_parameter_changed(self, parameter: str, value: int):
        """Handle animation parameter changes."""
        setattr(self.animation_config, parameter, value)
        label = getattr(self, f"{parameter}_label")
        label.setText(str(value))
        
        self._update_animation_config()
    
    def _update_animation_config(self):
        """Update animation configuration."""
        if self.camera_controller.worker:
            self.camera_controller.worker.update_animation_config(self.animation_config)
    
    def _show_status(self, message: str, status_type: str = "info"):
        """Show status message with appropriate styling."""
        colors = {
            "info": "#2196F3",
            "success": "#4CAF50", 
            "warning": "#FF9800",
            "error": "#f44336"
        }
        
        color = colors.get(status_type, colors["info"])
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        
        # Auto-reset status after 5 seconds for non-persistent messages
        if status_type in ["info", "warning"]:
            self.status_timer.start(5000)
    
    def _reset_status(self):
        """Reset status to ready state."""
        self.status_label.setText("✅ Ready")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
    
    def load_audio_for_sync(self, audio_path: str):
        """Load audio file for lip synchronization."""
        try:
            if ANIMATION_AVAILABLE and self.camera_controller.worker and self.camera_controller.worker.face_sync:
                self.camera_controller.worker.face_sync.load_audio(audio_path)
                self._show_status("🎵 Audio loaded for synchronization", "success")
                self.audio_sync_requested.emit(audio_path)
            else:
                self._show_status("❌ Animation not available", "error")
                
        except Exception as e:
            self.logger.error(f"Error loading audio: {e}")
            self._show_status(f"❌ Error loading audio: {str(e)}", "error")
    
    def closeEvent(self, event):
        """Handle tab closure."""
        self.logger.info("Closing avatar tab")
        self._stop_camera()
        super().closeEvent(event)
    
    def __del__(self):
        """Cleanup resources on destruction."""
        if hasattr(self, 'camera_controller'):
            self.camera_controller.stop()
