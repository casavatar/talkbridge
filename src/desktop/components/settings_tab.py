#!/usr/bin/env python3
"""
TalkBridge Desktop - Settings Tab Component
===========================================

Settings management interface for TTS, translation, animation, and system configuration.
Provides comprehensive configuration options with validation and persistence.

Author: TalkBridge Team  
Date: 2025-09-18
Version: 1.0
"""

# Standard library imports
import json
import logging
import os
import tkinter as tk
from pathlib import Path
from typing import Dict, Any, Optional, List

# Third-party imports
import customtkinter as ctk

# Local imports - Core utilities
from ...logging_config import get_logger, log_exception

# Local imports - Theme system (centralized)
from ..ui.theme import (
    ColorPalette,
    Typography,
    Dimensions, 
    Spacing,
    ComponentThemes
)

# Local imports - Configuration
try:
    from ...config import get_config
except ImportError:
    get_config = None

# Local imports - Status utilities
try:
    from ...utils.status_utils import update_status  
except ImportError:
    update_status = None

# Constants - Use centralized theme directly
TAB_HEIGHT = 300

# Theme availability check
THEME_AVAILABLE = True

# Config availability check  
CONFIG_AVAILABLE = get_config is not None

# Convenience functions for cleaner code
def clean_text(text: str) -> str:
    """Clean text for display (placeholder for localization)."""
    return text

# Legacy constants for backward compatibility (use centralized theme values)
LABEL_FONT_SIZE = Typography.FONT_SIZE_BODY
SECTION_FONT_SIZE = Typography.FONT_SIZE_H3
BUTTON_HEIGHT = Dimensions.HEIGHT_BUTTON
ITEM_SPACING = Spacing.MD
SECTION_SPACING = Spacing.LG

