#!/usr/bin/env python3
"""
TalkBridge Desktop - Settings Tab (CustomTkinter)
=================================================

Settings tab for TTS, translation and animation with CustomTkinter.

Author: TalkBridge Team
Date: 2025-09-08
Version: 2.1

Requirements:
- customtkinter
- tkinter
======================================================================
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
import tkinter as tk
import customtkinter as ctk

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import unified theme
try:
    from src.desktop.ui.theme import (
        ColorPalette, Typography, Spacing, Dimensions, 
        ComponentThemes, UIText, Icons, UXGuidelines
    )
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

# Import UI utilities and theme
try:
    from src.desktop.ui.ui_utils import clean_text
    from src.desktop.ui.theme import ComponentThemes, Typography, ColorPalette, Dimensions
    UI_THEME_AVAILABLE = True
except ImportError:
    UI_THEME_AVAILABLE = False

try:
    from src.config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class SettingsTheme:
    """Theme configuration for the settings tab."""
    
    # Use unified theme if available, otherwise fallback to original colors
    if THEME_AVAILABLE:
        BACKGROUND_MAIN = ColorPalette.BACKGROUND_PRIMARY
        BACKGROUND_SECONDARY = ColorPalette.BACKGROUND_SECONDARY
        BACKGROUND_ELEVATED = ColorPalette.BACKGROUND_ELEVATED
        
        TEXT_PRIMARY = ColorPalette.TEXT_PRIMARY
        TEXT_SECONDARY = ColorPalette.TEXT_SECONDARY
        TEXT_HINT = ColorPalette.TEXT_HINT
        
        ACCENT_BLUE = ColorPalette.ACCENT_PRIMARY
        ACCENT_BLUE_HOVER = ColorPalette.ACCENT_PRIMARY_HOVER
        ACCENT_GREEN = ColorPalette.SUCCESS
        ACCENT_GREEN_HOVER = ColorPalette.SUCCESS_HOVER
        ACCENT_ORANGE = ColorPalette.WARNING
        ACCENT_ORANGE_HOVER = ColorPalette.WARNING_HOVER
        
        INPUT_BACKGROUND = ColorPalette.INPUT_BACKGROUND
        INPUT_BORDER = ColorPalette.BORDER_DEFAULT
        INPUT_BORDER_FOCUS = ColorPalette.BORDER_FOCUS
        
        SUCCESS_COLOR = ColorPalette.SUCCESS
        WARNING_COLOR = ColorPalette.WARNING
        ERROR_COLOR = ColorPalette.ERROR
    else:
        # Fallback colors
        BACKGROUND_MAIN = "#1e1e1e"
        BACKGROUND_SECONDARY = "#2d2d2d"
        BACKGROUND_ELEVATED = "#3c3c3c"
        
        TEXT_PRIMARY = "#ffffff"
        TEXT_SECONDARY = "#cccccc"
        TEXT_HINT = "#888888"
        
        ACCENT_BLUE = "#0078d4"
        ACCENT_BLUE_HOVER = "#106ebe"
        ACCENT_GREEN = "#4CAF50"
        ACCENT_GREEN_HOVER = "#45a049"
        ACCENT_ORANGE = "#FF9800"
        ACCENT_ORANGE_HOVER = "#F57C00"
        
        INPUT_BACKGROUND = "#3c3c3c"
        INPUT_BORDER = "#555555"
        INPUT_BORDER_FOCUS = "#0078d4"
        
        SUCCESS_COLOR = "#4CAF50"
        WARNING_COLOR = "#FF9800"
        ERROR_COLOR = "#f44336"


# Spacing (using theme if available)
MAIN_MARGIN = Spacing.MARGIN_MAIN if THEME_AVAILABLE else 20
SECTION_SPACING = Spacing.LG if THEME_AVAILABLE else 15
ITEM_SPACING = Spacing.SM if THEME_AVAILABLE else 10
SMALL_SPACING = Spacing.XS if THEME_AVAILABLE else 5

# Sizes (using theme if available)
BUTTON_HEIGHT = Dimensions.HEIGHT_BUTTON if THEME_AVAILABLE else 40
INPUT_HEIGHT = Dimensions.HEIGHT_INPUT if THEME_AVAILABLE else 35
SLIDER_HEIGHT = Dimensions.HEIGHT_SLIDER if THEME_AVAILABLE else 25
TAB_HEIGHT = 300

# Fonts (using theme if available)
TITLE_FONT_SIZE = Typography.FONT_SIZE_H1 if THEME_AVAILABLE else 20
SECTION_FONT_SIZE = Typography.FONT_SIZE_H3 if THEME_AVAILABLE else 16
LABEL_FONT_SIZE = Typography.FONT_SIZE_BODY if THEME_AVAILABLE else 12
INPUT_FONT_SIZE = Typography.FONT_SIZE_CAPTION if THEME_AVAILABLE else 11


class SettingsTab:
    """
    Enhanced system settings tab with CustomTkinter.
    
    Features:
    - Comprehensive TTS (Text-to-Speech) settings
    - Advanced translation configuration
    - Animation and visual effects settings
    - Audio input/output configuration
    - Application preferences and theming
    - Import/export configuration support
    - Real-time settings validation
    """

    def __init__(self, parent, state_manager=None, core_bridge=None):
        """Initialize the enhanced settings tab."""
        self.parent = parent
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        self.logger = logging.getLogger("talkbridge.desktop.settings")
        
        # Configuration
        self.config = {}
        self.settings_file = Path.home() / ".talkbridge" / "settings.json"
        self.default_settings = self._get_default_settings()
        
        # UI Components (will be initialized in setup_ui)
        self.main_frame = None
        self.title_label = None
        self.tabview = None
        
        # TTS Settings
        self.tts_engine_var = None
        self.tts_model_var = None
        self.tts_voice_var = None
        self.tts_speed_var = None
        self.tts_pitch_var = None
        self.tts_volume_var = None
        
        # Translation Settings
        self.translation_service_var = None
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
        
        # Load configuration
        self._load_settings()
        
        # Setup UI
        self.setup_ui()
        
        self.logger.info("Enhanced settings tab initialized")

    def setup_ui(self):
        """Set up the enhanced settings user interface."""
        # Main frame with themed background
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=SettingsTheme.BACKGROUND_MAIN)
        self.main_frame.pack(fill="both", expand=True, padx=MAIN_MARGIN, pady=MAIN_MARGIN)
        
        # Title section
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, SECTION_SPACING))
        
        self.title_label = ctk.CTkLabel(
            title_frame,
            text=clean_text("System Settings") if THEME_AVAILABLE else "System Settings",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=TITLE_FONT_SIZE, weight="bold"), "text_color": SettingsTheme.TEXT_PRIMARY}
        )
        self.title_label.pack(pady=ITEM_SPACING)
        
        # Settings tabs
        self.tabview = ctk.CTkTabview(
            self.main_frame,
            fg_color=SettingsTheme.BACKGROUND_SECONDARY,
            segmented_button_fg_color=SettingsTheme.BACKGROUND_ELEVATED,
            segmented_button_selected_color=SettingsTheme.ACCENT_BLUE,
            segmented_button_selected_hover_color=SettingsTheme.ACCENT_BLUE_HOVER,
            text_color=SettingsTheme.TEXT_PRIMARY,
            height=TAB_HEIGHT
        )
        self.tabview.pack(fill="both", expand=True, pady=SECTION_SPACING)
        
        # Create tabs
        self._create_tts_tab()
        self._create_translation_tab()
        self._create_animation_tab()
        self._create_audio_tab()
        self._create_general_tab()
        
        # Action buttons section
        self._create_action_buttons()
        
        # Load current settings into UI
        self._update_ui_from_settings()
        
        self.logger.info("Enhanced settings UI setup completed")

    def _create_tts_tab(self):
        """Create the TTS (Text-to-Speech) settings tab."""
        tts_tab = self.tabview.add("🔊 TTS")
        
        # Scrollable frame for TTS settings
        tts_scroll = ctk.CTkScrollableFrame(
            tts_tab,
            fg_color=SettingsTheme.BACKGROUND_MAIN,
            scrollbar_button_color=SettingsTheme.ACCENT_BLUE
        )
        tts_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Voice Synthesis Engine Section
        engine_frame = ctk.CTkFrame(tts_scroll, fg_color=SettingsTheme.BACKGROUND_SECONDARY)
        engine_frame.pack(fill="x", pady=SECTION_SPACING)
        
        engine_title = ctk.CTkLabel(
            engine_frame,
            text=clean_text("Voice Synthesis Engine") if THEME_AVAILABLE else "Voice Synthesis Engine",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=SECTION_FONT_SIZE, weight="bold"), "text_color": SettingsTheme.TEXT_PRIMARY}
        )
        engine_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Engine selection
        engine_selection_frame = ctk.CTkFrame(engine_frame, fg_color="transparent")
        engine_selection_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
        
        ctk.CTkLabel(
            engine_selection_frame,
            text=clean_text("TTS Engine:") if THEME_AVAILABLE else "TTS Engine:",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=LABEL_FONT_SIZE), "text_color": SettingsTheme.TEXT_PRIMARY}
        ).pack(side="left")
        
        self.tts_engine_var = tk.StringVar(value="TTS Coqui (Local)")
        self.tts_engine_combo = ctk.CTkComboBox(
            engine_selection_frame,
            values=[
                "TTS Coqui (Local)",
                "OpenAI TTS (API)",
                "Azure Speech (API)",
                "Google TTS (API)",
                "System (SAPI)"
            ],
            variable=self.tts_engine_var,
            command=self._on_tts_engine_changed,
            **ComponentThemes.get_combobox_theme() if THEME_AVAILABLE else {"fg_color": SettingsTheme.INPUT_BACKGROUND, "border_color": SettingsTheme.INPUT_BORDER, "button_color": SettingsTheme.ACCENT_BLUE}
        )
        self.tts_engine_combo.pack(side="right", padx=(10, 0))
        
        # TTS Model selection
        model_selection_frame = ctk.CTkFrame(engine_frame, fg_color="transparent")
        model_selection_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
        
        ctk.CTkLabel(
            model_selection_frame,
            text=clean_text("Voice Model:") if THEME_AVAILABLE else "Voice Model:",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=LABEL_FONT_SIZE), "text_color": SettingsTheme.TEXT_PRIMARY}
        ).pack(side="left")
        
        self.tts_model_var = tk.StringVar(value="tts_models/en/ljspeech/tacotron2-DDC")
        self.tts_model_combo = ctk.CTkComboBox(
            model_selection_frame,
            values=[
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/ljspeech/glow-tts",
                "tts_models/es/mai/tacotron2-DDC",
                "tts_models/multilingual/multi-dataset/bark"
            ],
            variable=self.tts_model_var,
            fg_color=SettingsTheme.INPUT_BACKGROUND,
            border_color=SettingsTheme.INPUT_BORDER,
            button_color=SettingsTheme.ACCENT_BLUE
        )
        self.tts_model_combo.pack(side="right", padx=(10, 0))
        
        # Voice selection
        voice_selection_frame = ctk.CTkFrame(engine_frame, fg_color="transparent")
        voice_selection_frame.pack(fill="x", padx=15, pady=(ITEM_SPACING, 15))
        
        ctk.CTkLabel(
            voice_selection_frame,
            text="Voice:",
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=SettingsTheme.TEXT_PRIMARY
        ).pack(side="left")
        
        self.tts_voice_var = tk.StringVar(value="Female (Default)")
        self.tts_voice_combo = ctk.CTkComboBox(
            voice_selection_frame,
            values=["Female (Default)", "Male (Alternative)", "Child", "Elderly"],
            variable=self.tts_voice_var,
            fg_color=SettingsTheme.INPUT_BACKGROUND,
            border_color=SettingsTheme.INPUT_BORDER,
            button_color=SettingsTheme.ACCENT_BLUE
        )
        self.tts_voice_combo.pack(side="right", padx=(10, 0))
        
        # Voice Parameters Section
        params_frame = ctk.CTkFrame(tts_scroll, fg_color=SettingsTheme.BACKGROUND_SECONDARY)
        params_frame.pack(fill="x", pady=SECTION_SPACING)
        
        params_title = ctk.CTkLabel(
            params_frame,
            text="🎛️ Voice Parameters",
            font=ctk.CTkFont(size=SECTION_FONT_SIZE, weight="bold"),
            text_color=SettingsTheme.TEXT_PRIMARY
        )
        params_title.pack(anchor="w", padx=15, pady=(15, 10))
        
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

    def _create_translation_tab(self):
        """Create the translation settings tab."""
        trans_tab = self.tabview.add("🌐 Translation")
        
        trans_scroll = ctk.CTkScrollableFrame(
            trans_tab,
            fg_color=SettingsTheme.BACKGROUND_MAIN,
            scrollbar_button_color=SettingsTheme.ACCENT_BLUE
        )
        trans_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Translation Service Section
        service_frame = ctk.CTkFrame(trans_scroll, fg_color=SettingsTheme.BACKGROUND_SECONDARY)
        service_frame.pack(fill="x", pady=SECTION_SPACING)
        
        service_title = ctk.CTkLabel(
            service_frame,
            text="🌐 Translation Service",
            font=ctk.CTkFont(size=SECTION_FONT_SIZE, weight="bold"),
            text_color=SettingsTheme.TEXT_PRIMARY
        )
        service_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Service selection
        service_selection_frame = ctk.CTkFrame(service_frame, fg_color="transparent")
        service_selection_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
        
        ctk.CTkLabel(
            service_selection_frame,
            text="Service:",
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=SettingsTheme.TEXT_PRIMARY
        ).pack(side="left")
        
        self.translation_service_var = tk.StringVar(value="Google Translate")
        self.translation_service_combo = ctk.CTkComboBox(
            service_selection_frame,
            values=["Google Translate", "Microsoft Translator", "DeepL", "Local AI"],
            variable=self.translation_service_var,
            fg_color=SettingsTheme.INPUT_BACKGROUND,
            border_color=SettingsTheme.INPUT_BORDER,
            button_color=SettingsTheme.ACCENT_BLUE
        )
        self.translation_service_combo.pack(side="right", padx=(10, 0))
        
        # Language Configuration Section
        lang_frame = ctk.CTkFrame(trans_scroll, fg_color=SettingsTheme.BACKGROUND_SECONDARY)
        lang_frame.pack(fill="x", pady=SECTION_SPACING)
        
        lang_title = ctk.CTkLabel(
            lang_frame,
            text="🗣️ Language Configuration",
            font=ctk.CTkFont(size=SECTION_FONT_SIZE, weight="bold"),
            text_color=SettingsTheme.TEXT_PRIMARY
        )
        lang_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Source language
        source_lang_frame = ctk.CTkFrame(lang_frame, fg_color="transparent")
        source_lang_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
        
        ctk.CTkLabel(
            source_lang_frame,
            text="Source Language:",
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=SettingsTheme.TEXT_PRIMARY
        ).pack(side="left")
        
        self.source_lang_var = tk.StringVar(value="Auto-detect")
        self.source_lang_combo = ctk.CTkComboBox(
            source_lang_frame,
            values=["Auto-detect", "English", "Spanish", "French", "German", "Italian", "Portuguese"],
            variable=self.source_lang_var,
            fg_color=SettingsTheme.INPUT_BACKGROUND,
            border_color=SettingsTheme.INPUT_BORDER,
            button_color=SettingsTheme.ACCENT_BLUE
        )
        self.source_lang_combo.pack(side="right", padx=(10, 0))
        
        # Target language
        target_lang_frame = ctk.CTkFrame(lang_frame, fg_color="transparent")
        target_lang_frame.pack(fill="x", padx=15, pady=(ITEM_SPACING, 15))
        
        ctk.CTkLabel(
            target_lang_frame,
            text="Target Language:",
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=SettingsTheme.TEXT_PRIMARY
        ).pack(side="left")
        
        self.target_lang_var = tk.StringVar(value="English")
        self.target_lang_combo = ctk.CTkComboBox(
            target_lang_frame,
            values=["English", "Spanish", "French", "German", "Italian", "Portuguese", "Chinese", "Japanese"],
            variable=self.target_lang_var,
            fg_color=SettingsTheme.INPUT_BACKGROUND,
            border_color=SettingsTheme.INPUT_BORDER,
            button_color=SettingsTheme.ACCENT_BLUE
        )
        self.target_lang_combo.pack(side="right", padx=(10, 0))

    def _create_animation_tab(self):
        """Create the animation settings tab."""
        anim_tab = self.tabview.add("Animation")
        
        anim_scroll = ctk.CTkScrollableFrame(
            anim_tab,
            fg_color=SettingsTheme.BACKGROUND_MAIN,
            scrollbar_button_color=SettingsTheme.ACCENT_BLUE
        )
        anim_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Animation Controls Section
        controls_frame = ctk.CTkFrame(anim_scroll, fg_color=SettingsTheme.BACKGROUND_SECONDARY)
        controls_frame.pack(fill="x", pady=SECTION_SPACING)
        
        controls_title = ctk.CTkLabel(
            controls_frame,
            text="Animation Controls",
            font=ctk.CTkFont(size=SECTION_FONT_SIZE, weight="bold"),
            text_color=SettingsTheme.TEXT_PRIMARY
        )
        controls_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Enable animations checkbox
        self.enable_animations_var = tk.BooleanVar(value=True)
        self.enable_animations_checkbox = ctk.CTkCheckBox(
            controls_frame,
            text="Enable Animations",
            variable=self.enable_animations_var,
            text_color=SettingsTheme.TEXT_PRIMARY,
            fg_color=SettingsTheme.ACCENT_BLUE,
            hover_color=SettingsTheme.ACCENT_BLUE_HOVER
        )
        self.enable_animations_checkbox.pack(anchor="w", padx=15, pady=ITEM_SPACING)
        
        # Animation speed
        self._create_slider_control(
            controls_frame,
            "Animation Speed:",
            0.5, 3.0, 1.0,
            lambda var: setattr(self, 'animation_speed_var', var)
        )

    def _create_audio_tab(self):
        """Create the audio settings tab."""
        audio_tab = self.tabview.add("🎤 Audio")
        
        audio_scroll = ctk.CTkScrollableFrame(
            audio_tab,
            fg_color=SettingsTheme.BACKGROUND_MAIN,
            scrollbar_button_color=SettingsTheme.ACCENT_BLUE
        )
        audio_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Device Configuration Section
        device_frame = ctk.CTkFrame(audio_scroll, fg_color=SettingsTheme.BACKGROUND_SECONDARY)
        device_frame.pack(fill="x", pady=SECTION_SPACING)
        
        device_title = ctk.CTkLabel(
            device_frame,
            text="🎤 Audio Devices",
            font=ctk.CTkFont(size=SECTION_FONT_SIZE, weight="bold"),
            text_color=SettingsTheme.TEXT_PRIMARY
        )
        device_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Input device
        input_device_frame = ctk.CTkFrame(device_frame, fg_color="transparent")
        input_device_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
        
        ctk.CTkLabel(
            input_device_frame,
            text="Input Device:",
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=SettingsTheme.TEXT_PRIMARY
        ).pack(side="left")
        
        self.input_device_var = tk.StringVar(value="Default")
        self.input_device_combo = ctk.CTkComboBox(
            input_device_frame,
            values=["Default", "Microphone (Built-in)", "USB Microphone", "Headset"],
            variable=self.input_device_var,
            fg_color=SettingsTheme.INPUT_BACKGROUND,
            border_color=SettingsTheme.INPUT_BORDER,
            button_color=SettingsTheme.ACCENT_BLUE
        )
        self.input_device_combo.pack(side="right", padx=(10, 0))

    def _create_general_tab(self):
        """Create the general settings tab."""
        general_tab = self.tabview.add("🔧 General")
        
        general_scroll = ctk.CTkScrollableFrame(
            general_tab,
            fg_color=SettingsTheme.BACKGROUND_MAIN,
            scrollbar_button_color=SettingsTheme.ACCENT_BLUE
        )
        general_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Application Preferences Section
        prefs_frame = ctk.CTkFrame(general_scroll, fg_color=SettingsTheme.BACKGROUND_SECONDARY)
        prefs_frame.pack(fill="x", pady=SECTION_SPACING)
        
        prefs_title = ctk.CTkLabel(
            prefs_frame,
            text="🔧 Application Preferences",
            font=ctk.CTkFont(size=SECTION_FONT_SIZE, weight="bold"),
            text_color=SettingsTheme.TEXT_PRIMARY
        )
        prefs_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Theme selection
        theme_frame = ctk.CTkFrame(prefs_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=15, pady=(ITEM_SPACING, 15))
        
        ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=SettingsTheme.TEXT_PRIMARY
        ).pack(side="left")
        
        self.theme_var = tk.StringVar(value="Dark")
        self.theme_combo = ctk.CTkComboBox(
            theme_frame,
            values=["Dark", "Light", "System"],
            variable=self.theme_var,
            fg_color=SettingsTheme.INPUT_BACKGROUND,
            border_color=SettingsTheme.INPUT_BORDER,
            button_color=SettingsTheme.ACCENT_BLUE
        )
        self.theme_combo.pack(side="right", padx=(10, 0))

    def _create_action_buttons(self):
        """Create action buttons section."""
        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=SECTION_SPACING)
        
        # Save button
        self.save_button = ctk.CTkButton(
            buttons_frame,
            text="💾 Save Settings",
            height=BUTTON_HEIGHT,
            fg_color=SettingsTheme.ACCENT_GREEN,
            hover_color=SettingsTheme.ACCENT_GREEN_HOVER,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._save_settings
        )
        self.save_button.pack(side="left", padx=(0, ITEM_SPACING))
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            buttons_frame,
            text="Reset Values",
            height=BUTTON_HEIGHT,
            fg_color=SettingsTheme.ACCENT_ORANGE,
            hover_color=SettingsTheme.ACCENT_ORANGE_HOVER,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._reset_settings
        )
        self.reset_button.pack(side="left", padx=ITEM_SPACING)
        
        # Export button
        self.export_button = ctk.CTkButton(
            buttons_frame,
            text="📤 Export Config",
            height=BUTTON_HEIGHT,
            fg_color=SettingsTheme.ACCENT_BLUE,
            hover_color=SettingsTheme.ACCENT_BLUE_HOVER,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._export_settings
        )
        self.export_button.pack(side="left", padx=ITEM_SPACING)
        
        # Import button
        self.import_button = ctk.CTkButton(
            buttons_frame,
            text="📥 Import Config",
            height=BUTTON_HEIGHT,
            fg_color=SettingsTheme.INPUT_BACKGROUND,
            hover_color=SettingsTheme.BACKGROUND_ELEVATED,
            border_width=2,
            border_color=SettingsTheme.INPUT_BORDER,
            text_color=SettingsTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._import_settings
        )
        self.import_button.pack(side="right")

    def _create_slider_control(self, parent, label_text, min_value, max_value, default_value, var_setter):
        """Create a slider control with label and value display."""
        control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        control_frame.pack(fill="x", padx=15, pady=ITEM_SPACING)
        
        # Label
        label = ctk.CTkLabel(
            control_frame,
            text=label_text,
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=SettingsTheme.TEXT_PRIMARY
        )
        label.pack(side="left")
        
        # Value label
        value_var = tk.DoubleVar(value=default_value)
        var_setter(value_var)
        
        value_label = ctk.CTkLabel(
            control_frame,
            text=f"{default_value:.2f}",
            font=ctk.CTkFont(size=LABEL_FONT_SIZE),
            text_color=SettingsTheme.TEXT_SECONDARY,
            width=50
        )
        value_label.pack(side="right", padx=(10, 0))
        
        # Slider
        slider = ctk.CTkSlider(
            control_frame,
            from_=min_value,
            to=max_value,
            variable=value_var,
            button_color=SettingsTheme.ACCENT_BLUE,
            button_hover_color=SettingsTheme.ACCENT_BLUE_HOVER,
            progress_color=SettingsTheme.ACCENT_BLUE,
            fg_color=SettingsTheme.INPUT_BORDER,
            command=lambda val: value_label.configure(text=f"{float(val):.2f}")
        )
        slider.pack(side="right", fill="x", expand=True, padx=(10, 10))
        
        return value_var, slider, value_label

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings configuration."""
        return {
            # TTS Settings
            "tts_engine": "TTS Coqui (Local)",
            "tts_model": "tts_models/en/ljspeech/tacotron2-DDC",
            "tts_voice": "Female (Default)",
            "tts_speed": 1.0,
            "tts_pitch": 1.0,
            "tts_volume": 0.8,
            
            # Translation Settings
            "translation_service": "Google Translate",
            "source_language": "Auto-detect",
            "target_language": "English",
            "auto_detect": True,
            "translation_quality": "Standard",
            
            # Animation Settings
            "enable_animations": True,
            "animation_speed": 1.0,
            "face_tracking": False,
            "avatar_style": "Realistic",
            "background_effects": False,
            
            # Audio Settings
            "input_device": "Default",
            "output_device": "Default",
            "input_volume": 0.8,
            "output_volume": 0.8,
            "noise_cancellation": True,
            "echo_cancellation": True,
            
            # General Settings
            "theme": "Dark",
            "language": "English",
            "auto_save": True,
            "notifications": True,
            "startup": False
        }

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
            self.logger.error(f"Error loading settings: {e}")
            self.config = self.default_settings.copy()

    def _update_ui_from_settings(self):
        """Update UI components with current settings values."""
        try:
            # TTS Settings
            if hasattr(self, 'tts_engine_var') and self.tts_engine_var:
                self.tts_engine_var.set(self.config.get("tts_engine", "TTS Coqui (Local)"))
            if hasattr(self, 'tts_model_var') and self.tts_model_var:
                self.tts_model_var.set(self.config.get("tts_model", "tts_models/en/ljspeech/tacotron2-DDC"))
            if hasattr(self, 'tts_voice_var') and self.tts_voice_var:
                self.tts_voice_var.set(self.config.get("tts_voice", "Female (Default)"))
            if hasattr(self, 'tts_speed_var') and self.tts_speed_var:
                self.tts_speed_var.set(self.config.get("tts_speed", 1.0))
            if hasattr(self, 'tts_pitch_var') and self.tts_pitch_var:
                self.tts_pitch_var.set(self.config.get("tts_pitch", 1.0))
            if hasattr(self, 'tts_volume_var') and self.tts_volume_var:
                self.tts_volume_var.set(self.config.get("tts_volume", 0.8))
            
            # Translation Settings
            if hasattr(self, 'translation_service_var') and self.translation_service_var:
                self.translation_service_var.set(self.config.get("translation_service", "Google Translate"))
            if hasattr(self, 'source_lang_var') and self.source_lang_var:
                self.source_lang_var.set(self.config.get("source_language", "Auto-detect"))
            if hasattr(self, 'target_lang_var') and self.target_lang_var:
                self.target_lang_var.set(self.config.get("target_language", "English"))
                
            # Animation Settings
            if hasattr(self, 'enable_animations_var') and self.enable_animations_var:
                self.enable_animations_var.set(self.config.get("enable_animations", True))
            if hasattr(self, 'animation_speed_var') and self.animation_speed_var:
                self.animation_speed_var.set(self.config.get("animation_speed", 1.0))
                
            # Audio Settings
            if hasattr(self, 'input_device_var') and self.input_device_var:
                self.input_device_var.set(self.config.get("input_device", "Default"))
                
            # General Settings
            if hasattr(self, 'theme_var') and self.theme_var:
                self.theme_var.set(self.config.get("theme", "Dark"))
                
            self.logger.info("UI updated from settings")
            
        except Exception as e:
            self.logger.error(f"Error updating UI from settings: {e}")

    def _on_tts_engine_changed(self, value):
        """Handle TTS engine change."""
        self.logger.info(f"TTS engine changed to: {value}")
        # Update available models based on engine
        if value == "TTS Coqui (Local)":
            models = [
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/ljspeech/glow-tts",
                "tts_models/es/mai/tacotron2-DDC",
                "tts_models/multilingual/multi-dataset/bark"
            ]
        elif value == "OpenAI TTS (API)":
            models = ["tts-1", "tts-1-hd"]
        else:
            models = ["Default"]
            
        if hasattr(self, 'tts_model_combo'):
            self.tts_model_combo.configure(values=models)
            if models:
                self.tts_model_var.set(models[0])

    def _save_settings(self):
        """Save current settings to file."""
        try:
            # Collect current settings from UI
            current_settings = {}
            
            # TTS Settings
            if hasattr(self, 'tts_engine_var') and self.tts_engine_var:
                current_settings["tts_engine"] = self.tts_engine_var.get()
            if hasattr(self, 'tts_model_var') and self.tts_model_var:
                current_settings["tts_model"] = self.tts_model_var.get()
            if hasattr(self, 'tts_voice_var') and self.tts_voice_var:
                current_settings["tts_voice"] = self.tts_voice_var.get()
            if hasattr(self, 'tts_speed_var') and self.tts_speed_var:
                current_settings["tts_speed"] = self.tts_speed_var.get()
            if hasattr(self, 'tts_pitch_var') and self.tts_pitch_var:
                current_settings["tts_pitch"] = self.tts_pitch_var.get()
            if hasattr(self, 'tts_volume_var') and self.tts_volume_var:
                current_settings["tts_volume"] = self.tts_volume_var.get()
            
            # Translation Settings
            if hasattr(self, 'translation_service_var') and self.translation_service_var:
                current_settings["translation_service"] = self.translation_service_var.get()
            if hasattr(self, 'source_lang_var') and self.source_lang_var:
                current_settings["source_language"] = self.source_lang_var.get()
            if hasattr(self, 'target_lang_var') and self.target_lang_var:
                current_settings["target_language"] = self.target_lang_var.get()
                
            # Animation Settings
            if hasattr(self, 'enable_animations_var') and self.enable_animations_var:
                current_settings["enable_animations"] = self.enable_animations_var.get()
            if hasattr(self, 'animation_speed_var') and self.animation_speed_var:
                current_settings["animation_speed"] = self.animation_speed_var.get()
                
            # Audio Settings
            if hasattr(self, 'input_device_var') and self.input_device_var:
                current_settings["input_device"] = self.input_device_var.get()
                
            # General Settings
            if hasattr(self, 'theme_var') and self.theme_var:
                current_settings["theme"] = self.theme_var.get()
            
            # Update config
            self.config.update(current_settings)
            
            # Ensure settings directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Settings saved to {self.settings_file}")
            
            # Show success feedback
            self._show_status_message("Settings saved successfully!", SettingsTheme.SUCCESS_COLOR)
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            self._show_status_message(f"Error saving settings: {e}", SettingsTheme.ERROR_COLOR)

    def _reset_settings(self):
        """Reset settings to default values."""
        try:
            self.config = self.default_settings.copy()
            self._update_ui_from_settings()
            self.logger.info("Settings reset to defaults")
            self._show_status_message("Settings reset to defaults", SettingsTheme.WARNING_COLOR)
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
            self._show_status_message(f"Error resetting settings: {e}", SettingsTheme.ERROR_COLOR)

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
                self._show_status_message(f"Settings exported to {file_path}", SettingsTheme.SUCCESS_COLOR)
                
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            self._show_status_message(f"Error exporting settings: {e}", SettingsTheme.ERROR_COLOR)

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
                
                self._update_ui_from_settings()
                self.logger.info(f"Settings imported from {file_path}")
                self._show_status_message(f"Settings imported from {file_path}", SettingsTheme.SUCCESS_COLOR)
                
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            self._show_status_message(f"Error importing settings: {e}", SettingsTheme.ERROR_COLOR)

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

    def get_frame(self):
        """Get the main frame widget."""
        return self.main_frame
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        self.logger = logging.getLogger("talkbridge.desktop.settings")
        
        # UI elements
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.settings_tabview: Optional[ctk.CTkTabview] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        
        # Settings variables
        self.settings = {}
        
        # Callbacks
        self.error_occurred_callback = None
        
        # Setup UI
        self.setup_ui()
        self.load_settings()

    def setup_ui(self) -> None:
        """Sets up the settings interface."""
        self.logger.info("Setting up settings tab UI")
        
        # Main frame
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="TalkBridge Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Settings tabview
        self.settings_tabview = ctk.CTkTabview(self.main_frame, width=800, height=500)
        self.settings_tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add setting tabs
        self.settings_tabview.add("Audio")
        self.settings_tabview.add("TTS")
        self.settings_tabview.add("Translation")
        self.settings_tabview.add("Avatar")
        self.settings_tabview.add("General")
        
        # Setup each tab
        self.setup_audio_tab()
        self.setup_tts_tab()
        self.setup_translation_tab()
        self.setup_avatar_tab()
        self.setup_general_tab()
        
        # Control buttons frame
        control_frame = ctk.CTkFrame(self.main_frame)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # Save button
        save_button = ctk.CTkButton(
            control_frame,
            text="Save Settings",
            width=120,
            command=self.save_settings
        )
        save_button.pack(side="left", padx=10, pady=10)
        
        # Restore defaults button
        restore_button = ctk.CTkButton(
            control_frame,
            text="Restore Defaults",
            width=120,
            fg_color="orange",
            hover_color="darkorange",
            command=self.restore_defaults
        )
        restore_button.pack(side="left", padx=10, pady=10)
        
        # Export button
        export_button = ctk.CTkButton(
            control_frame,
            text="Export Settings",
            width=120,
            fg_color="green",
            hover_color="darkgreen",
            command=self.export_settings
        )
        export_button.pack(side="left", padx=10, pady=10)
        
        # Import button
        import_button = ctk.CTkButton(
            control_frame,
            text="Import Settings",
            width=120,
            fg_color="blue",
            hover_color="darkblue",
            command=self.import_settings
        )
        import_button.pack(side="left", padx=10, pady=10)
        
        # Status frame
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Settings ready",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=5)

    def setup_audio_tab(self) -> None:
        """Sets up the audio settings tab."""
        audio_tab = self.settings_tabview.tab("Audio")
        
        # Audio frame
        audio_frame = ctk.CTkScrollableFrame(audio_tab)
        audio_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input device
        input_label = ctk.CTkLabel(
            audio_frame,
            text="Input Device:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        input_label.pack(anchor="w", pady=(10, 5))
        
        self.input_device_combo = ctk.CTkComboBox(
            audio_frame,
            values=["Default", "Microphone 1", "Microphone 2", "USB Headset"],
            width=300
        )
        self.input_device_combo.pack(anchor="w", padx=20, pady=5)
        
        # Output device
        output_label = ctk.CTkLabel(
            audio_frame,
            text="Output Device:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_label.pack(anchor="w", pady=(20, 5))
        
        self.output_device_combo = ctk.CTkComboBox(
            audio_frame,
            values=["Default", "Speakers", "Headphones", "USB Headset"],
            width=300
        )
        self.output_device_combo.pack(anchor="w", padx=20, pady=5)
        
        # Sample rate
        sample_rate_label = ctk.CTkLabel(
            audio_frame,
            text="Sample Rate:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        sample_rate_label.pack(anchor="w", pady=(20, 5))
        
        self.sample_rate_combo = ctk.CTkComboBox(
            audio_frame,
            values=["16000", "22050", "44100", "48000"],
            width=150
        )
        self.sample_rate_combo.pack(anchor="w", padx=20, pady=5)
        self.sample_rate_combo.set("16000")
        
        # Volume control
        volume_label = ctk.CTkLabel(
            audio_frame,
            text="Master Volume:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        volume_label.pack(anchor="w", pady=(20, 5))
        
        volume_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        volume_frame.pack(fill="x", padx=20, pady=5)
        
        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self.on_volume_changed
        )
        self.volume_slider.pack(side="left", fill="x", expand=True)
        self.volume_slider.set(80)
        
        self.volume_label = ctk.CTkLabel(
            volume_frame,
            text="80%",
            font=ctk.CTkFont(size=12)
        )
        self.volume_label.pack(side="right", padx=10)

    def setup_tts_tab(self) -> None:
        """Sets up the TTS settings tab."""
        tts_tab = self.settings_tabview.tab("TTS")
        
        # TTS frame
        tts_frame = ctk.CTkScrollableFrame(tts_tab)
        tts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # TTS Engine
        engine_label = ctk.CTkLabel(
            tts_frame,
            text="TTS Engine:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        engine_label.pack(anchor="w", pady=(10, 5))
        
        self.tts_engine_combo = ctk.CTkComboBox(
            tts_frame,
            values=["System (SAPI)", "OpenAI TTS", "Eleven Labs", "Local TTS"],
            width=300
        )
        self.tts_engine_combo.pack(anchor="w", padx=20, pady=5)
        
        # Voice selection
        voice_label = ctk.CTkLabel(
            tts_frame,
            text="Voice:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        voice_label.pack(anchor="w", pady=(20, 5))
        
        self.voice_combo = ctk.CTkComboBox(
            tts_frame,
            values=["Default", "Male Voice 1", "Female Voice 1", "Neural Voice"],
            width=300
        )
        self.voice_combo.pack(anchor="w", padx=20, pady=5)
        
        # Speech rate
        rate_label = ctk.CTkLabel(
            tts_frame,
            text="Speech Rate:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        rate_label.pack(anchor="w", pady=(20, 5))
        
        rate_frame = ctk.CTkFrame(tts_frame, fg_color="transparent")
        rate_frame.pack(fill="x", padx=20, pady=5)
        
        self.rate_slider = ctk.CTkSlider(
            rate_frame,
            from_=0.5,
            to=2.0,
            number_of_steps=15,
            command=self.on_rate_changed
        )
        self.rate_slider.pack(side="left", fill="x", expand=True)
        self.rate_slider.set(1.0)
        
        self.rate_label = ctk.CTkLabel(
            rate_frame,
            text="1.0x",
            font=ctk.CTkFont(size=12)
        )
        self.rate_label.pack(side="right", padx=10)
        
        # Auto-speak responses
        self.auto_speak_var = tk.BooleanVar(value=True)
        auto_speak_checkbox = ctk.CTkCheckBox(
            tts_frame,
            text="Automatically speak AI responses",
            variable=self.auto_speak_var
        )
        auto_speak_checkbox.pack(anchor="w", padx=20, pady=20)

    def setup_translation_tab(self) -> None:
        """Sets up the translation settings tab."""
        translation_tab = self.settings_tabview.tab("Translation")
        
        # Translation frame
        translation_frame = ctk.CTkScrollableFrame(translation_tab)
        translation_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Translation service
        service_label = ctk.CTkLabel(
            translation_frame,
            text="Translation Service:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        service_label.pack(anchor="w", pady=(10, 5))
        
        self.translation_service_combo = ctk.CTkComboBox(
            translation_frame,
            values=["Google Translate", "Microsoft Translator", "DeepL", "Local Model"],
            width=300
        )
        self.translation_service_combo.pack(anchor="w", padx=20, pady=5)
        
        # Source language
        source_label = ctk.CTkLabel(
            translation_frame,
            text="Source Language:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        source_label.pack(anchor="w", pady=(20, 5))
        
        self.source_lang_combo = ctk.CTkComboBox(
            translation_frame,
            values=["Auto-detect", "English", "Spanish", "French", "German", "Italian", "Portuguese"],
            width=300
        )
        self.source_lang_combo.pack(anchor="w", padx=20, pady=5)
        self.source_lang_combo.set("Auto-detect")
        
        # Target language
        target_label = ctk.CTkLabel(
            translation_frame,
            text="Target Language:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        target_label.pack(anchor="w", pady=(20, 5))
        
        self.target_lang_combo = ctk.CTkComboBox(
            translation_frame,
            values=["English", "Spanish", "French", "German", "Italian", "Portuguese"],
            width=300
        )
        self.target_lang_combo.pack(anchor="w", padx=20, pady=5)
        
        # Auto-translate
        self.auto_translate_var = tk.BooleanVar()
        auto_translate_checkbox = ctk.CTkCheckBox(
            translation_frame,
            text="Enable automatic translation",
            variable=self.auto_translate_var
        )
        auto_translate_checkbox.pack(anchor="w", padx=20, pady=20)

    def setup_avatar_tab(self) -> None:
        """Sets up the avatar settings tab."""
        avatar_tab = self.settings_tabview.tab("Avatar")
        
        # Avatar frame
        avatar_frame = ctk.CTkScrollableFrame(avatar_tab)
        avatar_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Avatar model
        model_label = ctk.CTkLabel(
            avatar_frame,
            text="Avatar Model:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        model_label.pack(anchor="w", pady=(10, 5))
        
        self.avatar_model_combo = ctk.CTkComboBox(
            avatar_frame,
            values=["Default Avatar", "Realistic Model", "Cartoon Style", "Custom Model"],
            width=300
        )
        self.avatar_model_combo.pack(anchor="w", padx=20, pady=5)
        
        # Quality settings
        quality_label = ctk.CTkLabel(
            avatar_frame,
            text="Rendering Quality:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        quality_label.pack(anchor="w", pady=(20, 5))
        
        self.quality_combo = ctk.CTkComboBox(
            avatar_frame,
            values=["Low", "Medium", "High", "Ultra"],
            width=200
        )
        self.quality_combo.pack(anchor="w", padx=20, pady=5)
        self.quality_combo.set("Medium")
        
        # Face sync sensitivity
        sensitivity_label = ctk.CTkLabel(
            avatar_frame,
            text="Face Sync Sensitivity:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        sensitivity_label.pack(anchor="w", pady=(20, 5))
        
        sensitivity_frame = ctk.CTkFrame(avatar_frame, fg_color="transparent")
        sensitivity_frame.pack(fill="x", padx=20, pady=5)
        
        self.sensitivity_slider = ctk.CTkSlider(
            sensitivity_frame,
            from_=0.1,
            to=1.0,
            number_of_steps=9,
            command=self.on_sensitivity_changed
        )
        self.sensitivity_slider.pack(side="left", fill="x", expand=True)
        self.sensitivity_slider.set(0.5)
        
        self.sensitivity_label = ctk.CTkLabel(
            sensitivity_frame,
            text="0.5",
            font=ctk.CTkFont(size=12)
        )
        self.sensitivity_label.pack(side="right", padx=10)
        
        # Enable options
        self.enable_face_sync_var = tk.BooleanVar(value=True)
        face_sync_checkbox = ctk.CTkCheckBox(
            avatar_frame,
            text="Enable real-time face sync",
            variable=self.enable_face_sync_var
        )
        face_sync_checkbox.pack(anchor="w", padx=20, pady=10)
        
        self.enable_gestures_var = tk.BooleanVar()
        gestures_checkbox = ctk.CTkCheckBox(
            avatar_frame,
            text="Enable hand gestures",
            variable=self.enable_gestures_var
        )
        gestures_checkbox.pack(anchor="w", padx=20, pady=5)

    def setup_general_tab(self) -> None:
        """Sets up the general settings tab."""
        general_tab = self.settings_tabview.tab("General")
        
        # General frame
        general_frame = ctk.CTkScrollableFrame(general_tab)
        general_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Appearance
        appearance_label = ctk.CTkLabel(
            general_frame,
            text="Appearance:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        appearance_label.pack(anchor="w", pady=(10, 5))
        
        self.theme_combo = ctk.CTkComboBox(
            general_frame,
            values=["System", "Dark", "Light"],
            width=200,
            command=self.on_theme_changed
        )
        self.theme_combo.pack(anchor="w", padx=20, pady=5)
        self.theme_combo.set("Dark")
        
        # Color theme
        color_label = ctk.CTkLabel(
            general_frame,
            text="Color Theme:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        color_label.pack(anchor="w", pady=(20, 5))
        
        self.color_theme_combo = ctk.CTkComboBox(
            general_frame,
            values=["Blue", "Green", "Dark Blue"],
            width=200,
            command=self.on_color_theme_changed
        )
        self.color_theme_combo.pack(anchor="w", padx=20, pady=5)
        self.color_theme_combo.set("Blue")
        
        # Startup options
        startup_label = ctk.CTkLabel(
            general_frame,
            text="Startup Options:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        startup_label.pack(anchor="w", pady=(20, 5))
        
        self.startup_minimized_var = tk.BooleanVar()
        minimized_checkbox = ctk.CTkCheckBox(
            general_frame,
            text="Start minimized to system tray",
            variable=self.startup_minimized_var
        )
        minimized_checkbox.pack(anchor="w", padx=20, pady=5)
        
        self.auto_start_var = tk.BooleanVar()
        auto_start_checkbox = ctk.CTkCheckBox(
            general_frame,
            text="Start with Windows",
            variable=self.auto_start_var
        )
        auto_start_checkbox.pack(anchor="w", padx=20, pady=5)
        
        # Logging level
        logging_label = ctk.CTkLabel(
            general_frame,
            text="Logging Level:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        logging_label.pack(anchor="w", pady=(20, 5))
        
        self.logging_combo = ctk.CTkComboBox(
            general_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            width=200
        )
        self.logging_combo.pack(anchor="w", padx=20, pady=5)
        self.logging_combo.set("INFO")

    def on_volume_changed(self, value: float) -> None:
        """Handles volume slider change."""
        volume = int(value)
        self.volume_label.configure(text=f"{volume}%")

    def on_rate_changed(self, value: float) -> None:
        """Handles speech rate slider change."""
        rate = round(value, 1)
        self.rate_label.configure(text=f"{rate}x")

    def on_sensitivity_changed(self, value: float) -> None:
        """Handles sensitivity slider change."""
        sensitivity = round(value, 1)
        self.sensitivity_label.configure(text=str(sensitivity))

    def on_theme_changed(self, choice: str) -> None:
        """Handles theme change."""
        ctk.set_appearance_mode(choice.lower())
        self.update_status(f"Theme changed to {choice}")

    def on_color_theme_changed(self, choice: str) -> None:
        """Handles color theme change."""
        ctk.set_default_color_theme(choice.lower().replace(" ", "-"))
        self.update_status(f"Color theme changed to {choice}")

    def load_settings(self) -> None:
        """Loads settings from configuration."""
        try:
            if CONFIG_AVAILABLE:
                config = get_config()
                # Load settings from config
                self.settings = config.get("desktop_settings", {})
            else:
                # Use default settings
                self.settings = self.get_default_settings()
            
            self.apply_settings()
            self.update_status("Settings loaded")
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self.settings = self.get_default_settings()
            self.apply_settings()

    def save_settings(self) -> None:
        """Saves current settings."""
        try:
            # Collect settings from UI
            self.collect_settings()
            
            # Save to file (placeholder implementation)
            settings_file = Path("data/desktop_settings.json")
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            self.update_status("Settings saved successfully")
            self.logger.info("Settings saved")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            self.update_status(f"Error saving settings: {e}")

    def restore_defaults(self) -> None:
        """Restores default settings."""
        # Show confirmation dialog
        if self._show_confirmation("Restore Settings", 
                                 "Are you sure you want to restore default settings?"):
            self.settings = self.get_default_settings()
            self.apply_settings()
            self.update_status("Settings restored to defaults")
            self.logger.info("Settings restored to defaults")

    def export_settings(self) -> None:
        """Exports settings to a file."""
        try:
            # In a real implementation, would use file dialog
            export_file = Path("talkbridge_settings_export.json")
            
            self.collect_settings()
            
            with open(export_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            self.update_status("Settings exported successfully")
            self.logger.info(f"Settings exported to {export_file}")
            
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            self.update_status(f"Error exporting settings: {e}")

    def import_settings(self) -> None:
        """Imports settings from a file."""
        # Placeholder implementation
        self.update_status("Import feature coming soon")

    def collect_settings(self) -> None:
        """Collects settings from UI elements."""
        self.settings = {
            "audio": {
                "input_device": self.input_device_combo.get(),
                "output_device": self.output_device_combo.get(),
                "sample_rate": int(self.sample_rate_combo.get()),
                "volume": int(self.volume_slider.get())
            },
            "tts": {
                "engine": self.tts_engine_combo.get(),
                "voice": self.voice_combo.get(),
                "rate": self.rate_slider.get(),
                "auto_speak": self.auto_speak_var.get()
            },
            "translation": {
                "service": self.translation_service_combo.get(),
                "source_lang": self.source_lang_combo.get(),
                "target_lang": self.target_lang_combo.get(),
                "auto_translate": self.auto_translate_var.get()
            },
            "avatar": {
                "model": self.avatar_model_combo.get(),
                "quality": self.quality_combo.get(),
                "sensitivity": self.sensitivity_slider.get(),
                "face_sync": self.enable_face_sync_var.get(),
                "gestures": self.enable_gestures_var.get()
            },
            "general": {
                "theme": self.theme_combo.get(),
                "color_theme": self.color_theme_combo.get(),
                "startup_minimized": self.startup_minimized_var.get(),
                "auto_start": self.auto_start_var.get(),
                "logging_level": self.logging_combo.get()
            }
        }

    def apply_settings(self) -> None:
        """Applies settings to UI elements."""
        try:
            # Audio settings
            audio = self.settings.get("audio", {})
            if "input_device" in audio:
                self.input_device_combo.set(audio["input_device"])
            if "volume" in audio:
                self.volume_slider.set(audio["volume"])
                self.on_volume_changed(audio["volume"])
            
            # TTS settings
            tts = self.settings.get("tts", {})
            if "auto_speak" in tts:
                self.auto_speak_var.set(tts["auto_speak"])
            if "rate" in tts:
                self.rate_slider.set(tts["rate"])
                self.on_rate_changed(tts["rate"])
            
            # Translation settings
            translation = self.settings.get("translation", {})
            if "auto_translate" in translation:
                self.auto_translate_var.set(translation["auto_translate"])
            
            # General settings
            general = self.settings.get("general", {})
            if "theme" in general:
                self.theme_combo.set(general["theme"])
                ctk.set_appearance_mode(general["theme"].lower())
            
        except Exception as e:
            self.logger.error(f"Error applying settings: {e}")

    def get_default_settings(self) -> Dict[str, Any]:
        """Gets default settings."""
        return {
            "audio": {
                "input_device": "Default",
                "output_device": "Default",
                "sample_rate": 16000,
                "volume": 80
            },
            "tts": {
                "engine": "System (SAPI)",
                "voice": "Default",
                "rate": 1.0,
                "auto_speak": True
            },
            "translation": {
                "service": "Google Translate",
                "source_lang": "Auto-detect",
                "target_lang": "English",
                "auto_translate": False
            },
            "avatar": {
                "model": "Default Avatar",
                "quality": "Medium",
                "sensitivity": 0.5,
                "face_sync": True,
                "gestures": False
            },
            "general": {
                "theme": "Dark",
                "color_theme": "Blue",
                "startup_minimized": False,
                "auto_start": False,
                "logging_level": "INFO"
            }
        }

    def update_status(self, status: str) -> None:
        """Updates the status label."""
        if self.status_label:
            self.status_label.configure(text=status)
            self.parent.update_idletasks()

    def _show_confirmation(self, title: str, message: str) -> bool:
        """Shows a confirmation dialog."""
        result = [False]
        
        # Create confirmation dialog
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (150 // 2)
        dialog.geometry(f"300x150+{x}+{y}")
        
        # Add content
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Message
        label = ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=12),
            wraplength=260
        )
        label.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        def on_yes():
            result[0] = True
            dialog.destroy()
        
        def on_no():
            result[0] = False
            dialog.destroy()
        
        yes_button = ctk.CTkButton(button_frame, text="Yes", width=80, command=on_yes)
        yes_button.pack(side="left", padx=10)
        
        no_button = ctk.CTkButton(button_frame, text="No", width=80, command=on_no)
        no_button.pack(side="left", padx=10)
        
        # Make modal
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.wait_window()
        
        return result[0]

    def get_current_settings(self) -> Dict[str, Any]:
        """Gets current settings."""
        self.collect_settings()
        return self.settings.copy()
