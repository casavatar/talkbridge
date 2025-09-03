#!/usr/bin/env python3
"""
TalkBridge Desktop - Chat Tab
=============================

Translated chat tab with voice input and spoken response.

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
    AUDIO_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Audio module not available: {e}")
    AUDIO_AVAILABLE = False

try:
    from src.stt.whisper_engine import WhisperEngine
    WHISPER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Whisper engine not available: {e}")
    WHISPER_AVAILABLE = False

try:
    from src.translation.translator import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Translator not available: {e}")
    TRANSLATOR_AVAILABLE = False

try:
    from src.ollama.conversation_manager import ConversationManager
    OLLAMA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Ollama module not available: {e}")
    OLLAMA_AVAILABLE = False

try:
    from src.tts.synthesizer import synthesize_voice
    TTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: TTS synthesizer not available: {e}")
    TTS_AVAILABLE = False

MODULES_AVAILABLE = AUDIO_AVAILABLE and WHISPER_AVAILABLE and TRANSLATOR_AVAILABLE


class ChatTheme:
    """Tema oscuro mejorado para la interfaz de chat."""
    
    # Colores base del tema oscuro
    BACKGROUND_MAIN = "#1e1e1e"
    BACKGROUND_SECONDARY = "#2d2d2d"
    BACKGROUND_ELEVATED = "#3c3c3c"
    
    # Colores de texto
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#cccccc"
    TEXT_MUTED = "#999999"
    
    # Colores de acento
    ACCENT_BLUE = "#0078d4"
    ACCENT_BLUE_HOVER = "#106ebe"
    ACCENT_GREEN = "#4CAF50"
    ACCENT_ORANGE = "#FF9800"
    ACCENT_RED = "#f44336"
    
    # Colores para mensajes
    USER_MESSAGE_BG = "#0e3a5f"
    USER_MESSAGE_BORDER = "#1e5a8a"
    ASSISTANT_MESSAGE_BG = "#2d1b3d"
    ASSISTANT_MESSAGE_BORDER = "#4a2c5a"
    
    # Colores para elementos de UI
    INPUT_BACKGROUND = "#3c3c3c"
    INPUT_BORDER = "#555555"
    INPUT_BORDER_FOCUS = "#0078d4"
    
    @staticmethod
    def get_main_style() -> str:
        """Estilo principal para el ChatTab."""
        return f"""
        QWidget {{
            background-color: {ChatTheme.BACKGROUND_MAIN};
            color: {ChatTheme.TEXT_PRIMARY};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        QLabel {{
            color: {ChatTheme.TEXT_PRIMARY};
            background: transparent;
        }}
        
        QComboBox {{
            background-color: {ChatTheme.INPUT_BACKGROUND};
            border: 2px solid {ChatTheme.INPUT_BORDER};
            border-radius: 6px;
            padding: 8px;
            color: {ChatTheme.TEXT_PRIMARY};
            min-width: 150px;
        }}
        
        QComboBox:focus {{
            border-color: {ChatTheme.INPUT_BORDER_FOCUS};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: 2px solid {ChatTheme.TEXT_SECONDARY};
            width: 6px;
            height: 6px;
            border-top: none;
            border-right: none;
            transform: rotate(-45deg);
        }}
        
        QScrollArea {{
            background-color: {ChatTheme.BACKGROUND_SECONDARY};
            border: 1px solid {ChatTheme.INPUT_BORDER};
            border-radius: 8px;
        }}
        
        QScrollBar:vertical {{
            background-color: {ChatTheme.BACKGROUND_SECONDARY};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {ChatTheme.INPUT_BORDER};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {ChatTheme.TEXT_MUTED};
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {ChatTheme.INPUT_BORDER};
            border-radius: 8px;
            margin-top: 1ex;
            color: {ChatTheme.TEXT_PRIMARY};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: {ChatTheme.ACCENT_BLUE};
        }}
        """
    
    @staticmethod
    def get_button_style(button_type: str = "primary") -> str:
        """Estilos para botones según el tipo."""
        if button_type == "primary":
            return f"""
            QPushButton {{
                background-color: {ChatTheme.ACCENT_BLUE};
                color: {ChatTheme.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }}
            
            QPushButton:hover {{
                background-color: {ChatTheme.ACCENT_BLUE_HOVER};
            }}
            
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
            
            QPushButton:disabled {{
                background-color: {ChatTheme.INPUT_BORDER};
                color: {ChatTheme.TEXT_MUTED};
            }}
            """
        elif button_type == "danger":
            return f"""
            QPushButton {{
                background-color: {ChatTheme.ACCENT_RED};
                color: {ChatTheme.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }}
            
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
            
            QPushButton:pressed {{
                background-color: #b71c1c;
            }}
            """
        elif button_type == "recording":
            return f"""
            QPushButton {{
                background-color: {ChatTheme.ACCENT_GREEN};
                color: {ChatTheme.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }}
            
            QPushButton:hover {{
                background-color: #45a049;
            }}
            """
        elif button_type == "stop":
            return f"""
            QPushButton {{
                background-color: {ChatTheme.ACCENT_RED};
                color: {ChatTheme.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }}
            
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
            
            QPushButton:pressed {{
                background-color: #b71c1c;
            }}
            """
        
        return ChatTheme.get_button_style("primary")


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
        role_font.setPointSize(10)
        role_label.setFont(role_font)
        role_label.setStyleSheet(f"color: {ChatTheme.TEXT_SECONDARY}; margin-bottom: 4px;")
        layout.addWidget(role_label)
        
        # Texto del mensaje
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            padding: 10px;
            background-color: {ChatTheme.BACKGROUND_ELEVATED};
            border-radius: 8px;
            color: {ChatTheme.TEXT_PRIMARY};
            font-size: 14px;
            line-height: 1.4;
        """)
        layout.addWidget(message_label)
        
        # Traducción si está disponible
        if translation and translation != text:
            translation_label = QLabel(f"📝 Traducción: {translation}")
            translation_label.setWordWrap(True)
            translation_label.setStyleSheet(f"""
                padding: 8px;
                background-color: {ChatTheme.BACKGROUND_SECONDARY};
                border-radius: 6px;
                border-left: 3px solid {ChatTheme.ACCENT_BLUE};
                color: {ChatTheme.TEXT_SECONDARY};
                font-style: italic;
                font-size: 13px;
                margin-top: 6px;
            """)
            layout.addWidget(translation_label)
        
        # Estilo según el tipo de mensaje
        if is_user:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ChatTheme.USER_MESSAGE_BG};
                    border: 1px solid {ChatTheme.USER_MESSAGE_BORDER};
                    border-radius: 12px;
                    margin: 4px 20px 4px 4px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ChatTheme.ASSISTANT_MESSAGE_BG};
                    border: 1px solid {ChatTheme.ASSISTANT_MESSAGE_BORDER};
                    border-radius: 12px;
                    margin: 4px 4px 4px 20px;
                }}
            """)


class ChatTab(QWidget):
    """
    Translated chat tab with voice input.
    
    Features:
    - Voice recording
    - Automatic transcription
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
        self.conversation_id = None  # Para mantener la conversación activa
        
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
        # Aplicar tema oscuro
        self.setStyleSheet(ChatTheme.get_main_style())
        
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
        title_label.setStyleSheet(f"color: {ChatTheme.TEXT_PRIMARY}; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Language configuration
        config_group = QGroupBox("⚙️ Configuration")
        config_layout = QHBoxLayout(config_group)
        
        config_layout.addWidget(QLabel("Input language:"))
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
        self.record_button.setStyleSheet(ChatTheme.get_button_style("recording"))
        self.record_button.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_button)
        
        controls_layout.addLayout(button_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {ChatTheme.INPUT_BORDER};
                border-radius: 8px;
                background-color: {ChatTheme.BACKGROUND_SECONDARY};
                text-align: center;
                font-weight: bold;
                color: {ChatTheme.TEXT_PRIMARY};
            }}
            
            QProgressBar::chunk {{
                background-color: {ChatTheme.ACCENT_BLUE};
                border-radius: 6px;
            }}
        """)
        controls_layout.addWidget(self.progress_bar)
        
        # Estado
        self.status_label = QLabel("✅ Listo para grabar")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {ChatTheme.ACCENT_GREEN}; font-weight: bold; font-size: 14px;")
        controls_layout.addWidget(self.status_label)
        
        layout.addWidget(controls_group)
        
        # Botón de limpiar chat
        clear_button = QPushButton("🗑️ Limpiar Chat")
        clear_button.clicked.connect(self.clear_chat)
        clear_button.setStyleSheet(ChatTheme.get_button_style("danger"))
        layout.addWidget(clear_button)
        
    def initialize_services(self):
        """Inicializa los servicios backend."""
        try:
            services_initialized = []
            services_failed = []
            
            # Initialize Whisper Engine
            if WHISPER_AVAILABLE:
                try:
                    self.whisper_engine = WhisperEngine()
                    services_initialized.append("WhisperEngine")
                except Exception as e:
                    services_failed.append(f"WhisperEngine: {e}")
                    self.whisper_engine = None
            else:
                self.whisper_engine = None
                services_failed.append("WhisperEngine: Module not available")
                
            # Initialize Translator
            if TRANSLATOR_AVAILABLE:
                try:
                    self.translator = Translator()
                    services_initialized.append("Translator")
                except Exception as e:
                    services_failed.append(f"Translator: {e}")
                    self.translator = None
            else:
                self.translator = None
                services_failed.append("Translator: Module not available")
                
            # Initialize Conversation Manager (Ollama)
            if OLLAMA_AVAILABLE:
                try:
                    self.conversation_manager = ConversationManager()
                    services_initialized.append("ConversationManager")
                except Exception as e:
                    services_failed.append(f"ConversationManager: {e}")
                    self.conversation_manager = None
            else:
                self.conversation_manager = None
                services_failed.append("ConversationManager: Module not available")
            
            # Log results
            if services_initialized:
                self.logger.info(f"Services initialized successfully: {', '.join(services_initialized)}")
            
            if services_failed:
                self.logger.warning(f"Services not available: {', '.join(services_failed)}")
                
            if not services_initialized:
                self.logger.warning("Running in demo mode - no backend services available")
                
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
        self.record_button.setStyleSheet(ChatTheme.get_button_style("stop"))
        
        self.status_label.setText("🎤 Grabando...")
        self.status_label.setStyleSheet(f"color: {ChatTheme.ACCENT_RED}; font-weight: bold; font-size: 14px;")
        
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
        self.status_label.setStyleSheet(f"color: {ChatTheme.ACCENT_ORANGE}; font-weight: bold; font-size: 14px;")
        
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
                try:
                    # Create conversation only if it doesn't exist
                    if not self.conversation_id:
                        self.conversation_id = self.conversation_manager.create_conversation(
                            "Chat Session", 
                            "llama3.2:latest"  # Default model
                        )
                    
                    message_id = self.conversation_manager.send_message(self.conversation_id, translation)
                    
                    if message_id:
                        # Get the actual message content
                        messages = self.conversation_manager.get_conversation_messages(self.conversation_id)
                        # Find the assistant message by ID
                        response = "Respuesta generada correctamente"
                        for msg in reversed(messages):
                            if msg.role == 'assistant' and msg.id == message_id:
                                response = msg.content
                                break
                    else:
                        response = f"Respuesta demo para: '{translation}'"
                except Exception as e:
                    # Fallback for demo
                    self.logger.error(f"Error generating AI response: {e}")
                    response = f"Respuesta demo para: '{translation}'"
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
            self.status_label.setStyleSheet(f"color: {ChatTheme.ACCENT_GREEN}; font-weight: bold; font-size: 14px;")
            
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
        
        # Reset conversation
        self.conversation_id = None
    
    def reset_record_button(self):
        """Resetea el botón de grabación al estado inicial."""
        self.record_button.setText("🎤 Iniciar Grabación")
        self.record_button.setStyleSheet(ChatTheme.get_button_style("recording"))
    
    def show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.status_label.setText(f"❌ Error: {message}")
        self.status_label.setStyleSheet(f"color: {ChatTheme.ACCENT_RED}; font-weight: bold; font-size: 14px;")
        self.error_occurred.emit(message)
        
        # Resetear estado después de unos segundos
        QTimer.singleShot(5000, lambda: (
            self.status_label.setText("✅ Listo para grabar"),
            self.status_label.setStyleSheet(f"color: {ChatTheme.ACCENT_GREEN}; font-weight: bold; font-size: 14px;")
        ))
