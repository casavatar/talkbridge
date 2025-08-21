#!/usr/bin/env python3
"""
TalkBridge Desktop - Chat Tab
=============================

Pestaña de chat traducido con entrada por voz y respuesta hablada.

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
"""

import logging
import os
from typing import Optional, List
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QLabel, QComboBox, QScrollArea, QFrame, QSpacerItem,
    QSizePolicy, QProgressBar, QMessageBox, QGroupBox
)
from PySide6.QtCore import Signal, QTimer, QThread, QObject, Qt
from PySide6.QtGui import QFont, QIcon, QPalette, QColor

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.audio.capture import AudioCapture
    from src.stt.whisper_engine import WhisperEngine
    from src.translation.translator import Translator
    from src.ollama.conversation_manager import ConversationManager
    from src.tts.synthesizer import synthesize_voice
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    MODULES_AVAILABLE = False


class AudioRecordingWorker(QObject):
    """Worker thread for audio recording."""
    
    recording_finished = Signal(str)  # audio_file_path
    error_occurred = Signal(str)  # error_message
    
    def __init__(self, duration=5):
        super().__init__()
        self.duration = duration
        self.audio_capture = None
        
    def start_recording(self):
        """Start audio recording."""
        try:
            if MODULES_AVAILABLE:
                self.audio_capture = AudioCapture()
                audio_path = self.audio_capture.record_audio(duration=self.duration)
                self.recording_finished.emit(audio_path)
            else:
                # Demo mode
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                self.recording_finished.emit(temp_file.name)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ChatMessage(QFrame):
    """Widget para mostrar un mensaje individual en el chat."""
    
    def __init__(self, text: str, is_user: bool = True, translation: str = None):
        super().__init__()
        self.setup_ui(text, is_user, translation)
        
    def setup_ui(self, text: str, is_user: bool, translation: str):
        """Configura la UI del mensaje."""
        self.setFrameStyle(QFrame.Shape.Box)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Etiqueta de tipo de mensaje
        role_label = QLabel("🗣️ Tú" if is_user else "🤖 Asistente")
        role_font = QFont()
        role_font.setBold(True)
        role_label.setFont(role_font)
        layout.addWidget(role_label)
        
        # Texto del mensaje
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(message_label)
        
        # Traducción si está disponible
        if translation and translation != text:
            translation_label = QLabel(f"📝 Traducción: {translation}")
            translation_label.setWordWrap(True)
            translation_label.setStyleSheet("padding: 5px; background-color: #e8f4f8; border-radius: 5px; font-style: italic;")
            layout.addWidget(translation_label)
        
        # Estilo según el tipo de mensaje
        if is_user:
            self.setStyleSheet("QFrame { background-color: #e3f2fd; border-radius: 10px; }")
        else:
            self.setStyleSheet("QFrame { background-color: #f3e5f5; border-radius: 10px; }")


