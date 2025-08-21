#!/usr/bin/env python3
"""
TalkBridge Desktop - Avatar Tab
===============================

Animated Avatar tab synchronized with audio.

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- mediapipe
- opencv-python
======================================================================
"""

import logging
import cv2
import numpy as np
from typing import Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSlider, QGroupBox, QCheckBox, QSpinBox,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, QTimer, QThread, QObject, Qt
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


class WebcamWorker(QObject):
    """Worker thread para capturar frames de la webcam."""
    
    frame_ready = Signal(np.ndarray)  # frame
    error_occurred = Signal(str)  # error_message
    
    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False
        self.face_sync = None
        
    def start_capture(self):
        """Start the webcam capture."""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.error_occurred.emit("No se pudo acceder a la webcam")
                return
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if ANIMATION_AVAILABLE:
                self.face_sync = FaceSync(use_webcam=True)
            
            self.running = True
            while self.running:
                ret, frame = self.cap.read()
                if ret:
                    # Procesar frame con FaceSync si está disponible
                    if self.face_sync:
                        processed_frame = self.face_sync.process_frame(frame)
                        self.frame_ready.emit(processed_frame)
                    else:
                        # Modo demo: solo voltear horizontalmente
                        flipped_frame = cv2.flip(frame, 1)
                        self.frame_ready.emit(flipped_frame)
                else:
                    break
                    
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.cap:
                self.cap.release()
    
    def stop_capture(self):
        """Stop the webcam capture."""
        self.running = False
        if self.face_sync:
            self.face_sync.stop()


