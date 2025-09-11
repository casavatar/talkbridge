#!/usr/bin/env python3
"""
TalkBridge Desktop - Chat Tab (CustomTkinter)
=============================================

Translated chat tab with voice input and spoken response.

Author: TalkBridge Team
Date: 2025-09-08
Version: 2.1

Requirements:
- customtkinter
- tkinter
======================================================================
"""

import logging
import os
import time
import threading
from typing import Optional, List
from pathlib import Path
import tkinter as tk
import customtkinter as ctk

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import logging utilities
try:
    from src.desktop.logging_config import get_logger, log_exception, add_error_context
    LOGGING_UTILS_AVAILABLE = True
except ImportError:
    LOGGING_UTILS_AVAILABLE = False

# Import UI utilities and theme
try:
    from src.desktop.ui.ui_utils import clean_text, icon, strip_variation_selectors
    from src.desktop.ui.theme import ComponentThemes, Typography, ColorPalette
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

# Import unified theme
try:
    from src.desktop.ui.theme import (
        ColorPalette, Typography, Spacing, Dimensions, 
        ComponentThemes, UIText, Icons, UXGuidelines
    )
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

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
    TRANSLATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Translation module not available: {e}")
    TRANSLATION_AVAILABLE = False

try:
    from src.ollama.ollama_client import OllamaClient
    OLLAMA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Ollama client not available: {e}")
    OLLAMA_AVAILABLE = False

try:
    from src.tts.synthesizer import TTSSynthesizer
    TTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: TTS synthesizer not available: {e}")
    TTS_AVAILABLE = False


class ChatTheme:
    """Enhanced dark theme for the CustomTkinter chat interface."""
    
    # Base dark theme colors
    BACKGROUND_MAIN = "#1e1e1e"
    BACKGROUND_SECONDARY = "#2d2d2d"
    BACKGROUND_ELEVATED = "#3c3c3c"
    
    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#cccccc"
    TEXT_MUTED = "#999999"
    
    # Accent colors
    ACCENT_BLUE = "#0078d4"
    ACCENT_BLUE_HOVER = "#106ebe"
    ACCENT_GREEN = "#4CAF50"
    ACCENT_ORANGE = "#FF9800"
    ACCENT_RED = "#f44336"
    
    # Message colors
    USER_MESSAGE_BG = "#0e3a5f"
    USER_MESSAGE_BORDER = "#1e5a8a"
    ASSISTANT_MESSAGE_BG = "#2d1b3d"
    ASSISTANT_MESSAGE_BORDER = "#4a2c5a"
    
    # UI element colors
    INPUT_BACKGROUND = "#3c3c3c"
    INPUT_BORDER = "#555555"
    INPUT_BORDER_FOCUS = "#0078d4"
    BORDER_SUBTLE = "#4a4a4a"


class AudioVisualizer:
    """Visual representation of audio levels during recording."""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.bars = []
        self.max_bars = 20
        self.animation_running = False
        
    def start_animation(self):
        """Start the audio visualization animation."""
        self.animation_running = True
        self.animate_bars()
        
    def stop_animation(self):
        """Stop the audio visualization animation."""
        self.animation_running = False
        self.canvas.delete("audio_bar")
        
    def animate_bars(self):
        """Animate audio level bars."""
        if not self.animation_running:
            return
            
        import random
        
        self.canvas.delete("audio_bar")
        
        # Draw audio level bars
        bar_width = 15
        bar_spacing = 20
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            start_x = (canvas_width - (self.max_bars * bar_spacing)) // 2
            
            for i in range(self.max_bars):
                x = start_x + (i * bar_spacing)
                # Random height for animation effect
                bar_height = random.randint(10, canvas_height - 20)
                y = (canvas_height - bar_height) // 2
                
                # Color based on height
                color = "#4CAF50" if bar_height > canvas_height * 0.6 else "#FFA726"
                
                self.canvas.create_rectangle(
                    x, y, x + bar_width, y + bar_height,
                    fill=color, outline="", tags="audio_bar"
                )
        
        # Schedule next frame
        if self.animation_running:
            self.canvas.after(100, self.animate_bars)