class ChatTab(QWidget):
    """
    Pestaña de chat traducido con entrada por voz.
    
    Características:
    - Grabación de voz
    - Transcripción automática
    - Traducción en tiempo real
    - Respuesta de IA
    - Síntesis de voz para respuestas
    """
    
    # Señales
    status_changed = Signal(str)  # message
    error_occurred = Signal(str)  # error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("talkbridge.desktop.chat")
        
        # Estado
        self.is_recording = False
        self.is_processing = False
        
        # Servicios backend
        self.whisper_engine = None
        self.translator = None
        self.conversation_manager = None
        
        # UI Components
        self.chat_area = None
        self.chat_scroll = None
        self.record_button = None
        self.progress_bar = None
        self.language_combo = None
        self.status_label = None
        
        # Workers
        self.recording_worker = None
        self.recording_thread = None
        
        self.setup_ui()
        self.initialize_services()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title_label = QLabel("💬 Chat Traducido con IA")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Configuración de idioma
        config_group = QGroupBox("⚙️ Configuración")
        config_layout = QHBoxLayout(config_group)
        
        config_layout.addWidget(QLabel("Idioma de entrada:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "Español (es)", "English (en)", "Français (fr)", 
            "Deutsch (de)", "Italiano (it)", "Português (pt)"
        ])
        config_layout.addWidget(self.language_combo)
        config_layout.addStretch()
        
        layout.addWidget(config_group)
        
        # Área de chat
        chat_group = QGroupBox("💭 Conversación")
        chat_layout = QVBoxLayout(chat_group)
        
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setMinimumHeight(300)
        
        self.chat_area = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_area)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_area)
        
        chat_layout.addWidget(self.chat_scroll)
        layout.addWidget(chat_group)
        
        # Controles de grabación
        controls_group = QGroupBox("🎤 Controles de Voz")
        controls_layout = QVBoxLayout(controls_group)
        
        # Botón de grabación
        button_layout = QHBoxLayout()
        self.record_button = QPushButton("🎤 Iniciar Grabación")
        self.record_button.setMinimumHeight(50)
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.record_button.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_button)
        
        controls_layout.addLayout(button_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        # Estado
        self.status_label = QLabel("✅ Listo para grabar")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        controls_layout.addWidget(self.status_label)
        
        layout.addWidget(controls_group)
        
        # Botón de limpiar chat
        clear_button = QPushButton("🗑️ Limpiar Chat")
        clear_button.clicked.connect(self.clear_chat)
        clear_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; border-radius: 5px; }")
        layout.addWidget(clear_button)
        
    def initialize_services(self):
        """Inicializa los servicios backend."""
        try:
            if MODULES_AVAILABLE:
                self.whisper_engine = WhisperEngine()
                self.translator = Translator()
                self.conversation_manager = ConversationManager()
                self.logger.info("Backend services initialized successfully")
            else:
                self.logger.warning("Running in demo mode - backend services not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            self.show_error(f"Error al inicializar servicios: {e}")
    
    def toggle_recording(self):
        """Inicia o detiene la grabación de audio."""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Inicia la grabación de audio."""
        if self.is_processing:
            return
            
        self.is_recording = True
        self.record_button.setText("⏹️ Detener Grabación")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        self.status_label.setText("🎤 Grabando...")
        self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        
        # Crear worker para grabación
        self.recording_worker = AudioRecordingWorker(duration=5)
        self.recording_thread = QThread()
        self.recording_worker.moveToThread(self.recording_thread)
        
        # Conectar señales
        self.recording_worker.recording_finished.connect(self.on_recording_finished)
        self.recording_worker.error_occurred.connect(self.on_recording_error)
        self.recording_thread.started.connect(self.recording_worker.start_recording)
        
        self.recording_thread.start()
        
        # Timer para simular progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 50)  # 5 segundos = 50 * 100ms
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        self.progress_timer.start(100)
    
    def stop_recording(self):
        """Detiene la grabación de audio."""
        self.is_recording = False
        if hasattr(self, 'progress_timer'):
            self.progress_timer.stop()
        
        self.reset_record_button()
    
    def update_progress(self):
        """Actualiza la barra de progreso."""
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)
        
        if self.progress_value >= 50:
            self.progress_timer.stop()
    
    def on_recording_finished(self, audio_path: str):
        """Maneja el fin de la grabación."""
        self.stop_recording()
        self.progress_bar.setVisible(False)
        self.status_label.setText("⚙️ Procesando audio...")
        self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
        
        # Procesar el audio grabado
        self.process_audio(audio_path)
    
    def on_recording_error(self, error_message: str):
        """Maneja errores de grabación."""
        self.stop_recording()
        self.progress_bar.setVisible(False)
        self.show_error(f"Error en grabación: {error_message}")
        self.reset_record_button()
    
    def process_audio(self, audio_path: str):
        """Procesa el audio grabado: transcripción, traducción y respuesta."""
        if self.is_processing:
            return
            
        self.is_processing = True
        
        try:
            # 1. Transcripción
            self.status_label.setText("📝 Transcribiendo...")
            if MODULES_AVAILABLE and self.whisper_engine:
                transcription = self.whisper_engine.transcribe(audio_path)
            else:
                # Demo mode
                transcription = "Texto transcrito de ejemplo (modo demo)"
            
            if not transcription.strip():
                self.show_error("No se pudo transcribir el audio. Intente hablar más claro.")
                return
            
            # 2. Traducción (si es necesario)
            self.status_label.setText("🌐 Traduciendo...")
            source_lang = self.language_combo.currentText().split('(')[1].split(')')[0]
            
            if MODULES_AVAILABLE and self.translator:
                if source_lang != 'es':  # Traducir al español si no está en español
                    translation = self.translator.translate(transcription, source_lang, 'es')
                else:
                    translation = transcription
            else:
                # Demo mode
                translation = f"Traducción de: {transcription} (modo demo)"
            
            # Agregar mensaje del usuario al chat
            self.add_message(transcription, is_user=True, translation=translation if translation != transcription else None)
            
            # 3. Generar respuesta con IA
            self.status_label.setText("🤖 Generando respuesta...")
            if MODULES_AVAILABLE and self.conversation_manager:
                response = self.conversation_manager.get_response(translation)
            else:
                # Demo mode
                response = f"Esta es una respuesta de ejemplo a: '{translation}'"
            
            # Agregar respuesta del asistente al chat
            self.add_message(response, is_user=False)
            
            # 4. Síntesis de voz para la respuesta
            self.status_label.setText("🔊 Generando audio...")
            if MODULES_AVAILABLE:
                try:
                    audio_output = synthesize_voice(response, language="es")
                    # Aquí podrías reproducir el audio
                    self.logger.info("Audio generated successfully")
                except Exception as e:
                    self.logger.warning(f"TTS failed: {e}")
            
            self.status_label.setText("✅ Completado")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
        except Exception as e:
            self.show_error(f"Error procesando audio: {e}")
            self.logger.error(f"Audio processing error: {e}")
        finally:
            self.is_processing = False
            self.reset_record_button()
            
            # Limpiar archivo temporal
            try:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
            except:
                pass
    
    def add_message(self, text: str, is_user: bool = True, translation: str = None):
        """Agrega un mensaje al área de chat."""
        message_widget = ChatMessage(text, is_user, translation)
        self.chat_layout.addWidget(message_widget)
        
        # Scroll automático al final
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
    
    def clear_chat(self):
        """Limpia el área de chat."""
        # Eliminar todos los widgets del chat
        while self.chat_layout.count():
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def reset_record_button(self):
        """Resetea el botón de grabación al estado inicial."""
        self.record_button.setText("🎤 Iniciar Grabación")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
    
    def show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.status_label.setText(f"❌ Error: {message}")
        self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        self.error_occurred.emit(message)
        
        # Resetear estado después de unos segundos
        QTimer.singleShot(5000, lambda: (
            self.status_label.setText("✅ Listo para grabar"),
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        ))
