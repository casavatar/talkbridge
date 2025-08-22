#!/usr/bin/env python3
"""
TalkBridge Desktop - Settings Tab
=================================

Pestaña de configuración para TTS, traducción y animación.

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSlider, QGroupBox, QCheckBox, QSpinBox,
    QLineEdit, QTextEdit, QTabWidget, QFileDialog,
    QMessageBox, QFrame, QScrollArea
)
from PySide6.QtCore import Signal, QSettings, Qt
from PySide6.QtGui import QFont, QIcon

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class SettingsTab(QWidget):
    """
    Pestaña de configuración del sistema.
    
    Características:
    - Configuración de TTS (Text-to-Speech)
    - Configuración de traducción
    - Configuración de animación
    - Configuración de audio
    - Configuración general
    """
    
    # Señales
    settings_changed = Signal(str, object)  # setting_name, value
    settings_saved = Signal()
    error_occurred = Signal(str)  # error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("talkbridge.desktop.settings")
        
        # Settings
        self.settings = QSettings()
        self.config = {}
        
        # UI Components
        self.tabs = None
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title_label = QLabel("⚙️ Configuración del Sistema")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Pestañas de configuración
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_tts_tab(), "🔊 TTS")
        self.tabs.addTab(self.create_translation_tab(), "🌐 Traducción")
        self.tabs.addTab(self.create_animation_tab(), "🎭 Animación")
        self.tabs.addTab(self.create_audio_tab(), "🎤 Audio")
        self.tabs.addTab(self.create_general_tab(), "🔧 General")
        
        layout.addWidget(self.tabs)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Guardar Configuración")
        self.save_button.setMinimumHeight(40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("🔄 Restaurar Valores")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.reset_button.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_button)
        
        self.export_button = QPushButton("📤 Exportar Config")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.export_button.clicked.connect(self.export_settings)
        buttons_layout.addWidget(self.export_button)
        
        layout.addLayout(buttons_layout)
        
    def create_tts_tab(self):
        """Crea la pestaña de configuración de TTS."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Motor TTS
        engine_group = QGroupBox("🔊 Motor de Síntesis de Voz")
        engine_layout = QVBoxLayout(engine_group)
        
        # Selección de motor
        engine_selection_layout = QHBoxLayout()
        engine_selection_layout.addWidget(QLabel("Motor TTS:"))
        self.tts_engine_combo = QComboBox()
        self.tts_engine_combo.addItems([
            "TTS Coqui (Local)",
            "OpenAI TTS (API)",
            "Azure Speech (API)",
            "Google TTS (API)",
            "Sistema (SAPI)"
        ])
        engine_selection_layout.addWidget(self.tts_engine_combo)
        engine_selection_layout.addStretch()
        engine_layout.addLayout(engine_selection_layout)
        
        # Modelo TTS
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Modelo:"))
        self.tts_model_combo = QComboBox()
        self.tts_model_combo.addItems([
            "tts_models/multilingual/multi-dataset/xtts_v2",
            "tts_models/es/css10/vits",
            "tts_models/en/ljspeech/tacotron2-DDC"
        ])
        model_layout.addWidget(self.tts_model_combo)
        model_layout.addStretch()
        engine_layout.addLayout(model_layout)
        
        layout.addWidget(engine_group)
        
        # Configuración de voz
        voice_group = QGroupBox("🎤 Configuración de Voz")
        voice_layout = QVBoxLayout(voice_group)
        
        # Idioma
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Idioma:"))
        self.tts_language_combo = QComboBox()
        self.tts_language_combo.addItems([
            "Español (es)", "English (en)", "Français (fr)",
            "Deutsch (de)", "Italiano (it)", "Português (pt)"
        ])
        lang_layout.addWidget(self.tts_language_combo)
        lang_layout.addStretch()
        voice_layout.addLayout(lang_layout)
        
        # Velocidad
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Velocidad:"))
        self.tts_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.tts_speed_slider.setRange(50, 200)
        self.tts_speed_slider.setValue(100)
        self.tts_speed_slider.valueChanged.connect(self.on_tts_speed_changed)
        speed_layout.addWidget(self.tts_speed_slider)
        self.tts_speed_label = QLabel("100%")
        speed_layout.addWidget(self.tts_speed_label)
        voice_layout.addLayout(speed_layout)
        
        # Tono
        pitch_layout = QHBoxLayout()
        pitch_layout.addWidget(QLabel("Tono:"))
        self.tts_pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.tts_pitch_slider.setRange(-50, 50)
        self.tts_pitch_slider.setValue(0)
        self.tts_pitch_slider.valueChanged.connect(self.on_tts_pitch_changed)
        pitch_layout.addWidget(self.tts_pitch_slider)
        self.tts_pitch_label = QLabel("0")
        pitch_layout.addWidget(self.tts_pitch_label)
        voice_layout.addLayout(pitch_layout)
        
        # Volumen
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volumen:"))
        self.tts_volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.tts_volume_slider.setRange(0, 100)
        self.tts_volume_slider.setValue(80)
        self.tts_volume_slider.valueChanged.connect(self.on_tts_volume_changed)
        volume_layout.addWidget(self.tts_volume_slider)
        self.tts_volume_label = QLabel("80%")
        volume_layout.addWidget(self.tts_volume_label)
        voice_layout.addLayout(volume_layout)
        
        layout.addWidget(voice_group)
        
        # Clonación de voz
        clone_group = QGroupBox("👥 Clonación de Voz")
        clone_layout = QVBoxLayout(clone_group)
        
        self.enable_voice_cloning = QCheckBox("Activar clonación de voz")
        clone_layout.addWidget(self.enable_voice_cloning)
        
        # Archivo de referencia
        ref_layout = QHBoxLayout()
        ref_layout.addWidget(QLabel("Archivo de referencia:"))
        self.voice_ref_edit = QLineEdit()
        self.voice_ref_edit.setPlaceholderText("Selecciona un archivo de audio...")
        ref_layout.addWidget(self.voice_ref_edit)
        
        self.browse_voice_button = QPushButton("📁 Buscar")
        self.browse_voice_button.clicked.connect(self.browse_voice_reference)
        ref_layout.addWidget(self.browse_voice_button)
        clone_layout.addLayout(ref_layout)
        
        layout.addWidget(clone_group)
        
        layout.addStretch()
        return widget
        
    def create_translation_tab(self):
        """Crea la pestaña de configuración de traducción."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Motor de traducción
        engine_group = QGroupBox("🌐 Motor de Traducción")
        engine_layout = QVBoxLayout(engine_group)
        
        # Selección de servicio
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("Servicio:"))
        self.translation_service_combo = QComboBox()
        self.translation_service_combo.addItems([
            "Offline (Argos Translate)",
            "Google Translate (API)",
            "Azure Translator (API)",
            "DeepL (API)",
            "OpenAI (GPT)"
        ])
        service_layout.addWidget(self.translation_service_combo)
        service_layout.addStretch()
        engine_layout.addLayout(service_layout)
        
        layout.addWidget(engine_group)
        
        # Configuración de idiomas
        languages_group = QGroupBox("🗣️ Configuración de Idiomas")
        languages_layout = QVBoxLayout(languages_group)
        
        # Idioma fuente por defecto
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Idioma fuente por defecto:"))
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItems([
            "Auto-detectar", "Español", "English", "Français",
            "Deutsch", "Italiano", "Português", "中文", "日本語"
        ])
        source_layout.addWidget(self.source_lang_combo)
        source_layout.addStretch()
        languages_layout.addLayout(source_layout)
        
        # Idioma destino por defecto
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Idioma destino por defecto:"))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems([
            "Español", "English", "Français", "Deutsch",
            "Italiano", "Português", "中文", "日本語"
        ])
        target_layout.addWidget(self.target_lang_combo)
        target_layout.addStretch()
        languages_layout.addLayout(target_layout)
        
        # Traducción automática
        self.auto_translate_checkbox = QCheckBox("Traducir automáticamente al recibir audio")
        languages_layout.addWidget(self.auto_translate_checkbox)
        
        # Conservar texto original
        self.keep_original_checkbox = QCheckBox("Conservar texto original junto a la traducción")
        self.keep_original_checkbox.setChecked(True)
        languages_layout.addWidget(self.keep_original_checkbox)
        
        layout.addWidget(languages_group)
        
        # API Keys
        api_group = QGroupBox("🔑 Claves de API")
        api_layout = QVBoxLayout(api_group)
        
        # Google Translate API
        google_layout = QHBoxLayout()
        google_layout.addWidget(QLabel("Google Translate:"))
        self.google_api_edit = QLineEdit()
        self.google_api_edit.setPlaceholderText("Ingresa tu API key de Google Translate...")
        self.google_api_edit.setEchoMode(QLineEdit.EchoMode.Password)
        google_layout.addWidget(self.google_api_edit)
        api_layout.addLayout(google_layout)
        
        # Azure API
        azure_layout = QHBoxLayout()
        azure_layout.addWidget(QLabel("Azure Translator:"))
        self.azure_api_edit = QLineEdit()
        self.azure_api_edit.setPlaceholderText("Ingresa tu API key de Azure...")
        self.azure_api_edit.setEchoMode(QLineEdit.EchoMode.Password)
        azure_layout.addWidget(self.azure_api_edit)
        api_layout.addLayout(azure_layout)
        
        # DeepL API
        deepl_layout = QHBoxLayout()
        deepl_layout.addWidget(QLabel("DeepL:"))
        self.deepl_api_edit = QLineEdit()
        self.deepl_api_edit.setPlaceholderText("Ingresa tu API key de DeepL...")
        self.deepl_api_edit.setEchoMode(QLineEdit.EchoMode.Password)
        deepl_layout.addWidget(self.deepl_api_edit)
        api_layout.addLayout(deepl_layout)
        
        layout.addWidget(api_group)
        
        layout.addStretch()
        return widget
        
    def create_animation_tab(self):
        """Crea la pestaña de configuración de animación."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuración de detección facial
        detection_group = QGroupBox("👤 Detección Facial")
        detection_layout = QVBoxLayout(detection_group)
        
        # Modelo de detección
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Modelo:"))
        self.face_model_combo = QComboBox()
        self.face_model_combo.addItems([
            "MediaPipe Face Mesh",
            "OpenCV Haar Cascades",
            "Dlib Face Landmarks"
        ])
        model_layout.addWidget(self.face_model_combo)
        model_layout.addStretch()
        detection_layout.addLayout(model_layout)
        
        # Confianza mínima
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Confianza mínima:"))
        self.face_confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.face_confidence_slider.setRange(10, 95)
        self.face_confidence_slider.setValue(50)
        self.face_confidence_slider.valueChanged.connect(self.on_face_confidence_changed)
        confidence_layout.addWidget(self.face_confidence_slider)
        self.face_confidence_label = QLabel("50%")
        confidence_layout.addWidget(self.face_confidence_label)
        detection_layout.addLayout(confidence_layout)
        
        layout.addWidget(detection_group)
        
        # Configuración de sincronización labial
        lipsync_group = QGroupBox("👄 Sincronización Labial")
        lipsync_layout = QVBoxLayout(lipsync_group)
        
        # Sensibilidad
        sensitivity_layout = QHBoxLayout()
        sensitivity_layout.addWidget(QLabel("Sensibilidad:"))
        self.lipsync_sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.lipsync_sensitivity_slider.setRange(1, 10)
        self.lipsync_sensitivity_slider.setValue(5)
        self.lipsync_sensitivity_slider.valueChanged.connect(self.on_lipsync_sensitivity_changed)
        sensitivity_layout.addWidget(self.lipsync_sensitivity_slider)
        self.lipsync_sensitivity_label = QLabel("5")
        sensitivity_layout.addWidget(self.lipsync_sensitivity_label)
        lipsync_layout.addLayout(sensitivity_layout)
        
        # Suavizado temporal
        smoothing_layout = QHBoxLayout()
        smoothing_layout.addWidget(QLabel("Suavizado:"))
        self.lipsync_smoothing_slider = QSlider(Qt.Orientation.Horizontal)
        self.lipsync_smoothing_slider.setRange(0, 10)
        self.lipsync_smoothing_slider.setValue(3)
        self.lipsync_smoothing_slider.valueChanged.connect(self.on_lipsync_smoothing_changed)
        smoothing_layout.addWidget(self.lipsync_smoothing_slider)
        self.lipsync_smoothing_label = QLabel("3")
        smoothing_layout.addWidget(self.lipsync_smoothing_label)
        lipsync_layout.addLayout(smoothing_layout)
        
        layout.addWidget(lipsync_group)
        
        # Efectos visuales
        effects_group = QGroupBox("✨ Efectos Visuales")
        effects_layout = QVBoxLayout(effects_group)
        
        self.show_landmarks_checkbox = QCheckBox("Mostrar puntos faciales")
        effects_layout.addWidget(self.show_landmarks_checkbox)
        
        self.show_mesh_checkbox = QCheckBox("Mostrar malla facial")
        effects_layout.addWidget(self.show_mesh_checkbox)
        
        self.show_eye_tracking_checkbox = QCheckBox("Mostrar seguimiento ocular")
        effects_layout.addWidget(self.show_eye_tracking_checkbox)
        
        layout.addWidget(effects_group)
        
        layout.addStretch()
        return widget
        
    def create_audio_tab(self):
        """Crea la pestaña de configuración de audio."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Dispositivos de audio
        devices_group = QGroupBox("🎤 Dispositivos de Audio")
        devices_layout = QVBoxLayout(devices_group)
        
        # Micrófono
        mic_layout = QHBoxLayout()
        mic_layout.addWidget(QLabel("Micrófono:"))
        self.microphone_combo = QComboBox()
        self.microphone_combo.addItems(["Dispositivo por defecto", "Micrófono interno", "USB Mic"])
        mic_layout.addWidget(self.microphone_combo)
        
        self.refresh_devices_button = QPushButton("🔄 Actualizar")
        self.refresh_devices_button.clicked.connect(self.refresh_audio_devices)
        mic_layout.addWidget(self.refresh_devices_button)
        devices_layout.addLayout(mic_layout)
        
        # Altavoces
        speaker_layout = QHBoxLayout()
        speaker_layout.addWidget(QLabel("Altavoces:"))
        self.speaker_combo = QComboBox()
        self.speaker_combo.addItems(["Dispositivo por defecto", "Altavoces internos", "Auriculares"])
        speaker_layout.addWidget(self.speaker_combo)
        speaker_layout.addStretch()
        devices_layout.addLayout(speaker_layout)
        
        layout.addWidget(devices_group)
        
        # Configuración de grabación
        recording_group = QGroupBox("⏺️ Configuración de Grabación")
        recording_layout = QVBoxLayout(recording_group)
        
        # Calidad de audio
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Calidad:"))
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems([
            "Baja (8 kHz)", "Media (16 kHz)", "Alta (44.1 kHz)", "Muy Alta (48 kHz)"
        ])
        self.audio_quality_combo.setCurrentText("Media (16 kHz)")
        quality_layout.addWidget(self.audio_quality_combo)
        quality_layout.addStretch()
        recording_layout.addLayout(quality_layout)
        
        # Duración máxima
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duración máxima:"))
        self.max_duration_spin = QSpinBox()
        self.max_duration_spin.setRange(1, 60)
        self.max_duration_spin.setValue(30)
        self.max_duration_spin.setSuffix(" segundos")
        duration_layout.addWidget(self.max_duration_spin)
        duration_layout.addStretch()
        recording_layout.addLayout(duration_layout)
        
        # Detección de silencio
        self.silence_detection_checkbox = QCheckBox("Detección automática de silencio")
        self.silence_detection_checkbox.setChecked(True)
        recording_layout.addWidget(self.silence_detection_checkbox)
        
        # Reducción de ruido
        self.noise_reduction_checkbox = QCheckBox("Reducción de ruido")
        self.noise_reduction_checkbox.setChecked(True)
        recording_layout.addWidget(self.noise_reduction_checkbox)
        
        layout.addWidget(recording_group)
        
        # Test de audio
        test_group = QGroupBox("🧪 Pruebas de Audio")
        test_layout = QVBoxLayout(test_group)
        
        test_buttons_layout = QHBoxLayout()
        
        self.test_mic_button = QPushButton("🎤 Probar Micrófono")
        self.test_mic_button.clicked.connect(self.test_microphone)
        test_buttons_layout.addWidget(self.test_mic_button)
        
        self.test_speakers_button = QPushButton("🔊 Probar Altavoces")
        self.test_speakers_button.clicked.connect(self.test_speakers)
        test_buttons_layout.addWidget(self.test_speakers_button)
        
        test_layout.addLayout(test_buttons_layout)
        
        layout.addWidget(test_group)
        
        layout.addStretch()
        return widget
        
    def create_general_tab(self):
        """Crea la pestaña de configuración general."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuración de la aplicación
        app_group = QGroupBox("📱 Configuración de Aplicación")
        app_layout = QVBoxLayout(app_group)
        
        # Idioma de la interfaz
        ui_lang_layout = QHBoxLayout()
        ui_lang_layout.addWidget(QLabel("Idioma de interfaz:"))
        self.ui_language_combo = QComboBox()
        self.ui_language_combo.addItems(["Español", "English", "Français", "Deutsch"])
        ui_lang_layout.addWidget(self.ui_language_combo)
        ui_lang_layout.addStretch()
        app_layout.addLayout(ui_lang_layout)
        
        # Tema
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Claro", "Oscuro", "Automático"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        app_layout.addLayout(theme_layout)
        
        # Iniciar con Windows
        self.startup_checkbox = QCheckBox("Iniciar con Windows")
        app_layout.addWidget(self.startup_checkbox)
        
        # Minimizar a bandeja
        self.minimize_to_tray_checkbox = QCheckBox("Minimizar a bandeja del sistema")
        app_layout.addWidget(self.minimize_to_tray_checkbox)
        
        layout.addWidget(app_group)
        
        # Configuración de logging
        logging_group = QGroupBox("📝 Configuración de Logs")
        logging_layout = QVBoxLayout(logging_group)
        
        # Nivel de log
        log_level_layout = QHBoxLayout()
        log_level_layout.addWidget(QLabel("Nivel de log:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        log_level_layout.addWidget(self.log_level_combo)
        log_level_layout.addStretch()
        logging_layout.addLayout(log_level_layout)
        
        # Guardar logs
        self.save_logs_checkbox = QCheckBox("Guardar logs en archivo")
        self.save_logs_checkbox.setChecked(True)
        logging_layout.addWidget(self.save_logs_checkbox)
        
        # Ruta de logs
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(QLabel("Carpeta de logs:"))
        self.log_path_edit = QLineEdit()
        self.log_path_edit.setText("./data/logs")
        log_path_layout.addWidget(self.log_path_edit)
        
        self.browse_log_button = QPushButton("📁 Buscar")
        self.browse_log_button.clicked.connect(self.browse_log_path)
        log_path_layout.addWidget(self.browse_log_button)
        logging_layout.addLayout(log_path_layout)
        
        layout.addWidget(logging_group)
        
        # Información del sistema
        info_group = QGroupBox("ℹ️ Información del Sistema")
        info_layout = QVBoxLayout(info_group)
        
        self.system_info_text = QTextEdit()
        self.system_info_text.setMaximumHeight(100)
        self.system_info_text.setReadOnly(True)
        self.system_info_text.setText(self.get_system_info())
        info_layout.addWidget(self.system_info_text)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        return widget
    
    # Métodos de callback para sliders
    def on_tts_speed_changed(self, value):
        self.tts_speed_label.setText(f"{value}%")
        
    def on_tts_pitch_changed(self, value):
        self.tts_pitch_label.setText(str(value))
        
    def on_tts_volume_changed(self, value):
        self.tts_volume_label.setText(f"{value}%")
        
    def on_face_confidence_changed(self, value):
        self.face_confidence_label.setText(f"{value}%")
        
    def on_lipsync_sensitivity_changed(self, value):
        self.lipsync_sensitivity_label.setText(str(value))
        
    def on_lipsync_smoothing_changed(self, value):
        self.lipsync_smoothing_label.setText(str(value))
    
    # Métodos de utilidad
    def browse_voice_reference(self):
        """Busca archivo de referencia de voz."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de audio", "",
            "Audio Files (*.wav *.mp3 *.ogg *.flac);;All Files (*)"
        )
        if file_path:
            self.voice_ref_edit.setText(file_path)
    
    def browse_log_path(self):
        """Busca carpeta de logs."""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de logs"
        )
        if folder_path:
            self.log_path_edit.setText(folder_path)
    
    def refresh_audio_devices(self):
        """Actualiza la lista de dispositivos de audio."""
        # Aquí implementarías la lógica para detectar dispositivos
        QMessageBox.information(self, "Dispositivos", "Lista de dispositivos actualizada")
    
    def test_microphone(self):
        """Prueba el micrófono."""
        QMessageBox.information(self, "Test Micrófono", "Probando micrófono... (no implementado)")
    
    def test_speakers(self):
        """Prueba los altavoces."""
        QMessageBox.information(self, "Test Altavoces", "Probando altavoces... (no implementado)")
    
    def get_system_info(self):
        """Obtiene información del sistema."""
        import platform
        try:
            import PySide6.QtCore
            qt_version = PySide6.QtCore.__version__
            qt_name = "PySide6"
        except ImportError:
            try:
                # Fallback to PyQt6 (though we prefer PySide6)
                import PyQt6.QtCore
                qt_version = PyQt6.QtCore.PYQT_VERSION_STR
                qt_name = "PyQt6"
            except ImportError:
                qt_version = "No disponible"
                qt_name = "Qt"
        
        info = f"Sistema: {platform.system()} {platform.release()}\n"
        info += f"Python: {platform.python_version()}\n"
        info += f"{qt_name}: {qt_version}\n"
        info += f"TalkBridge: 1.0.0"
        
        return info
    
    def load_settings(self):
        """Carga la configuración guardada."""
        try:
            # Cargar desde QSettings
            if CONFIG_AVAILABLE:
                self.config = get_config()
            
            # Aplicar configuración a los controles
            # TTS
            if self.settings.value("tts/engine"):
                index = self.tts_engine_combo.findText(self.settings.value("tts/engine"))
                if index >= 0:
                    self.tts_engine_combo.setCurrentIndex(index)
            
            # Más configuraciones...
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Guarda la configuración actual."""
        try:
            # Guardar en QSettings
            self.settings.setValue("tts/engine", self.tts_engine_combo.currentText())
            self.settings.setValue("tts/speed", self.tts_speed_slider.value())
            self.settings.setValue("tts/pitch", self.tts_pitch_slider.value())
            self.settings.setValue("tts/volume", self.tts_volume_slider.value())
            
            # Más configuraciones...
            
            self.settings.sync()
            self.settings_saved.emit()
            
            QMessageBox.information(self, "Configuración", "Configuración guardada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            self.error_occurred.emit(f"Error al guardar configuración: {e}")
    
    def reset_settings(self):
        """Restaura la configuración por defecto."""
        reply = QMessageBox.question(
            self, "Restaurar Configuración",
            "¿Estás seguro de que quieres restaurar todos los valores por defecto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Restaurar valores por defecto
            self.tts_speed_slider.setValue(100)
            self.tts_pitch_slider.setValue(0)
            self.tts_volume_slider.setValue(80)
            # Más restauraciones...
            
            QMessageBox.information(self, "Configuración", "Valores restaurados")
    
    def export_settings(self):
        """Exporta la configuración a un archivo."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar configuración", "talkbridge_config.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                config_data = {
                    "tts": {
                        "engine": self.tts_engine_combo.currentText(),
                        "speed": self.tts_speed_slider.value(),
                        "pitch": self.tts_pitch_slider.value(),
                        "volume": self.tts_volume_slider.value()
                    }
                    # Más configuraciones...
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "Exportar", "Configuración exportada exitosamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar configuración: {e}")