class SettingsTab:
    """
    Settings management interface for comprehensive system configuration.
    
    Provides centralized configuration management for TTS, translation, animation,
    audio, and application settings with validation and persistence capabilities.
    
    Features:
    - Comprehensive TTS (Text-to-Speech) settings
    - Advanced translation configuration 
    - Animation and visual effects settings
    - Audio input/output configuration
    - Application preferences and theming
    - Import/export configuration support
    - Real-time settings validation
    - Centralized theme integration
    """

    def __init__(self, parent: ctk.CTkFrame, state_manager: Optional[Any] = None, core_bridge: Optional[Any] = None) -> None:
        """Initialize the settings tab component.
        
        Args:
            parent: Parent frame to contain this settings interface
            state_manager: Optional state management instance
            core_bridge: Optional core bridge for system integration
        """
        self.parent = parent
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        self.logger = get_logger(__name__)
        
        # Configuration
        self.config = {}
        self.settings_file = Path.home() / ".talkbridge" / "settings.json"
        
        # UI Components (will be initialized in setup_ui)
        self.main_frame = None
        self.title_label = None
        self.tabview = None
        
        # TTS Settings
        self.tts_engine_var = None
        self.tts_engine_combo = None
        self.tts_api_var = None
        self.tts_api_entry = None
        self.tts_api_frame = None
        self.tts_api_label = None
        self.tts_model_var = None
        self.tts_voice_var = None
        self.tts_speed_var = None
        self.tts_pitch_var = None
        self.tts_volume_var = None
        
        # Translation Settings
        self.translation_service_var = None
        self.translation_service_combo = None
        self.translation_api_var = None
        self.translation_api_entry = None
        self.translation_api_frame = None
        self.translation_api_label = None
        self.translation_local_model_var = None
        self.translation_local_model_combo = None
        self.translation_local_model_frame = None
        self.source_lang_var = None
        self.target_lang_var = None
        self.auto_detect_var = None
        self.translation_quality_var = None
        
        # Animation Settings
        self.enable_animations_var = None
        self.animation_speed_var = None
        self.face_tracking_var = None
        self.avatar_style_var = None
        self.background_effects_var = None
        
        # Audio Settings
        self.input_device_var = None
        self.output_device_var = None
        self.input_volume_var = None
        self.output_volume_var = None
        self.noise_cancellation_var = None
        self.echo_cancellation_var = None
        
        # General Settings
        self.theme_var = None
        self.language_var = None
        self.auto_save_var = None
        self.notifications_var = None
        self.startup_var = None
        
        # Action buttons
        self.save_button = None
        self.reset_button = None
        self.export_button = None
        self.import_button = None

        # Data-driven settings definition
        self._settings_definition = {
            "tts_engine": {"var": self.tts_engine_var, "default": "System (SAPI)"},
            "tts_api_key": {"var": self.tts_api_var, "default": ""},
            "tts_model": {"var": self.tts_model_var, "default": "tts_models/en/ljspeech/tacotron2-DDC"},
            "tts_voice": {"var": self.tts_voice_var, "default": "Female (Default)"},
            "tts_speed": {"var": self.tts_speed_var, "default": 1.0},
            "tts_pitch": {"var": self.tts_pitch_var, "default": 1.0},
            "tts_volume": {"var": self.tts_volume_var, "default": 0.8},
            "translation_service": {"var": self.translation_service_var, "default": "Google Translate"},
            "translation_api_key": {"var": self.translation_api_var, "default": ""},
            "translation_local_model": {"var": self.translation_local_model_var, "default": "llama3:8b"},
            "enable_animations": {"var": self.enable_animations_var, "default": True},
            "animation_speed": {"var": self.animation_speed_var, "default": 1.0},
            "theme": {"var": self.theme_var, "default": "Dark"},
        }
        
        # Load configuration and setup UI
        try:
            self._load_settings()
            self.setup_ui()
            self.logger.info("Settings tab initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing settings tab: {e}")
            log_exception(self.logger, e, "Settings tab initialization failed")
    
    @property
    def default_settings(self) -> Dict[str, Any]:
        """Default settings configuration."""
        return {
            "tts_engine": "System (SAPI)",
            "tts_api_key": "",
            "tts_model": "tts_models/en/ljspeech/tacotron2-DDC",
            "tts_voice": "Female (Default)",
            "tts_speed": 1.0,
            "tts_pitch": 1.0,
            "tts_volume": 0.8,
            "translation_service": "Google Translate",
            "translation_api_key": "",
            "translation_local_model": "llama3:8b",
            "source_language": "auto",
            "target_language": "en",
            "auto_detect_language": True,
            "translation_quality": "high",
            "enable_animations": True,
            "animation_speed": 1.0,
            "face_tracking": False,
            "avatar_style": "default",
            "background_effects": False,
            "input_device": "Default",
            "output_device": "Default",
            "input_volume": 0.8,
            "output_volume": 0.8,
            "noise_cancellation": True,
            "echo_cancellation": True,
            "theme": "Dark",
            "language": "en",
            "auto_save": True,
            "notifications": True,
            "startup_with_system": False
        }

    def setup_ui(self) -> None:
        """Set up the settings user interface with centralized theme."""
        try:
            # Main frame with themed background
            self.main_frame = ctk.CTkFrame(
                self.parent, 
                fg_color=ColorPalette.BACKGROUND_PRIMARY
            )
            self.main_frame.pack(
                fill="both", 
                expand=True, 
                padx=Spacing.MARGIN_MAIN, 
                pady=Spacing.MARGIN_MAIN
            )
            
            # Title section
            title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            title_frame.pack(fill="x", pady=(0, Spacing.LG))
            
            # Apply title theme from centralized system
            title_theme = ComponentThemes.get_label_theme("title")
            self.title_label = ctk.CTkLabel(
                title_frame,
                text="System Settings",
                **title_theme
            )
            self.title_label.pack(pady=Spacing.MD)
            
            # Settings tabview with centralized theme
            self.tabview = ctk.CTkTabview(
                self.main_frame,
                fg_color=ColorPalette.BACKGROUND_SECONDARY,
                segmented_button_fg_color=ColorPalette.BACKGROUND_ELEVATED,
                segmented_button_selected_color=ColorPalette.ACCENT_PRIMARY,
                segmented_button_selected_hover_color=ColorPalette.ACCENT_PRIMARY_HOVER,
                text_color=ColorPalette.TEXT_PRIMARY,
                height=TAB_HEIGHT
            )
            self.tabview.pack(fill="both", expand=True, pady=Spacing.LG)
            
            # Create tabs
            self._create_tts_tab()
            self._create_translation_tab()
            self._create_animation_tab()
            self._create_audio_tab()
            self._create_general_tab()
            
            # Action buttons section
            self._create_action_buttons()
            
            # Load current settings into UI
            self._update_ui_from_config()
            
            self.logger.info("Settings UI setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up settings UI: {e}")
            log_exception(self.logger, e, "Settings UI setup failed")

    def _create_section(self, parent: Any, title: str) -> ctk.CTkFrame:
        """Creates a themed section frame with a title."""
        section_frame = ctk.CTkFrame(parent, fg_color=ColorPalette.BACKGROUND_SECONDARY)
        section_frame.pack(fill="x", pady=Spacing.LG)
        
        subtitle_theme = ComponentThemes.get_label_theme("subtitle")
        ctk.CTkLabel(
            section_frame,
            text=title,
            **subtitle_theme
        ).pack(anchor="w", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        
        return section_frame

    def _enumerate_audio_devices(self) -> Dict[str, Any]:
        """
        Enumerate available audio input and output devices with real OS names.
        
        Returns:
            Dict containing input_devices, output_devices, and device mappings
        """
        try:
            # Import AudioCapture for device enumeration
            from src.audio.capture import AudioCapture
            
            # Create temporary AudioCapture instance to get device list
            audio_capture = AudioCapture()
            devices_info = audio_capture.list_devices()
            devices = devices_info.get('devices', [])
            
            input_devices = []
            output_devices = []
            input_device_mapping = {}  # name -> index
            output_device_mapping = {}  # name -> index
            
            # Always add "Default" option first
            input_devices.append("Default")
            output_devices.append("Default")
            
            # Get default device indices
            default_input_idx = devices_info.get('default_input')
            default_output_idx = devices_info.get('default_output')
            
            if default_input_idx is not None:
                input_device_mapping["Default"] = default_input_idx
            if default_output_idx is not None:
                output_device_mapping["Default"] = default_output_idx
            
            self.logger.debug(f"Enumerating {len(devices)} audio devices...")
            
            # Process each device
            for i, device in enumerate(devices):
                device_name = device.get('name', f'Device {i}')
                max_inputs = device.get('max_input_channels', 0)
                max_outputs = device.get('max_output_channels', 0)
                
                # Clean up device name (remove extra whitespace, etc.)
                clean_name = device_name.strip()
                
                # Add to input devices if it has input channels
                if max_inputs > 0:
                    input_devices.append(clean_name)
                    input_device_mapping[clean_name] = i
                    self.logger.debug(f"Input device {i}: {clean_name} ({max_inputs} channels)")
                
                # Add to output devices if it has output channels
                if max_outputs > 0:
                    output_devices.append(clean_name)
                    output_device_mapping[clean_name] = i
                    self.logger.debug(f"Output device {i}: {clean_name} ({max_outputs} channels)")
            
            self.logger.info(f"Found {len(input_devices)-1} input and {len(output_devices)-1} output devices")
            
            return {
                'input_devices': input_devices,
                'output_devices': output_devices,
                'input_device_mapping': input_device_mapping,
                'output_device_mapping': output_device_mapping,
                'default_input': default_input_idx,
                'default_output': default_output_idx
            }
            
        except Exception as e:
            self.logger.error(f"Failed to enumerate audio devices: {e}")
            # Fallback to basic device list
            return {
                'input_devices': ["Default", "Microphone (Built-in)", "USB Microphone", "Headset"],
                'output_devices': ["Default", "Speakers", "Headphones", "USB Headset"],
                'input_device_mapping': {"Default": None},
                'output_device_mapping': {"Default": None},
                'default_input': None,
                'default_output': None
            }

    def get_input_device_index(self, device_name: str) -> Optional[int]:
        """
        Get the device index for a given input device name.
        
        Args:
            device_name: The display name of the device
            
        Returns:
            Device index or None if not found
        """
        if hasattr(self, 'audio_devices_info'):
            return self.audio_devices_info['input_device_mapping'].get(device_name)
        return None
    
    def get_output_device_index(self, device_name: str) -> Optional[int]:
        """
        Get the device index for a given output device name.
        
        Args:
            device_name: The display name of the device
            
        Returns:
            Device index or None if not found
        """
        if hasattr(self, 'audio_devices_info'):
            return self.audio_devices_info['output_device_mapping'].get(device_name)
        return None
    
    def get_available_input_devices(self) -> List[str]:
        """Get list of available input device names."""
        if hasattr(self, 'audio_devices_info'):
            return self.audio_devices_info['input_devices']
        return ["Default"]
    
    def get_available_output_devices(self) -> List[str]:
        """Get list of available output device names."""
        if hasattr(self, 'audio_devices_info'):
            return self.audio_devices_info['output_devices']
        return ["Default"]

    def _create_tts_tab(self) -> None:
        """Create the TTS (Text-to-Speech) settings tab with centralized theme."""
        if not self.tabview:
            self.logger.error("Cannot create TTS tab: tabview is not initialized.")
            return
        try:
            tts_tab = self.tabview.add("🔊 TTS")  # type: ignore
            
            # Scrollable frame for TTS settings
            tts_scroll = ctk.CTkScrollableFrame(
                tts_tab,
                fg_color=ColorPalette.BACKGROUND_PRIMARY,
                scrollbar_button_color=ColorPalette.ACCENT_PRIMARY
            )
            tts_scroll.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
            
            engine_frame = self._create_section(tts_scroll, "🔊 Voice Synthesis Engine")
            
            # Engine selection
            engine_selection_frame = ctk.CTkFrame(engine_frame, fg_color="transparent")
            engine_selection_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
            combobox_theme = ComponentThemes.get_combobox_theme()
            self.tts_engine_combo = ctk.CTkComboBox(
                engine_selection_frame,
                values=[
                    "System (SAPI)",
                    "OpenAI TTS", 
                    "Eleven Labs",
                    "Local TTS"
                ],
                command=self._on_tts_engine_changed,
                **combobox_theme
            )
            self.tts_engine_combo.pack(side="right", padx=(Spacing.SM, 0))

            self.tts_engine_var = self._bind_variable(self.tts_engine_combo, "tts_engine", tk.StringVar)

            ctk.CTkLabel(engine_selection_frame, text="TTS Engine:", **ComponentThemes.get_label_theme()).pack(side="left")

            # API Key section (initially hidden)
            self.tts_api_frame = ctk.CTkFrame(engine_frame, fg_color="transparent")
            self.tts_api_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
            
            self.tts_api_label = ctk.CTkLabel(
            self.tts_api_frame,
            text=clean_text("API Key:"),
            **ComponentThemes.get_label_theme()
            )
            self.tts_api_label.pack(side="left")
            
            self.tts_api_var = tk.StringVar() # This will be bound in _save_settings
            self.tts_api_entry = ctk.CTkEntry(
            self.tts_api_frame,
            textvariable=self.tts_api_var,
            placeholder_text="Enter API Key",
            show="*",
            width=250,
            **ComponentThemes.get_input_theme()
            )
            self.tts_api_entry.pack(side="right", padx=(10, 0))
            
            # Hide API key section by default
            self.tts_api_frame.pack_forget()
            
            # TTS Model selection
            model_selection_frame = ctk.CTkFrame(engine_frame, fg_color="transparent")
            model_selection_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
            
            ctk.CTkLabel(
                model_selection_frame,
                text=clean_text("Voice Model:"),
                **ComponentThemes.get_label_theme()
            ).pack(side="left")
            
            self.tts_model_combo = ctk.CTkComboBox(
            model_selection_frame,
            values=[
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/ljspeech/glow-tts",
                "tts_models/es/mai/tacotron2-DDC",
                "tts_models/multilingual/multi-dataset/bark"
            ],
            **ComponentThemes.get_combobox_theme()
            )
            self.tts_model_combo.pack(side="right", padx=(10, 0))

            self.tts_model_var = self._bind_variable(self.tts_model_combo, "tts_model")
            
            # Voice selection
            voice_selection_frame = ctk.CTkFrame(engine_frame, fg_color="transparent")
            voice_selection_frame.pack(fill="x", padx=15, pady=(ITEM_SPACING, 15))
            
            label_theme = ComponentThemes.get_label_theme()
            ctk.CTkLabel(
                voice_selection_frame,
                text="Voice:",
                **label_theme
            ).pack(side="left")
            
            self.tts_voice_combo = ctk.CTkComboBox(
            voice_selection_frame,
            values=["Female (Default)", "Male (Alternative)", "Child", "Elderly"],
            **ComponentThemes.get_combobox_theme()
            )
            self.tts_voice_combo.pack(side="right", padx=(10, 0))

            self.tts_voice_var = self._bind_variable(self.tts_voice_combo, "tts_voice")
            
            params_frame = self._create_section(tts_scroll, "🎛️ Voice Parameters")
            
            # Speed control
            self._create_slider_control(
                params_frame,
                "Speed:",
                0.5, 2.0, 1.0,
                lambda var: setattr(self, 'tts_speed_var', var)
            )
            
            # Pitch control
            self._create_slider_control(
                params_frame,
                "Pitch:",
                0.5, 2.0, 1.0,
                lambda var: setattr(self, 'tts_pitch_var', var)
            )
            
            # Volume control
            self._create_slider_control(
                params_frame,
                "Volume:",
                0.0, 1.0, 0.8,
                lambda var: setattr(self, 'tts_volume_var', var)
            )
                
        except Exception as e:
            self.logger.error(f"Error creating TTS tab: {e}")
            log_exception(self.logger, e, "TTS tab creation failed")

    def _create_translation_tab(self) -> None:
        """Create the translation settings tab with centralized theme."""
        if not self.tabview:
            self.logger.error("Cannot create Translation tab: tabview is not initialized.")
            return
        try:
            trans_tab = self.tabview.add("🌐 Translation")  # type: ignore
            
            # Scrollable frame with centralized theme
            trans_scroll = ctk.CTkScrollableFrame(
                trans_tab,
                fg_color=ColorPalette.BACKGROUND_PRIMARY,
                scrollbar_button_color=ColorPalette.ACCENT_PRIMARY
            )
            trans_scroll.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
            
            service_frame = self._create_section(trans_scroll, "🌐 Translation Service")
            
            # Service selection
            service_selection_frame = ctk.CTkFrame(service_frame, fg_color="transparent")
            service_selection_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

            combobox_theme = ComponentThemes.get_combobox_theme()
            self.translation_service_combo = ctk.CTkComboBox(
                service_selection_frame,
                values=[
                    "Google Translate",
                    "Microsoft Translator", 
                    "DeepL",
                    "Local Model"
                ],
                command=self._on_translation_service_changed,
                **combobox_theme
            )
            self.translation_service_combo.pack(side="right", padx=(Spacing.SM, 0))

            self.translation_service_var = self._bind_variable(self.translation_service_combo, "translation_service", tk.StringVar)
            
            ctk.CTkLabel(service_selection_frame, text="Translation Service:", **ComponentThemes.get_label_theme()).pack(side="left")

            # API Key section (initially hidden)
            self.translation_api_frame = ctk.CTkFrame(service_frame, fg_color="transparent")
            self.translation_api_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
            
            self.translation_api_label = ctk.CTkLabel(
                self.translation_api_frame,
                text=clean_text("API Key:"),
                **ComponentThemes.get_label_theme()
            )
            self.translation_api_label.pack(side="left")
            
            self.translation_api_var = tk.StringVar() # Bound in _save_settings
            self.translation_api_entry = ctk.CTkEntry(
                self.translation_api_frame,
                textvariable=self.translation_api_var,
                placeholder_text="Enter API Key",
                show="*",
                width=250,
                **ComponentThemes.get_input_theme()
            )
            self.translation_api_entry.pack(side="right", padx=(10, 0))
            
            # Local Model selection (initially hidden)
            self.translation_local_model_frame = ctk.CTkFrame(service_frame, fg_color="transparent")
            self.translation_local_model_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
            
            ctk.CTkLabel(
                self.translation_local_model_frame,
                text=clean_text("Local Model:"),
                **ComponentThemes.get_label_theme()
            ).pack(side="left")
            
            self.translation_local_model_combo = ctk.CTkComboBox(
                self.translation_local_model_frame,
                values=[
                    "llama3:8b",
                    "mistral:7b",
                    "gemma2:2b",
                    "codellama:7b"
                ],
                **ComponentThemes.get_combobox_theme()
            )
            self.translation_local_model_combo.pack(side="right", padx=(10, 0))

            self.translation_local_model_var = self._bind_variable(self.translation_local_model_combo, "translation_local_model")
            
            # Hide API key and local model sections by default
            self.translation_api_frame.pack_forget()
            self.translation_local_model_frame.pack_forget()
                
        except Exception as e:
            self.logger.error(f"Error creating translation tab: {e}")
            log_exception(self.logger, e, "Translation tab creation failed")

    def _create_animation_tab(self) -> None:
        """Create the animation settings tab with centralized theme."""
        if not self.tabview:
            self.logger.error("Cannot create Animation tab: tabview is not initialized.")
            return
        try:
            anim_tab = self.tabview.add("Animation")  # type: ignore
            
            # Scrollable frame with centralized theme
            anim_scroll = ctk.CTkScrollableFrame(
                anim_tab,
                fg_color=ColorPalette.BACKGROUND_PRIMARY,
                scrollbar_button_color=ColorPalette.ACCENT_PRIMARY
            )
            anim_scroll.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
            
            controls_frame = self._create_section(anim_scroll, "🎨 Animation Controls")
            
            # Enable animations checkbox with centralized theme
            checkbox_theme = ComponentThemes.get_checkbox_theme()
            self.enable_animations_checkbox = ctk.CTkCheckBox(
                controls_frame,
                text="Enable Animations",
                **checkbox_theme
            )
            self.enable_animations_checkbox.pack(anchor="w", padx=Spacing.LG, pady=Spacing.MD)

            self.enable_animations_var = self._bind_variable(self.enable_animations_checkbox, "enable_animations", tk.BooleanVar)
            
            # Animation speed
            self._create_slider_control(
                controls_frame,
                "Animation Speed:",
                0.5, 3.0, 1.0,
                lambda var: setattr(self, 'animation_speed_var', var)
            )
                
        except Exception as e:
            self.logger.error(f"Error creating animation tab: {e}")
            log_exception(self.logger, e, "Animation tab creation failed")

    def _create_audio_tab(self) -> None:
        """Create the audio settings tab with centralized theme."""
        if not self.tabview:
            self.logger.error("Cannot create Audio tab: tabview is not initialized.")
            return
        
        audio_tab = None
        try:
            audio_tab = self.tabview.add("🎤 Audio")  # type: ignore
            
            # Scrollable frame with centralized theme
            audio_scroll = ctk.CTkScrollableFrame(
                audio_tab,
                fg_color=ColorPalette.BACKGROUND_PRIMARY,
                scrollbar_button_color=ColorPalette.ACCENT_PRIMARY
            )
            audio_scroll.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
            
            # Get real audio devices
            self.audio_devices_info = self._enumerate_audio_devices()
            
            # Device Configuration Section  
            device_frame = self._create_section(audio_scroll, "🎤 Audio Devices")
            
            # Input device section
            input_device_frame = ctk.CTkFrame(device_frame, fg_color="transparent")
            input_device_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

            combobox_theme = ComponentThemes.get_combobox_theme()
            self.input_device_combo = ctk.CTkComboBox(
                input_device_frame,
                values=self.audio_devices_info['input_devices'],
                **combobox_theme
            )
            self.input_device_combo.pack(side="right", padx=(Spacing.SM, 0))
            self.input_device_var = self._bind_variable(self.input_device_combo, "input_device")
            ctk.CTkLabel(input_device_frame, text="Input Device:", **ComponentThemes.get_label_theme()).pack(side="left")
            
            # Output device section
            output_device_frame = ctk.CTkFrame(device_frame, fg_color="transparent")
            output_device_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
            
            self.output_device_combo = ctk.CTkComboBox(
                output_device_frame,
                values=self.audio_devices_info['output_devices'],
                **combobox_theme
            )
            self.output_device_combo.pack(side="right", padx=(Spacing.SM, 0))
            self.output_device_var = self._bind_variable(self.output_device_combo, "output_device")
            ctk.CTkLabel(output_device_frame, text="Output Device:", **ComponentThemes.get_label_theme()).pack(side="left")

            # System Audio Capture Section
            system_audio_frame = self._create_section(audio_scroll, "🔊 System Audio Capture")
            
            # Enable system audio capture checkbox
            enable_loopback_frame = ctk.CTkFrame(system_audio_frame, fg_color="transparent")
            enable_loopback_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
            
            self.enable_system_audio_var = tk.BooleanVar(value=False)
            
            # Apply checkbox theme from centralized system
            checkbox_theme = ComponentThemes.get_checkbox_theme()
            self.enable_system_audio_checkbox = ctk.CTkCheckBox(
                enable_loopback_frame,
                text="Capture from system audio output",
                variable=self.enable_system_audio_var,
                command=self._on_system_audio_toggle,
                **checkbox_theme
            )
            self.enable_system_audio_checkbox.pack(anchor="w")
            
            # System audio device selection
            system_device_frame = ctk.CTkFrame(system_audio_frame, fg_color="transparent")
            system_device_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
            
            ctk.CTkLabel(system_device_frame, text="Output Device:", **ComponentThemes.get_label_theme()).pack(side="left")
            
            self.system_audio_device_var = tk.StringVar(value="Auto-detect")
            self.system_audio_device_combo = ctk.CTkComboBox(
                system_device_frame,
                values=["Auto-detect"],
                variable=self.system_audio_device_var,
                state="disabled",  # Disabled until checkbox is enabled
                **combobox_theme
            )
            self.system_audio_device_combo.pack(side="right", padx=(Spacing.SM, 0))
            
            # System audio status/info - use a more descriptive theme
            status_theme = ComponentThemes.get_label_theme("body_small")
            self.system_audio_status_label = ctk.CTkLabel(
                system_audio_frame,
                text="System audio capture not configured",
                **status_theme
            )
            self.system_audio_status_label.pack(anchor="w", padx=Spacing.LG, pady=(Spacing.XS, Spacing.LG))
            
            # Initialize system audio detection
            self._initialize_system_audio_detection()
        
        except Exception as e:
            self.logger.error(f"Error creating audio tab: {e}")
            # Create error frame to show the issue
            if audio_tab is not None:
                try:
                    error_label = ctk.CTkLabel(
                        audio_tab,
                        text=f"⚠️ Error loading audio settings: {str(e)[:100]}...",
                        text_color=ColorPalette.ERROR
                    )
                    error_label.pack(padx=Spacing.LG, pady=Spacing.LG)
                except:
                    pass  # If even this fails, we'll just log the error

    def _initialize_system_audio_detection(self):
        """Initialize system audio capture detection and populate devices."""
        try:
            # Import audio capture for device detection
            from pathlib import Path
            from src.audio.capture import AudioCapture
            
            # Create audio capture instance to check support
            audio_capture = AudioCapture()
            is_supported, info_message = audio_capture.is_loopback_supported()
            
            if is_supported:
                # Get available loopback devices
                loopback_devices = audio_capture.get_loopback_devices()
                device_names = ["Auto-detect"]
                
                for device in loopback_devices:
                    device_name = f"{device['name']} ({device['platform']})"
                    device_names.append(device_name)
                
                # Update combo box values
                self.system_audio_device_combo.configure(values=device_names)
                self.system_audio_status_label.configure(
                    text=f"✅ {info_message} - {len(loopback_devices)} devices found",
                    text_color=ColorPalette.SUCCESS
                )
                
                # Enable the checkbox
                self.enable_system_audio_checkbox.configure(state="normal")
                
            else:
                self.system_audio_status_label.configure(
                    text=f"❌ {info_message}",
                    text_color=ColorPalette.WARNING
                )
                # Keep checkbox disabled
                self.enable_system_audio_checkbox.configure(state="disabled")
                
        except ImportError as e:
            self.system_audio_status_label.configure(
                text="❌ Audio capture module not available",
                text_color=ColorPalette.WARNING
            )
            self.enable_system_audio_checkbox.configure(state="disabled")
        except Exception as e:
            self.system_audio_status_label.configure(
                text=f"❌ Error checking system audio support: {str(e)[:50]}...",
                text_color=ColorPalette.WARNING
            )
            self.enable_system_audio_checkbox.configure(state="disabled")

    def _on_system_audio_toggle(self):
        """Handle system audio capture toggle."""
        is_enabled = self.enable_system_audio_var.get()
        
        if is_enabled:
            self.system_audio_device_combo.configure(state="normal")
            self.logger.info("System audio capture enabled")
        else:
            self.system_audio_device_combo.configure(state="disabled")
            self.logger.info("System audio capture disabled")

    def _create_general_tab(self):
        """Create the general settings tab."""
        if not self.tabview:
            self.logger.error("Cannot create General tab: tabview is not initialized.")
            return
        
        general_tab = None
        try:
            general_tab = self.tabview.add("🔧 General")  # type: ignore
            
            # Apply scrollable frame with primary background
            general_scroll = ctk.CTkScrollableFrame(
                general_tab,
                fg_color=ColorPalette.BACKGROUND_PRIMARY,
                scrollbar_button_color=ColorPalette.ACCENT_PRIMARY
            )
            general_scroll.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
            
            prefs_frame = self._create_section(general_scroll, "🔧 Application Preferences")
            
            # Theme selection
            theme_frame = ctk.CTkFrame(prefs_frame, fg_color="transparent")
            theme_frame.pack(fill="x", padx=Spacing.LG, pady=(Spacing.MD, Spacing.LG))
            
            # Apply combobox theme from centralized system
            combobox_theme = ComponentThemes.get_combobox_theme()
            self.theme_combo = ctk.CTkComboBox(
                theme_frame,
                values=["Dark", "Light", "System"],
                **combobox_theme
            )
            self.theme_combo.pack(side="right", padx=(Spacing.SM, 0))

            self.theme_var = self._bind_variable(self.theme_combo, "theme", tk.StringVar)

            ctk.CTkLabel(theme_frame, text="Theme:", **ComponentThemes.get_label_theme()).pack(side="left")
        
        except Exception as e:
            self.logger.error(f"Error creating general tab: {e}")
            # Create error frame to show the issue
            if general_tab is None and self.tabview is not None:
                try:
                    general_tab = self.tabview.add("🔧 General (Error)")
                except:
                    pass
            
            if general_tab is not None:
                try:
                    error_label = ctk.CTkLabel(
                        general_tab,
                        text=f"⚠️ Error loading general settings: {str(e)[:100]}...",
                        text_color=ColorPalette.ERROR
                    )
                    error_label.pack(padx=Spacing.LG, pady=Spacing.LG)
                except:
                    pass  # If even this fails, we'll just log the error

    def _create_action_buttons(self):
        """Create action buttons section with centralized theme."""
        try:
            buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            buttons_frame.pack(fill="x", pady=Spacing.LG)
            
            # Apply button themes from centralized system
            success_button_theme = ComponentThemes.get_button_theme("success")
            danger_button_theme = ComponentThemes.get_button_theme("danger") # Use danger for reset
            primary_button_theme = ComponentThemes.get_button_theme("primary")
            
            # Save button
            self.save_button = ctk.CTkButton(
                buttons_frame,
                text="💾 Save Settings",
                command=self._save_settings,
                **success_button_theme
            )
            self.save_button.pack(side="left", padx=(0, Spacing.MD))
            
            # Reset button
            self.reset_button = ctk.CTkButton(
                buttons_frame,
                text="🔄 Reset Values",
                command=self._reset_settings,
                **danger_button_theme
            )
            self.reset_button.pack(side="left", padx=Spacing.MD)
            
            # Export button
            self.export_button = ctk.CTkButton(
                buttons_frame,
                text="📤 Export Config",
                command=self._export_settings,
                **primary_button_theme
            )
            self.export_button.pack(side="left", padx=Spacing.MD)
            
            # Import button - use secondary style
            secondary_button_theme = ComponentThemes.get_button_theme("secondary")
            self.import_button = ctk.CTkButton(
                buttons_frame,
                text="📥 Import Config",
                command=self._import_settings,
                **secondary_button_theme
            )
            self.import_button.pack(side="right")
        
        except Exception as e:
            self.logger.error(f"Error creating action buttons: {e}")
            # Create minimal save button as fallback
            fallback_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            fallback_frame.pack(fill="x", pady=Spacing.LG)
            
            fallback_button = ctk.CTkButton(
                fallback_frame,
                text="💾 Save Settings",
                fg_color=ColorPalette.SUCCESS,
                hover_color=ColorPalette.SUCCESS_HOVER,
                command=self._save_settings
            )
            fallback_button.pack(side="left")

    def _bind_variable(self, widget, key, var_type=None):
        """Creates, binds, and returns a variable for a widget."""
        if key in self._settings_definition:
            default_value = self._settings_definition[key]["default"]
            # Use provided var_type or default to StringVar
            if var_type is None:
                var_type = tk.StringVar
            variable = var_type(value=default_value)
            widget.configure(variable=variable)
            self._settings_definition[key]["var"] = variable
            return variable
        self.logger.warning(f"Attempted to bind variable for unknown setting key: {key}")
        return None

    def _create_slider_control(self, parent, label_text, min_value, max_value, default_value, var_setter):
        """Helper to create a slider control with label and value display."""
        try:
            control_frame = ctk.CTkFrame(parent, fg_color="transparent")
            control_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
            
            # Apply label theme from centralized system
            label_theme = ComponentThemes.get_label_theme()
            label = ctk.CTkLabel(
                control_frame,
                text=label_text,
                **label_theme
            )
            label.pack(side="left")
            
            # Value label with secondary text style
            value_var = tk.DoubleVar(value=default_value)
            var_setter(value_var)

            value_theme = ComponentThemes.get_label_theme("body_small")
            value_label = ctk.CTkLabel(
                control_frame,
                text=f"{default_value:.2f}",
                width=50,
                **value_theme
            )
            value_label.pack(side="right", padx=(Spacing.SM, 0))

            slider = ctk.CTkSlider(
                control_frame,
                from_=min_value,
                to=max_value,
                variable=value_var,
                command=lambda val: value_label.configure(text=f"{float(val):.2f}"),
                button_color=ColorPalette.ACCENT_PRIMARY,
                button_hover_color=ColorPalette.ACCENT_PRIMARY_HOVER,
                progress_color=ColorPalette.ACCENT_PRIMARY,
                fg_color=ColorPalette.BORDER_DEFAULT
            )
            slider.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, Spacing.SM))
            
            return value_var, slider, value_label
        
        except Exception as e:
            self.logger.error(f"Error creating slider control: {e}")
            # Create fallback frame
            fallback_frame = ctk.CTkFrame(parent, fg_color="transparent")
            fallback_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)
            
            fallback_label = ctk.CTkLabel(
                fallback_frame,
                text=f"⚠️ {label_text} (Error loading control)",
                text_color=ColorPalette.WARNING
            )
            fallback_label.pack(side="left")
            return None, None, None

    def _load_settings(self):
        """Load settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info(f"Settings loaded from {self.settings_file}")
            else:
                self.config = self.default_settings.copy()
                self.logger.info("Using default settings")
        except Exception as e:
            self.logger.exception("Error loading settings:")
            self.config = self.default_settings.copy()

    def _update_ui_from_config(self):
        """Update all UI variables from the self.config dictionary."""
        for key, value in self.config.items():
            var_name = f"{key}_var"
            if key in self._settings_definition:
                var = self._settings_definition[key].get("var")
                if var:
                    try:
                        var.set(value)
                    except Exception as e:
                        self.logger.warning(f"Could not set UI variable for '{key}': {e}")
        
        self.logger.info("UI updated from settings configuration.")

    def _update_ui_from_settings(self):
        """Update UI components with current settings values."""
        try:
            self._update_ui_from_config()
            self.logger.info("UI updated from settings")
            
        except Exception as e:
            self.logger.exception("Error updating UI from settings:")

    def _on_tts_engine_changed(self, value):
        """Handle TTS engine change and show/hide API key field."""
        self.logger.info(f"TTS engine changed to: {value}")
        
        # Show/hide API key field based on selected engine
        if value in ["OpenAI TTS", "Eleven Labs"] and self.tts_api_frame is not None:
            self.tts_api_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
            # Update placeholder text based on engine
            if self.tts_api_entry is not None:
                if value == "OpenAI TTS":
                    self.tts_api_entry.configure(placeholder_text="Enter OpenAI API Key")
                elif value == "Eleven Labs":
                    self.tts_api_entry.configure(placeholder_text="Enter Eleven Labs API Key")
        elif self.tts_api_frame is not None:
            self.tts_api_frame.pack_forget()
        
        # Update available models based on engine
        if value == "Local TTS":
            models = [
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/ljspeech/glow-tts",
                "tts_models/es/mai/tacotron2-DDC",
                "tts_models/multilingual/multi-dataset/bark"
            ]
        elif value == "OpenAI TTS":
            models = ["tts-1", "tts-1-hd"]
        elif value == "Eleven Labs":
            models = ["eleven_monolingual_v1", "eleven_multilingual_v2"]
        else:
            models = ["Default"]
            
        if hasattr(self, 'tts_model_combo') and self.tts_model_combo is not None:
            self.tts_model_combo.configure(values=models)
            if models and self.tts_model_var is not None:
                self.tts_model_var.set(models[0])

    def _on_translation_service_changed(self, value):
        """Handle translation service change and show/hide API key or local model fields."""
        self.logger.info(f"Translation service changed to: {value}")
        
        # Hide all conditional fields first
        if self.translation_api_frame is not None:
            self.translation_api_frame.pack_forget()
        if self.translation_local_model_frame is not None:
            self.translation_local_model_frame.pack_forget()
        
        # Show appropriate fields based on selected service
        if value in ["Microsoft Translator", "DeepL"] and self.translation_api_frame is not None:
            self.translation_api_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
            # Update placeholder text based on service
            if self.translation_api_entry is not None:
                if value == "Microsoft Translator":
                    self.translation_api_entry.configure(placeholder_text="Enter Microsoft Translator API Key")
                elif value == "DeepL":
                    self.translation_api_entry.configure(placeholder_text="Enter DeepL API Key")
        elif value == "Local Model" and self.translation_local_model_frame is not None:
            self.translation_local_model_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)

    def _validate_settings(self):
        """Validate current settings and show errors if any."""
        errors = []
        
        # Validate TTS settings
        if hasattr(self, 'tts_engine_var') and self.tts_engine_var is not None:
            tts_engine = self.tts_engine_var.get()
            if tts_engine in ["OpenAI TTS", "Eleven Labs"]:
                if not hasattr(self, 'tts_api_var') or self.tts_api_var is None or not self.tts_api_var.get().strip():
                    errors.append(f"{tts_engine} requires an API key.")
        
        # Validate Translation settings
        if hasattr(self, 'translation_service_var') and self.translation_service_var is not None:
            translation_service = self.translation_service_var.get()
            if translation_service in ["Microsoft Translator", "DeepL"]:
                if not hasattr(self, 'translation_api_var') or self.translation_api_var is None or not self.translation_api_var.get().strip():
                    errors.append(f"{translation_service} requires an API key.")
            elif translation_service == "Local Model":
                if hasattr(self, 'translation_local_model_var') and self.translation_local_model_var:
                    local_model = self.translation_local_model_var.get()
                    # Here you could add Ollama availability check
                    # For now, just check if a model is selected
                    if not local_model.strip():
                        errors.append("Local Model translation requires a model selection.")
        
        # Show errors if any
        if errors:
            error_message = "Please fix the following issues:\n\n" + "\n".join(f"• {error}" for error in errors)
            self._show_status_message(error_message, ColorPalette.ERROR)
            return False
        
        return True

    def _save_settings(self):
        """Save current settings to file with validation."""
        try:
            # Validate settings before saving
            if not self._validate_settings():
                return False
            
            # Collect current settings from UI
            current_settings = self.config.copy()
            for key, definition in self._settings_definition.items():
                var = definition.get("var")
                if var:
                    try:
                        current_settings[key] = var.get()
                    except Exception as e:
                        self.logger.warning(f"Could not get value for setting '{key}': {e}")
            
            # Update config
            self.config.update(current_settings)
            
            # Ensure settings directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Save engine settings to state manager for chat tab access
            if self.state_manager:
                try:
                    engine_settings = {
                        "tts_engine": current_settings.get("tts_engine", "System (SAPI)"),
                        "translation_service": current_settings.get("translation_service", "Google Translate"),
                        "tts_api_key": current_settings.get("tts_api_key", ""),
                        "translation_api_key": current_settings.get("translation_api_key", ""),
                        "translation_local_model": current_settings.get("translation_local_model", "llama3:8b")
                    }
                    self.state_manager.set_setting("engines", engine_settings)
                    self.logger.info("Engine settings saved to state manager")
                except Exception as e:
                    self.logger.error(f"Failed to save engine settings to state manager: {e}")
            
            self.logger.info(f"Settings saved to {self.settings_file}")
            
            # Show success feedback
            self._show_status_message("Settings saved successfully!", ColorPalette.SUCCESS)
            
            # Notify chat tab to update engine displays
            self._notify_chat_tab_of_engine_changes(current_settings)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            self._show_status_message(f"Error saving settings: {e}", ColorPalette.ERROR)
            return False

    def _notify_chat_tab_of_engine_changes(self, settings):
        """Notify chat tab of engine changes to update display labels."""
        try:
            # If core_bridge is available, use it to communicate with chat tab
            if self.core_bridge and hasattr(self.core_bridge, 'update_chat_engine_displays'):
                tts_engine = settings.get("tts_engine", "System (SAPI)")
                translation_service = settings.get("translation_service", "Google Translate")
                self.core_bridge.update_chat_engine_displays(tts_engine, translation_service)
                self.logger.info("Notified chat tab of engine changes")
        except Exception as e:
            self.logger.error(f"Failed to notify chat tab of engine changes: {e}")

    def _reset_settings(self):
        """Reset settings to default values."""
        try:
            self.config = self.default_settings.copy()
            self._update_ui_from_config()
            self.logger.info("Settings reset to defaults")
            self._show_status_message("Settings reset to defaults", ColorPalette.WARNING)
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
            self._show_status_message(f"Error resetting settings: {e}", ColorPalette.ERROR)

    def _export_settings(self):
        """Export settings to a file."""
        try:
            # Use tkinter file dialog
            import tkinter.filedialog as fd
            
            file_path = fd.asksaveasfilename(
                title="Export Settings",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Settings exported to {file_path}")
                self._show_status_message(f"Settings exported to {file_path}", ColorPalette.SUCCESS)
                
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            self._show_status_message(f"Error exporting settings: {e}", ColorPalette.ERROR)

    def _import_settings(self):
        """Import settings from a file."""
        try:
            # Use tkinter file dialog
            import tkinter.filedialog as fd
            
            file_path = fd.askopenfilename(
                title="Import Settings",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_config = json.load(f)
                
                # Validate and merge settings
                for key, value in imported_config.items():
                    if key in self.default_settings:
                        self.config[key] = value
                
                self._update_ui_from_config()
                self.logger.info(f"Settings imported from {file_path}")
                self._show_status_message(f"Settings imported from {file_path}", ColorPalette.SUCCESS)
                
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            self._show_status_message(f"Error importing settings: {e}", ColorPalette.ERROR)

    def _show_status_message(self, message: str, color: str):
        """Show status message (placeholder for future implementation)."""
        # This could be enhanced with a status bar or notification system
        self.logger.info(f"Status: {message}")

    def get_setting(self, key: str, default=None):
        """Get a specific setting value."""
        return self.config.get(key, default)

    def set_setting(self, key: str, value):
        """Set a specific setting value."""
        self.config[key] = value

    def get_frame(self) -> Optional[ctk.CTkFrame]:
        """Get the main frame widget.
        
        Returns:
            The main frame widget or None if not initialized
        """
        return self.main_frame
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings configuration.
        
        Returns:
            Dictionary of current settings
        """
        return self.config.copy()