class MessageWidget:
    """Enhanced message widget with rich formatting and animations."""
    
    def __init__(self, parent, text: str, is_user: bool = True, translation: str = None, timestamp: str = None):
        self.parent = parent
        self.text = text
        self.is_user = is_user
        self.translation = translation
        self.timestamp = timestamp
        
        # Create main frame with proper styling
        self.setup_message_frame()
        
    def setup_message_frame(self):
        """Create and style the message frame."""
        # Message container
        message_container = ctk.CTkFrame(self.parent)
        message_container.pack(fill="x", padx=10, pady=5)
        
        # Configure colors based on message type
        if self.is_user:
            bg_color = ChatTheme.USER_MESSAGE_BG
            border_color = ChatTheme.USER_MESSAGE_BORDER
            align = "e"
            sender_text = "You" if THEME_AVAILABLE else "You"
            sender_color = "#87CEEB"
        else:
            bg_color = ChatTheme.ASSISTANT_MESSAGE_BG
            border_color = ChatTheme.ASSISTANT_MESSAGE_BORDER
            align = "w"
            sender_text = "Assistant" if THEME_AVAILABLE else "Assistant"
            sender_color = "#DDA0DD"
        
        # Inner frame for message content
        inner_frame = ctk.CTkFrame(
            message_container,
            fg_color=bg_color,
            border_color=border_color,
            border_width=2,
            corner_radius=Dimensions.RADIUS_MD
        )
        inner_frame.pack(fill="x", padx=5, pady=5)
        
        # Header with sender and timestamp
        header_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        sender_label = ctk.CTkLabel(
            header_frame,
            text=sender_text,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY, Typography.FONT_WEIGHT_BOLD),
            text_color=sender_color
        )
        sender_label.pack(side="left")
        
        if self.timestamp:
            time_label = ctk.CTkLabel(
                header_frame,
                text=self.timestamp,
                font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
                text_color=ChatTheme.TEXT_MUTED
            )
            time_label.pack(side="right")
        
        # Message text
        message_text = ctk.CTkTextbox(
            inner_frame,
            height=60,
            wrap="word",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY),
            fg_color="transparent",
            scrollbar_button_color=border_color
        )
        message_text.pack(fill="both", expand=True, padx=10, pady=5)
        message_text.insert("1.0", strip_variation_selectors(self.text))
        message_text.configure(state="disabled")
        
        # Translation if available
        if self.translation and self.translation != self.text:
            translation_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
            translation_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            translation_label = ctk.CTkLabel(
                translation_frame,
                text="Translation:",
                image=icon("globe"),
                compound="left",
                font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION, Typography.FONT_WEIGHT_BOLD),
                text_color=ChatTheme.TEXT_MUTED
            )
            translation_label.pack(anchor="w")
            
            translation_text = ctk.CTkLabel(
                translation_frame,
                text=strip_variation_selectors(self.translation),
                font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION, "italic"),
                text_color=ChatTheme.TEXT_SECONDARY,
                wraplength=400,
                justify="left"
            )
            translation_text.pack(anchor="w", pady=(2, 0))