class AvatarTab(QWidget):
    """
  Animated avatar tab.
    
    Characteristics:
    -Webcam live view
    -Detection of facial points
    -Lip synchronization with audio
    -Animation parameters configuration
    """
    
    # Señales
    status_changed = Signal(str)  # message
    error_occurred = Signal(str)  # error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("talkbridge.desktop.avatar")
        
        # Estado
        self.webcam_active = False
        self.animation_enabled = True
        
        # Servicios backend
        self.face_sync = None
        self.audio_player = None
        
        # UI Components
        self.video_label = None
        self.start_button = None
        self.status_label = None
        self.animation_controls = {}
        
        # Workers
        self.webcam_worker = None
        self.webcam_thread = None
        
        self.setup_ui()
        self.initialize_services()
        
    def setup_ui(self):
        """Configure the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title_label = QLabel("👤 Avatar Animado")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout()
        
        # Panel izquierdo: Video
        video_group = QGroupBox("📹 Camera view")
        video_layout = QVBoxLayout(video_group)
        
        # Video display
        self.video_label = QLabel()
        self.video_label.setMinimumSize(480, 360)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setText("📷\nDisconnected camera\n\nClick on 'Start camera' to start")
        video_layout.addWidget(self.video_label)
        
        # Video controls
        video_controls_layout = QHBoxLayout()
        
        self.start_button = QPushButton("📹 Iniciar Cámara")
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.start_button.clicked.connect(self.toggle_webcam)
        video_controls_layout.addWidget(self.start_button)
        
        video_controls_layout.addStretch()
        video_layout.addLayout(video_controls_layout)
        
        # Estado
        self.status_label = QLabel("✅ Listo")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        video_layout.addWidget(self.status_label)
        
        main_layout.addWidget(video_group, 2)
        
        # Right Panel: Animation controls
        controls_group = QGroupBox("⚙️ Controles de Animación")
        controls_layout = QVBoxLayout(controls_group)
        
        # Activate/deactivate animation
        self.animation_checkbox = QCheckBox("🎭 Activar Animación Facial")
        self.animation_checkbox.setChecked(True)
        self.animation_checkbox.toggled.connect(self.toggle_animation)
        controls_layout.addWidget(self.animation_checkbox)
        
        controls_layout.addWidget(self.create_separator())
        
        # Facial detection configuration
        face_group = QGroupBox("👤 Facial detection")
        face_layout = QVBoxLayout(face_group)
        
        # Detection sensitivity
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Sensitivity:"))
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)
        self.sensitivity_slider.valueChanged.connect(self.on_sensitivity_changed)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        self.sensitivity_label = QLabel("5")
        sensitivity_layout.addWidget(self.sensitivity_label)
        face_layout.addLayout(sensitivity_layout)

        # Minimum face size
        min_face_layout = QHBoxLayout()
        min_face_layout.addWidget(QLabel("Minimum face size:"))
        self.min_face_spin = QSpinBox()
        self.min_face_spin.setRange(50, 200)
        self.min_face_spin.setValue(100)
        self.min_face_spin.setSuffix(" px")
        min_face_layout.addWidget(self.min_face_spin)
        min_face_layout.addStretch()
        face_layout.addLayout(min_face_layout)
        
        controls_layout.addWidget(face_group)

        # Lip sync configuration
        lips_group = QGroupBox("👄 Lip Sync")
        lips_layout = QVBoxLayout(lips_group)

        # Movement intensity
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("Intensity:"))
        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(1, 10)
        self.intensity_slider.setValue(7)
        self.intensity_slider.valueChanged.connect(self.on_intensity_changed)
        intensity_layout.addWidget(self.intensity_slider)
        self.intensity_label = QLabel("7")
        intensity_layout.addWidget(self.intensity_label)
        lips_layout.addLayout(intensity_layout)

        # Smoothing
        smoothing_layout = QHBoxLayout()
        smoothing_layout.addWidget(QLabel("Smoothing:"))
        self.smoothing_slider = QSlider(Qt.Orientation.Horizontal)
        self.smoothing_slider.setRange(1, 10)
        self.smoothing_slider.setValue(3)
        self.smoothing_slider.valueChanged.connect(self.on_smoothing_changed)
        smoothing_layout.addWidget(self.smoothing_slider)
        self.smoothing_label = QLabel("3")
        smoothing_layout.addWidget(self.smoothing_label)
        lips_layout.addLayout(smoothing_layout)
        
        controls_layout.addWidget(lips_group)

        # Effects configuration
        effects_group = QGroupBox("✨ Visual Effects")
        effects_layout = QVBoxLayout(effects_group)

        self.landmarks_checkbox = QCheckBox("🔍 Show Facial Landmarks")
        self.landmarks_checkbox.setChecked(False)
        effects_layout.addWidget(self.landmarks_checkbox)

        self.mesh_checkbox = QCheckBox("🕸️ Show Facial Mesh")
        self.mesh_checkbox.setChecked(False)
        effects_layout.addWidget(self.mesh_checkbox)
        
        controls_layout.addWidget(effects_group)
        
        controls_layout.addStretch()

        # Reset button
        reset_button = QPushButton("🔄 Reset Values")
        reset_button.clicked.connect(self.reset_settings)
        reset_button.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px; border-radius: 5px; }")
        controls_layout.addWidget(reset_button)
        
        main_layout.addWidget(controls_group, 1)
        
        layout.addLayout(main_layout)
        
    def create_separator(self):
        """Creates a separator line."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line
        
    def initialize_services(self):
        """Initialize backend services."""
        try:
            if ANIMATION_AVAILABLE:
                self.audio_player = AudioPlayer()
                self.logger.info("Animation services initialized successfully")
            else:
                self.logger.warning("Running in demo mode - animation services not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize animation services: {e}")
            self.show_error(f"Error al inicializar servicios de animación: {e}")
    
    def toggle_webcam(self):
        """Start or stop the webcam."""
        if not self.webcam_active:
            self.start_webcam()
        else:
            self.stop_webcam()
    
    def start_webcam(self):
        """Start the webcam capture."""
        try:
            self.webcam_worker = WebcamWorker()
            self.webcam_thread = QThread()
            self.webcam_worker.moveToThread(self.webcam_thread)
            
            # Conectar señales
            self.webcam_worker.frame_ready.connect(self.update_frame)
            self.webcam_worker.error_occurred.connect(self.on_webcam_error)
            self.webcam_thread.started.connect(self.webcam_worker.start_capture)
            
            self.webcam_thread.start()
            
            self.webcam_active = True
            self.start_button.setText("⏹️ Stop camera")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            
            self.status_label.setText("📹 Active Chamber")
            self.status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
            
        except Exception as e:
            self.show_error(f"Error at the start camera: {e}")
    
    def stop_webcam(self):
        """Stop the webcam capture."""
        if self.webcam_worker:
            self.webcam_worker.stop_capture()
        if self.webcam_thread:
            self.webcam_thread.quit()
            self.webcam_thread.wait()
        
        self.webcam_active = False
        self.start_button.setText("📹 Start camera")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        self.video_label.setText("📷\nDisconnected camera\n\nClick on 'Start camera' to start")
        self.status_label.setText("✅ Ready")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
    
    def update_frame(self, frame):
        """Update the frame shown in the UI."""
        try:
            # Convertir frame de OpenCV a QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Scalar image to adjust to the label
            label_size = self.video_label.size()
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.logger.error(f"Error updating frame: {e}")
    
    def on_webcam_error(self, error_message: str):
        """Maneja errores de la webcam."""
        self.show_error(f"Error de cámara: {error_message}")
        self.stop_webcam()
    
    def toggle_animation(self, enabled: bool):
        """Activa o desactiva la animación."""
        self.animation_enabled = enabled
        if self.webcam_worker and hasattr(self.webcam_worker, 'face_sync'):
            if self.webcam_worker.face_sync:
                if enabled:
                    self.webcam_worker.face_sync.start()
                else:
                    self.webcam_worker.face_sync.stop()
    
    def on_sensitivity_changed(self, value: int):
        """Maneja cambios en la sensibilidad."""
        self.sensitivity_label.setText(str(value))
        # Here you would apply the configuration to the animation module
        
    def on_intensity_changed(self, value: int):
        """Maneja cambios en la intensidad."""
        self.intensity_label.setText(str(value))
        # Here you would apply the configuration to the animation module
        
    def on_smoothing_changed(self, value: int):
        """Maneja cambios en el suavizado."""
        self.smoothing_label.setText(str(value))
        # Here you would apply the configuration to the animation module
    
    def reset_settings(self):
        """Restore default values."""
        self.sensitivity_slider.setValue(5)
        self.intensity_slider.setValue(7)
        self.smoothing_slider.setValue(3)
        self.min_face_spin.setValue(100)
        self.animation_checkbox.setChecked(True)
        self.landmarks_checkbox.setChecked(False)
        self.mesh_checkbox.setChecked(False)
    
    def load_audio_for_sync(self, audio_path: str):
        """Load an audio file for lip synchronization."""
        try:
            if ANIMATION_AVAILABLE and self.face_sync:
                self.face_sync.load_audio(audio_path)
                self.status_label.setText("🎵 Audio cargado para sincronización")
                self.status_label.setStyleSheet("color: #9C27B0; font-weight: bold;")
        except Exception as e:
            self.show_error(f"Error cargando audio: {e}")
    
    def show_error(self, message: str):
        """Show an error message."""
        self.status_label.setText(f"❌ Error: {message}")
        self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        self.error_occurred.emit(message)
        
        # Reset the state after a few seconds
        QTimer.singleShot(5000, lambda: (
            self.status_label.setText("✅ Listo"),
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        ))
    
    def closeEvent(self, event):
        """Manage the closure of the tab."""
        if self.webcam_active:
            self.stop_webcam()
        super().closeEvent(event)