class ChatMessage:
    """Individual chat message widget with CustomTkinter styling."""
    
    def __init__(self, parent, text: str, is_user: bool = True, translation: str = None):
        self.parent = parent
        self.text = text
        self.is_user = is_user
        self.translation = translation
        
        # Create message frame
        self.frame = ctk.CTkFrame(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the message UI with proper styling."""
        # Configure colors based on message type
        if self.is_user:
            self.frame.configure(fg_color="#1e3a5f", border_color="#1e5a8a", border_width=2)
        else:
            self.frame.configure(fg_color="#2d1b3d", border_color="#4a2c5a", border_width=2)
        
        # Message text
        message_label = ctk.CTkLabel(
            self.frame,
            text=self.text,
            wraplength=400,
            justify="left",
            font=ctk.CTkFont(size=12)
        )
        message_label.pack(padx=10, pady=5, anchor="w")
        
        # Translation if available
        if self.translation and self.translation != self.text:
            translation_label = ctk.CTkLabel(
                self.frame,
                text=f"Translation: {self.translation}",
                wraplength=400,
                justify="left",
                font=ctk.CTkFont(size=10, slant="italic"),
                text_color="gray"
            )
            translation_label.pack(padx=10, pady=(0, 5), anchor="w")


class ChatTab:
    """
    Enhanced chat interface tab with CustomTkinter.
    
    Features:
    - Voice input with speech-to-text and visual feedback
    - AI conversation via Ollama with rich message display
    - Text-to-speech output with progress indicators
    - Real-time translation with language selection
    - Rich message history with timestamps
    - Audio visualization during recording
    - Comprehensive controls and settings
    """

    def __init__(self, parent, state_manager=None, core_bridge=None):
        """Initialize the enhanced chat tab."""
        self.parent = parent
        self.state_manager = state_manager
        self.core_bridge = core_bridge
        # Logger with enhanced error handling
        self.logger = logging.getLogger("talkbridge.desktop.chat")
        
        # Add error context for better debugging
        if LOGGING_UTILS_AVAILABLE:
            add_error_context(self.logger, "ChatTab")
        
        # Backend components
        self.audio_capture: Optional[AudioCapture] = None
        self.whisper_engine: Optional[WhisperEngine] = None
        self.translator: Optional[Translator] = None
        self.ollama_client: Optional[OllamaClient] = None
        self.tts_synthesizer: Optional[TTSSynthesizer] = None
        
        # UI elements
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.chat_scrollable: Optional[ctk.CTkScrollableFrame] = None
        self.input_entry: Optional[ctk.CTkEntry] = None
        self.send_button: Optional[ctk.CTkButton] = None
        self.voice_button: Optional[ctk.CTkButton] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.language_combo: Optional[ctk.CTkComboBox] = None
        self.tts_engine_display: Optional[ctk.CTkLabel] = None
        self.translation_service_display: Optional[ctk.CTkLabel] = None
        self.recording_canvas: Optional[tk.Canvas] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None
        
        # Visual components
        self.audio_visualizer: Optional[AudioVisualizer] = None
        self.message_widgets = []
        
        # State variables
        self.recording = False
        self.processing = False
        self.conversation_history = []
        self.current_language = "en"
        self.current_model = "llama3.2:3b"
        self.auto_scroll = True
        
        # Settings
        self.voice_enabled = True
        self.translation_enabled = True
        self.tts_enabled = True
        self.show_timestamps = True
        
        # State
        self.is_recording = False
        self.is_processing = False
        self.conversation_history = []
        
        # Callbacks
        self.error_occurred_callback = None
        
        # Setup UI
        self.setup_ui()
        self.initialize_components()

    def setup_ui(self) -> None:
        """Set up the enhanced chat interface with comprehensive visual elements."""
        self.logger.info("Setting up enhanced chat tab UI")
        
        # Main frame with theme colors
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=ChatTheme.BACKGROUND_MAIN)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title with enhanced styling
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=clean_text("AI Chat with Translation & Voice") if THEME_AVAILABLE else "AI Chat with Translation & Voice",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=20, weight="bold"), "text_color": ChatTheme.TEXT_PRIMARY}
        )
        title_label.pack(side="left")
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            title_frame,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=ChatTheme.ACCENT_GREEN
        )
        self.status_indicator.pack(side="right", padx=10)
        
        # Control panel with comprehensive options
        control_panel = ctk.CTkFrame(self.main_frame, fg_color=ChatTheme.BACKGROUND_SECONDARY)
        control_panel.pack(fill="x", padx=10, pady=5)
        
        # Language and model selection
        settings_row1 = ctk.CTkFrame(control_panel, fg_color="transparent")
        settings_row1.pack(fill="x", padx=10, pady=10)
        
        # Language selection
        lang_label = ctk.CTkLabel(
            settings_row1,
            text=clean_text("Language:") if THEME_AVAILABLE else "Language:",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=12, weight="bold"), "text_color": ChatTheme.TEXT_PRIMARY}
        )
        lang_label.pack(side="left", padx=(0, 10))
        
        self.language_combo = ctk.CTkComboBox(
            settings_row1,
            values=["English (en)", "Spanish (es)", "French (fr)", "German (de)", 
                   "Italian (it)", "Portuguese (pt)", "Russian (ru)", "Chinese (zh)", 
                   "Japanese (ja)", "Korean (ko)"],
            width=150,
            command=self.on_language_changed,
            **ComponentThemes.get_combobox_theme() if THEME_AVAILABLE else {"fg_color": ChatTheme.INPUT_BACKGROUND, "border_color": ChatTheme.INPUT_BORDER}
        )
        self.language_combo.set("English (en)")
        self.language_combo.pack(side="left", padx=5)
        
        # TTS Engine Status (read-only)
        tts_label = ctk.CTkLabel(
            settings_row1,
            text=clean_text("TTS:") if THEME_AVAILABLE else "TTS:",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=12, weight="bold"), "text_color": ChatTheme.TEXT_PRIMARY}
        )
        tts_label.pack(side="left", padx=(20, 10))
        
        self.tts_engine_display = ctk.CTkLabel(
            settings_row1,
            text="System (SAPI)",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=12), "text_color": ChatTheme.TEXT_SECONDARY}
        )
        self.tts_engine_display.pack(side="left", padx=5)
        
        # Translation Service Status (read-only)
        translation_label = ctk.CTkLabel(
            settings_row1,
            text=clean_text("Translation:") if THEME_AVAILABLE else "Translation:",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=12, weight="bold"), "text_color": ChatTheme.TEXT_PRIMARY}
        )
        translation_label.pack(side="left", padx=(20, 10))
        
        self.translation_service_display = ctk.CTkLabel(
            settings_row1,
            text="Google Translate",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=12), "text_color": ChatTheme.TEXT_SECONDARY}
        )
        self.translation_service_display.pack(side="left", padx=5)
        
        # Toggle switches for features
        settings_row2 = ctk.CTkFrame(control_panel, fg_color="transparent")
        settings_row2.pack(fill="x", padx=10, pady=(0, 10))
        
        # Voice toggle
        self.voice_switch = ctk.CTkSwitch(
            settings_row2,
            text=clean_text("Voice Input") if THEME_AVAILABLE else "Voice Input",
            command=self.toggle_voice_feature,
            fg_color=ChatTheme.ACCENT_GREEN
        )
        self.voice_switch.pack(side="left", padx=5)
        
        # Translation toggle
        self.translation_switch = ctk.CTkSwitch(
            settings_row2,
            text=clean_text("Translation") if THEME_AVAILABLE else "Translation",
            command=self.toggle_translation_feature,
            fg_color=ChatTheme.ACCENT_BLUE
        )
        self.translation_switch.pack(side="left", padx=15)
        
        # TTS toggle
        self.tts_switch = ctk.CTkSwitch(
            settings_row2,
            text=clean_text("Text-to-Speech") if THEME_AVAILABLE else "Text-to-Speech",
            command=self.toggle_tts_feature,
            fg_color=ChatTheme.ACCENT_ORANGE
        )
        self.tts_switch.pack(side="left", padx=15)
        
        # Clear and export buttons
        button_frame = ctk.CTkFrame(settings_row2, fg_color="transparent")
        button_frame.pack(side="right", padx=10)
        
        export_button = ctk.CTkButton(
            button_frame,
            text=clean_text("Export") if THEME_AVAILABLE else "Export",
            width=80,
            command=self.export_conversation,
            **ComponentThemes.get_button_theme() if THEME_AVAILABLE else {"fg_color": ChatTheme.ACCENT_BLUE, "hover_color": ChatTheme.ACCENT_BLUE_HOVER}
        )
        export_button.pack(side="right", padx=5)
        
        clear_button = ctk.CTkButton(
            button_frame,
            text=clean_text("Clear") if THEME_AVAILABLE else "Clear",
            width=80,
            command=self.clear_chat,
            **ComponentThemes.get_button_theme() if THEME_AVAILABLE else {"fg_color": ChatTheme.ACCENT_RED, "hover_color": "#c62828"}
        )
        clear_button.pack(side="right", padx=5)
        
        # Chat display area with enhanced scrolling
        chat_frame = ctk.CTkFrame(self.main_frame, fg_color=ChatTheme.BACKGROUND_SECONDARY)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        chat_header = ctk.CTkFrame(chat_frame, fg_color="transparent")
        chat_header.pack(fill="x", padx=10, pady=(10, 5))
        
        chat_title = ctk.CTkLabel(
            chat_header,
            text=clean_text("Conversation") if THEME_AVAILABLE else "Conversation",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=16, weight="bold"), "text_color": ChatTheme.TEXT_PRIMARY}
        )
        chat_title.pack(side="left")
        
        # Auto-scroll toggle
        self.auto_scroll_switch = ctk.CTkSwitch(
            chat_header,
            text="Auto-scroll",
            command=self.toggle_auto_scroll,
            fg_color=ChatTheme.ACCENT_GREEN
        )
        self.auto_scroll_switch.pack(side="right")
        self.auto_scroll_switch.select()  # Enable by default
        
        # Scrollable message area
        self.chat_scrollable = ctk.CTkScrollableFrame(
            chat_frame,
            height=350,
            fg_color=ChatTheme.BACKGROUND_MAIN,
            scrollbar_button_color=ChatTheme.ACCENT_BLUE
        )
        self.chat_scrollable.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Input area with enhanced controls
        input_main_frame = ctk.CTkFrame(self.main_frame, fg_color=ChatTheme.BACKGROUND_SECONDARY)
        input_main_frame.pack(fill="x", padx=10, pady=5)
        
        # Recording visualization area
        recording_frame = ctk.CTkFrame(input_main_frame, fg_color="transparent")
        recording_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.recording_canvas = tk.Canvas(
            recording_frame,
            height=Dimensions.HEIGHT_BUTTON,
            bg=ChatTheme.BACKGROUND_MAIN,
            highlightthickness=0
        )
        self.recording_canvas.pack(fill="x", pady=5)
        
        # Initialize audio visualizer
        self.audio_visualizer = AudioVisualizer(self.recording_canvas)
        
        # Input controls
        input_frame = ctk.CTkFrame(input_main_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Voice recording button with enhanced styling
        voice_theme = ComponentThemes.get_button_theme() if THEME_AVAILABLE else {"fg_color": ChatTheme.ACCENT_GREEN, "hover_color": "#45a049", "font": ctk.CTkFont(size=16)}
        voice_theme["height"] = 40  # Override height to ensure consistent sizing
        self.voice_button = ctk.CTkButton(
            input_frame,
            text=clean_text("Mic") if THEME_AVAILABLE else "Mic",
            width=50,
            command=self.toggle_voice_input,
            **voice_theme
        )
        self.voice_button.pack(side="left", padx=(0, 10))
        
        # Text input with enhanced styling
        input_theme = ComponentThemes.get_input_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=12), "fg_color": ChatTheme.INPUT_BACKGROUND, "border_color": ChatTheme.INPUT_BORDER}
        input_theme["height"] = 40  # Override height to ensure consistent sizing
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=clean_text("Type your message or use voice input... (Press Enter to send)") if THEME_AVAILABLE else "Type your message or use voice input... (Press Enter to send)",
            **input_theme
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.input_entry.bind("<Return>", lambda e: self.send_message())
        self.input_entry.bind("<FocusIn>", self.on_input_focus)
        self.input_entry.bind("<FocusOut>", self.on_input_unfocus)
        
        # Send button with enhanced styling
        send_theme = ComponentThemes.get_button_theme() if THEME_AVAILABLE else {"fg_color": ChatTheme.ACCENT_BLUE, "hover_color": ChatTheme.ACCENT_BLUE_HOVER, "font": ctk.CTkFont(size=12, weight="bold")}
        send_theme["height"] = 40  # Override height to ensure consistent sizing
        self.send_button = ctk.CTkButton(
            input_frame,
            text=clean_text("Send") if THEME_AVAILABLE else "Send",
            width=100,
            command=self.send_message,
            **send_theme
        )
        self.send_button.pack(side="right", padx=(10, 0))
        
        # Progress bar for processing indication (hidden by default)
        self.progress_bar = ctk.CTkProgressBar(
            input_main_frame,
            width=400,
            height=8,
            progress_color=ChatTheme.ACCENT_BLUE
        )
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide by default
        
        # Status bar with enhanced information and improved visibility
        status_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color=ChatTheme.BACKGROUND_ELEVATED, 
            height=50,
            corner_radius=Dimensions.RADIUS_MD,
            border_width=1,
            border_color=ChatTheme.BORDER_SUBTLE
        )
        status_frame.pack(fill="x", padx=10, pady=(5, 10))
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to chat",
            height=36,
            font=(Typography.FONT_FAMILY_PRIMARY, 13, Typography.FONT_WEIGHT_REGULAR),
            text_color=ChatTheme.TEXT_PRIMARY
        )
        self.status_label.pack(side="left", padx=12, pady=8)
        
        # Message count indicator
        self.message_count_label = ctk.CTkLabel(
            status_frame,
            text="Messages: 0",
            **ComponentThemes.get_label_theme() if THEME_AVAILABLE else {"font": ctk.CTkFont(size=10), "text_color": ChatTheme.TEXT_MUTED}
        )
        self.message_count_label.pack(side="right", padx=10, pady=8)
        
        # Initialize components
        self.initialize_components()
        
        self.logger.info("Enhanced chat tab UI setup completed")

    def on_language_changed(self, value: str) -> None:
        """Handle language selection change."""
        # Extract language code from display value
        self.current_language = value.split("(")[1].replace(")", "") if "(" in value else "en"
        self.logger.info(f"Language changed to: {self.current_language}")
        self.update_status(f"Language set to {value}")

    def on_model_changed(self, value: str) -> None:
        """Handle AI model selection change."""
        self.current_model = value
        self.logger.info(f"AI model changed to: {value}")
        self.update_status(f"AI model set to {value}")
    
    def update_engine_displays(self, tts_engine: str = None, translation_service: str = None):
        """Update the engine display labels from settings."""
        if tts_engine and self.tts_engine_display:
            self.tts_engine_display.configure(text=tts_engine)
            self.logger.info(f"TTS engine display updated to: {tts_engine}")
        
        if translation_service and self.translation_service_display:
            self.translation_service_display.configure(text=translation_service)
            self.logger.info(f"Translation service display updated to: {translation_service}")
    
    def get_engine_settings_from_state(self):
        """Load current engine settings from state manager."""
        if self.state_manager:
            try:
                # Check for updated engine settings
                current_engines = self.state_manager.get_setting("current_engines", {})
                if current_engines:
                    tts_engine = current_engines.get("tts_engine", "System (SAPI)")
                    translation_service = current_engines.get("translation_service", "Google Translate")
                else:
                    # Fallback to engines settings
                    settings = self.state_manager.get_setting("engines", {})
                    tts_engine = settings.get("tts_engine", "System (SAPI)")
                    translation_service = settings.get("translation_service", "Google Translate")
                
                self.update_engine_displays(tts_engine, translation_service)
            except Exception as e:
                self.logger.error(f"Failed to load engine settings: {e}")
                # Set defaults
                self.update_engine_displays("System (SAPI)", "Google Translate")
    
    def refresh_engine_displays(self):
        """Refresh engine displays from current state - can be called periodically."""
        self.get_engine_settings_from_state()

    def toggle_voice_feature(self) -> None:
        """Toggle voice input feature."""
        self.voice_enabled = self.voice_switch.get()
        status = "enabled" if self.voice_enabled else "disabled"
        self.logger.info(f"Voice input {status}")
        self.update_status(f"Voice input {status}")

    def toggle_translation_feature(self) -> None:
        """Toggle translation feature."""
        self.translation_enabled = self.translation_switch.get()
        status = "enabled" if self.translation_enabled else "disabled"
        self.logger.info(f"Translation {status}")
        self.update_status(f"Translation {status}")

    def toggle_tts_feature(self) -> None:
        """Toggle text-to-speech feature."""
        self.tts_enabled = self.tts_switch.get()
        status = "enabled" if self.tts_enabled else "disabled"
        self.logger.info(f"Text-to-speech {status}")
        self.update_status(f"Text-to-speech {status}")

    def toggle_auto_scroll(self) -> None:
        """Toggle auto-scroll feature."""
        self.auto_scroll = self.auto_scroll_switch.get()
        status = "enabled" if self.auto_scroll else "disabled"
        self.logger.info(f"Auto-scroll {status}")

    def on_input_focus(self, event) -> None:
        """Handle input field focus."""
        self.input_entry.configure(border_color=ChatTheme.INPUT_BORDER_FOCUS)

    def on_input_unfocus(self, event) -> None:
        """Handle input field unfocus."""
        self.input_entry.configure(border_color=ChatTheme.INPUT_BORDER)

    def export_conversation(self) -> None:
        """Export conversation to file."""
        try:
            import json
            from datetime import datetime
            from tkinter import filedialog
            
            if not self.conversation_history:
                self.update_status("No conversation to export")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Conversation"
            )
            
            if filename:
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "language": self.current_language,
                    "model": self.current_model,
                    "conversation": self.conversation_history
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self.update_status(f"Conversation exported to {filename}")
                self.logger.info(f"Conversation exported to {filename}")
        
        except Exception as e:
            self.logger.exception("Failed to export conversation:")
            self.update_status(f"Export failed: {e}")

    def update_progress(self, value: float) -> None:
        """Update progress bar."""
        if self.progress_bar:
            self.progress_bar.set(value)

    def show_progress_bar(self) -> None:
        """Show and reset the progress bar."""
        if self.progress_bar:
            self.progress_bar.set(0)
            self.progress_bar.pack(pady=(0, 10))

    def hide_progress_bar(self) -> None:
        """Hide the progress bar."""
        if self.progress_bar:
            self.progress_bar.pack_forget()

    def animate_progress(self, duration: int = 3000) -> None:
        """Animate progress bar over specified duration in milliseconds."""
        if not self.progress_bar:
            return
            
        self.show_progress_bar()
        steps = 100
        interval = duration // steps
        
        def update_step(step: int):
            if step <= steps and self.progress_bar:
                progress_value = step / steps
                self.progress_bar.set(progress_value)
                if step < steps:
                    # Schedule next update
                    self.main_frame.after(interval, lambda: update_step(step + 1))
                else:
                    # Animation complete, hide progress bar
                    self.main_frame.after(500, self.hide_progress_bar)
        
        update_step(0)

    def start_processing_animation(self) -> None:
        """Start processing animation."""
        self.processing = True
        self.update_progress(0.3)
        self.status_indicator.configure(text_color=ChatTheme.ACCENT_ORANGE)
        
    def stop_processing_animation(self) -> None:
        """Stop processing animation."""
        self.processing = False
        self.update_progress(0)
        self.status_indicator.configure(text_color=ChatTheme.ACCENT_GREEN)
        
        # Bind Enter key to send message
        self.input_entry.bind("<Return>", lambda e: self.send_message())
        
        # Add welcome message
        self.add_message("System", "Welcome to TalkBridge Chat! You can type messages or use voice input.", "system")

    def initialize_components(self) -> None:
        """Initialize backend components with robust error handling."""
        self.logger.info("Initializing chat components")
        
        try:
            # Initialize Audio Capture with validation
            if AUDIO_AVAILABLE:
                try:
                    self.audio_capture = AudioCapture()
                    # Validate that required methods are available
                    if not hasattr(self.audio_capture, 'record_chunk'):
                        self.logger.warning("AudioCapture missing record_chunk method - voice recording may not work")
                    else:
                        self.logger.debug("AudioCapture record_chunk method available")
                    self.logger.info("Audio capture initialized")
                except Exception as audio_error:
                    if LOGGING_UTILS_AVAILABLE:
                        log_exception(self.logger, audio_error, "Audio capture initialization")
                    else:
                        self.logger.error(f"Audio capture initialization failed: {audio_error}", exc_info=True)
                    self.audio_capture = None
            else:
                self.logger.warning("Audio module not available - voice features disabled")
                self.audio_capture = None
            
            # Initialize Whisper Engine with validation
            if WHISPER_AVAILABLE:
                try:
                    self.whisper_engine = WhisperEngine()
                    self.logger.info("Whisper engine initialized")
                except Exception as whisper_error:
                    self.logger.error(f"Whisper engine initialization failed: {whisper_error}")
                    self.whisper_engine = None
            
            # Initialize Translator with validation
            if TRANSLATION_AVAILABLE:
                try:
                    self.translator = Translator()
                    self.logger.info("Translator initialized")
                except KeyError as config_error:
                    self.logger.warning(f"Translator config missing: {config_error} - translation features disabled")
                    self.translator = None
                except Exception as translation_error:
                    self.logger.error(f"Translator initialization failed: {translation_error}")
                    self.translator = None
            else:
                self.logger.warning("Translation module not available - translation features disabled")
                self.translator = None
            
            # Initialize Ollama Client with enhanced error handling
            if OLLAMA_AVAILABLE:
                try:
                    # Check if Ollama server is accessible before initializing
                    self.ollama_client = OllamaClient()
                    
                    # Test connection to Ollama server
                    if hasattr(self.ollama_client, 'test_connection'):
                        if not self.ollama_client.test_connection():
                            self.logger.warning("Ollama server not accessible - chat functionality limited")
                            self.ollama_client = None
                        else:
                            self.logger.info("Ollama client initialized and connected")
                    else:
                        # If no test_connection method, assume it's working
                        self.logger.info("Ollama client initialized")
                        
                except Exception as ollama_error:
                    if LOGGING_UTILS_AVAILABLE:
                        log_exception(self.logger, ollama_error, "Ollama client initialization")
                    else:
                        self.logger.error(f"Ollama client initialization failed: {ollama_error}", exc_info=True)
                    self.logger.info("Continuing without Ollama - AI chat features will be disabled")
                    self.ollama_client = None
            else:
                self.logger.info("Ollama not available - AI chat features will be disabled")
            
            # Initialize TTS Synthesizer with validation
            if TTS_AVAILABLE:
                try:
                    self.tts_synthesizer = TTSSynthesizer()
                    self.logger.info("TTS synthesizer initialized")
                except Exception as tts_error:
                    self.logger.error(f"TTS synthesizer initialization failed: {tts_error}")
                    self.tts_synthesizer = None
            
            # Log initialization summary
            components = []
            if self.audio_capture: components.append("Audio")
            if self.whisper_engine: components.append("Speech-to-Text")
            if self.translator: components.append("Translation")
            if self.ollama_client: components.append("AI Chat")
            if self.tts_synthesizer: components.append("Text-to-Speech")
            
            self.logger.info(f"Chat components initialized: {', '.join(components) if components else 'None'}")
            
            # Load engine settings from state manager
            self.get_engine_settings_from_state()
            
        except Exception as e:
            if LOGGING_UTILS_AVAILABLE:
                log_exception(self.logger, e, "Chat component initialization")
            else:
                self.logger.exception("Error initializing components:")
            if self.error_occurred_callback:
                self.error_occurred_callback(f"Component initialization error: {e}")
            # Continue with partial initialization rather than failing completely

    def send_message(self) -> None:
        """Sends a text message."""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        # Clear input
        self.input_entry.delete(0, tk.END)
        
        # Add user message to chat
        self.add_message("You", message, "user")
        
        # Process message in background
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()

    def _process_message(self, message: str) -> None:
        """Processes a message through the AI pipeline."""
        try:
            self.update_status("Processing message...")
            # Start progress bar animation for message processing
            self.animate_progress(duration=4000)
            
            # Get AI response
            if self.ollama_client:
                try:
                    # Get model from settings instead of combo box
                    model = self.current_model or "llama3.2:3b"
                    
                    # Format message for Ollama chat API
                    messages = [{"role": "user", "content": message}]
                    response = self.ollama_client.chat(model, messages)
                    
                    # Handle different response formats
                    if isinstance(response, dict):
                        ai_response = response.get("response", response.get("content", "Sorry, I couldn't process that."))
                    elif isinstance(response, str):
                        ai_response = response
                    else:
                        ai_response = "Sorry, I couldn't process that."
                        
                except Exception as e:
                    self.logger.exception("Ollama error:")
                    ai_response = "I'm having trouble connecting to the AI service."
            else:
                ai_response = "AI service is not available."
            
            # Add AI response to chat
            self.add_message("AI", ai_response, "assistant")
            
            # Text-to-speech if available
            if self.tts_synthesizer:
                try:
                    self.update_status("Generating speech...")
                    # Generate and play TTS in background
                    threading.Thread(target=self._play_tts, args=(ai_response,), daemon=True).start()
                except Exception as e:
                    self.logger.exception("TTS error:")
            
            self.update_status("Ready")
            # Hide progress bar when processing completes
            self.hide_progress_bar()
            
        except Exception as e:
            self.logger.exception("Error processing message:")
            self.add_message("System", f"Error processing message: {e}", "error")
            self.update_status("Error")
            # Hide progress bar on error
            self.hide_progress_bar()

    def _play_tts(self, text: str) -> None:
        """Plays text-to-speech in background."""
        try:
            if self.tts_synthesizer:
                audio_data = self.tts_synthesizer.synthesize(text)
                if audio_data:
                    # Play audio (implementation depends on TTS backend)
                    pass
        except Exception as e:
            self.logger.exception("TTS playback error:")

    def toggle_voice_input(self) -> None:
        """Toggles voice recording."""
        if self.is_recording:
            self.stop_voice_input()
        else:
            self.start_voice_input()

    def start_voice_input(self) -> None:
        """Starts voice recording."""
        if not AUDIO_AVAILABLE or not self.audio_capture:
            self.update_status("Audio capture not available")
            return
        
        self.is_recording = True
        self.voice_button.configure(text="🔴 Stop", fg_color="red", hover_color="darkred")
        self.update_status("Recording... Click Stop when finished")
        
        # Start recording in background thread
        threading.Thread(target=self._record_voice, daemon=True).start()

    def stop_voice_input(self) -> None:
        """Stops voice recording."""
        self.is_recording = False
        self.voice_button.configure(text="🎤 Voice", fg_color="green", hover_color="darkgreen")
        self.update_status("Processing voice input...")
        # Start progress bar animation for voice processing
        self.animate_progress(duration=3000)

    def _record_voice(self) -> None:
        """Records voice input in background thread with robust error handling."""
        try:
            # Validate preconditions
            if not self.audio_capture:
                self.logger.warning("Audio capture not available")
                self.update_status("Audio capture not available")
                self.is_recording = False
                return
            
            # Initialize audio data list
            audio_data = []
            sample_rate = 16000
            chunk_duration = 0.1
            
            # Check if record_chunk method exists
            if not hasattr(self.audio_capture, 'record_chunk'):
                self.logger.error("AudioCapture missing record_chunk method - using fallback recording")
                self.update_status("Using fallback audio recording")
                # Try to use alternative recording method
                if hasattr(self.audio_capture, 'record_fixed_duration'):
                    try:
                        # Use fixed duration recording as fallback
                        while self.is_recording:
                            chunk = self.audio_capture.record_fixed_duration(chunk_duration)
                            if chunk is not None and len(chunk) > 0:
                                audio_data.append(chunk)
                            time.sleep(0.05)  # Small delay between chunks
                    except Exception as fallback_error:
                        self.logger.error(f"Fallback recording failed: {fallback_error}")
                        self.update_status("Audio recording failed")
                else:
                    self.logger.error("No viable audio recording method available")
                    self.update_status("Audio recording not available")
                self.is_recording = False
                return
            
            # Record audio while recording flag is True
            
            self.logger.info(f"Starting voice recording with sample_rate={sample_rate}")
            
            while self.is_recording:
                try:
                    # Record small chunks with timeout protection
                    chunk = self.audio_capture.record_chunk(
                        duration=chunk_duration, 
                        sample_rate=sample_rate
                    )
                    
                    if chunk is not None and len(chunk) > 0:
                        audio_data.append(chunk)
                    else:
                        self.logger.warning("Received empty audio chunk")
                        
                except Exception as chunk_error:
                    self.logger.warning(f"Audio chunk recording failed: {chunk_error}")
                    # Continue recording despite chunk errors
                    
                time.sleep(chunk_duration)  # Prevent CPU overload
            
            # Process recorded audio if available
            if audio_data:
                try:
                    # Combine audio chunks
                    import numpy as np
                    full_audio = np.concatenate(audio_data)
                    self.logger.info(f"Recorded {len(full_audio)} audio samples")
                    
                    # Process with speech-to-text
                    self._process_voice_input(full_audio, sample_rate)
                    
                except Exception as processing_error:
                    self.logger.error(f"Audio processing failed: {processing_error}")
                    self.update_status("Audio processing failed")
            else:
                self.logger.warning("No audio data recorded")
                self.update_status("No audio data captured")
            
        except Exception as e:
            if LOGGING_UTILS_AVAILABLE:
                log_exception(self.logger, e, "Voice recording")
            else:
                self.logger.exception("Voice recording error:")
            self.update_status("Voice recording failed")
        finally:
            self.is_recording = False
            self.voice_button.configure(text="🎤 Voice", fg_color="green", hover_color="darkgreen")
            # Ensure progress bar is hidden if recording fails
            self.hide_progress_bar()

    def _process_voice_input(self, audio_data, sample_rate: int) -> None:
        """Processes recorded voice input."""
        try:
            self.update_status("Converting speech to text...")
            
            if not WHISPER_AVAILABLE or not self.whisper_engine:
                self.update_status("Speech recognition not available")
                self.hide_progress_bar()  # Hide progress bar on error
                return
            
            # Convert speech to text using numpy array
            text = self.whisper_engine.transcribe_numpy(audio_data, sample_rate)
            
            if text and text.strip():
                # Set text in input field
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, text.strip())
                
                # Automatically send the message
                self.send_message()
                self.update_status("Message sent")
            else:
                self.update_status("No speech detected")
            
            # Hide progress bar after successful processing
            self.hide_progress_bar()
            
        except Exception as e:
            self.logger.exception("Voice processing error:")
            self.update_status("Voice processing failed")
            self.hide_progress_bar()  # Hide progress bar on error

    def add_message(self, sender: str, message: str, msg_type: str = "user", translation: str = None) -> None:
        """Add a message to the chat with enhanced visual styling."""
        from datetime import datetime
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%H:%M:%S") if self.show_timestamps else None
        
        # Determine if this is a user message
        is_user = msg_type == "user"
        
        # Create enhanced message widget
        message_widget = MessageWidget(
            self.chat_scrollable,
            text=message,
            is_user=is_user,
            translation=translation,
            timestamp=timestamp
        )
        
        # Store message in history
        self.conversation_history.append({
            "sender": sender,
            "message": message,
            "translation": translation,
            "timestamp": timestamp,
            "type": msg_type
        })
        
        # Update message count
        message_count = len(self.conversation_history)
        if self.message_count_label:
            self.message_count_label.configure(text=f"Messages: {message_count}")
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            self.chat_scrollable._parent_canvas.yview_moveto(1.0)
        
        self.logger.info(f"Added {msg_type} message from {sender}")

    def clear_chat(self) -> None:
        """Clear the chat area and reset history."""
        # Clear all message widgets
        for widget in self.chat_scrollable.winfo_children():
            widget.destroy()
        
        # Clear history
        self.conversation_history.clear()
        self.message_widgets.clear()
        
        # Update message count
        if self.message_count_label:
            self.message_count_label.configure(text="Messages: 0")
        
        # Add system message
        self.add_message("System", "Chat cleared. Ready for new conversation.", "system")
        
        self.logger.info("Chat cleared")

    def update_status(self, status: str) -> None:
        """Update the status label with enhanced formatting."""
        if self.status_label:
            self.status_label.configure(text=f"Status: {status}")
            
        # Update status indicator color based on status
        if "error" in status.lower() or "failed" in status.lower():
            self.status_indicator.configure(text_color=ChatTheme.ACCENT_RED)
        elif "processing" in status.lower() or "recording" in status.lower():
            self.status_indicator.configure(text_color=ChatTheme.ACCENT_ORANGE)
        else:
            self.status_indicator.configure(text_color=ChatTheme.ACCENT_GREEN)
        
        self.logger.info(f"Status updated: {status}")

    def get_conversation_history(self) -> List[dict]:
        """Gets the conversation history."""
        return self.conversation_history.copy()

    def set_language(self, language: str) -> None:
        """Sets the interface language."""
        if self.language_combo:
            self.language_combo.set(language)

    def get_language(self) -> str:
        """Gets the current language setting."""
        return self.language_combo.get() if self.language_combo else "English"
