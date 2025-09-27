#!/usr/bin/env python3
"""
TalkBridge Desktop - Voice Controls Component
=============================================

Component for voice/audio capture controls with visual feedback.
Handles start/stop buttons, recording indicators, and audio visualization.

Author: TalkBridge Team
Date: 2025-09-18
Version: 1.0
"""

import logging
import random
from typing import Optional, Callable
from pathlib import Path
import sys
import tkinter as tk
import customtkinter as ctk

from src.desktop.ui.events import EventBus, EventHandler, AudioStateEvent
from src.desktop.ui.theme import (
    ColorPalette, Typography, Spacing, Dimensions, 
    ComponentThemes
)

class AudioVisualizer:
    """Visual representation of audio levels during recording."""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.bars = []
        self.max_bars = 15
        self.animation_running = False
        self.logger = logging.getLogger("src.desktop.audio_visualizer")
        
    def start_animation(self) -> None:
        """Start the audio visualization animation."""
        self.animation_running = True
        self.logger.debug("Started audio visualization")
        self._animate_bars()
        
    def stop_animation(self) -> None:
        """Stop the audio visualization animation."""
        self.animation_running = False
        self.canvas.delete("audio_bar")
        self.logger.debug("Stopped audio visualization")
        
    def _animate_bars(self) -> None:
        """Animate audio level bars."""
        if not self.animation_running:
            return
            
        self.canvas.delete("audio_bar")
        
        # Draw audio level bars
        bar_width = 8
        bar_spacing = 12
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            start_x = (canvas_width - (self.max_bars * bar_spacing)) // 2
            
            for i in range(self.max_bars):
                x = start_x + (i * bar_spacing)
                # Random height for animation effect
                bar_height = random.randint(5, canvas_height - 10)
                y = (canvas_height - bar_height) // 2
                
                # Color based on height (green to yellow to red)
                if bar_height > canvas_height * 0.7:
                    color = "#ff6b6b"  # Red for high
                elif bar_height > canvas_height * 0.4:
                    color = "#ffa726"  # Orange for medium
                else:
                    color = "#4caf50"  # Green for low
                
                self.canvas.create_rectangle(
                    x, y, x + bar_width, y + bar_height,
                    fill=color, outline="", tags="audio_bar"
                )
        
        # Schedule next frame
        if self.animation_running:
            self.canvas.after(120, self._animate_bars)

class RecordingButton:
    """Custom recording button with visual states."""
    
    def __init__(self, parent: ctk.CTkFrame, text: str, source_type: str,
                 on_start: Optional[Callable] = None, on_stop: Optional[Callable] = None):
        self.parent = parent
        self.text = text
        self.source_type = source_type  # "mic" or "system"
        self.on_start = on_start
        self.on_stop = on_stop
        self.is_recording = False
        
        # Colors
        self.inactive_color = "#444444"
        self.active_color = "#ff4444" if source_type == "mic" else "#ff8800"
        self.hover_color = "#666666"
        
        # Create button
        self.button = ctk.CTkButton(
            parent,
            text=f"▶ {text}",
            width=120,
            height=40,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY, Typography.FONT_WEIGHT_BOLD),
            fg_color=self.inactive_color,
            hover_color=self.hover_color,
            command=self._on_button_click
        )
    
    def pack(self, **kwargs):
        """Pack the button."""
        self.button.pack(**kwargs)
    
    def _on_button_click(self) -> None:
        """Handle button click."""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()
    
    def _start_recording(self) -> None:
        """Start recording state."""
        self.is_recording = True
        self.button.configure(
            text=f"⏹ Stop {self.text}",
            fg_color=self.active_color
        )
        
        if self.on_start:
            self.on_start()
    
    def _stop_recording(self) -> None:
        """Stop recording state."""
        self.is_recording = False
        self.button.configure(
            text=f"▶ {self.text}",
            fg_color=self.inactive_color
        )
        
        if self.on_stop:
            self.on_stop()
    
    def set_recording_state(self, is_recording: bool) -> None:
        """Set recording state externally."""
        if is_recording != self.is_recording:
            if is_recording:
                self._start_recording()
            else:
                self._stop_recording()
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button."""
        state = "normal" if enabled else "disabled"
        self.button.configure(state=state)

class VoiceControls(EventHandler):
    """
    Voice controls component for audio capture management.
    
    Features:
    - Start/stop microphone recording
    - Start/stop system audio capture
    - Audio visualization during recording
    - Status indicators
    - Quick toggle switches
    """
    
    def __init__(self, parent: ctk.CTkFrame, event_bus: EventBus,
                 on_mic_start: Optional[Callable] = None,
                 on_mic_stop: Optional[Callable] = None,
                 on_system_start: Optional[Callable] = None,
                 on_system_stop: Optional[Callable] = None):
        """Initialize voice controls component."""
        super().__init__(event_bus)
        self.parent = parent
        
        # Callbacks
        self.on_mic_start = on_mic_start
        self.on_mic_stop = on_mic_stop
        self.on_system_start = on_system_start
        self.on_system_stop = on_system_stop
        
        # State
        self.mic_recording = False
        self.system_recording = False
        
        # UI components
        self.main_frame = None
        self.mic_button = None
        self.system_button = None
        self.visualizer_canvas = None
        self.audio_visualizer = None
        self.status_label = None
        
        # Quick toggles
        self.mic_toggle = None
        self.system_toggle = None
        
        # Setup UI
        self.setup_ui()
        
        # Subscribe to events
        self.subscribe_to_events()
    
    def setup_ui(self) -> None:
        """Setup the voice controls UI."""
        # Main container
        self.main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="#2d2d2d",
            corner_radius=Dimensions.RADIUS_MD
        )
        self.main_frame.pack(fill="x", padx=10, pady=5)
        
        # Title
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Voice Controls",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY, Typography.FONT_WEIGHT_BOLD),
            text_color="#ffffff"
        )
        title_label.pack(side="left")
        
        # Main controls section
        self._create_recording_controls()
        
        # Audio visualizer section
        self._create_audio_visualizer()
        
        # Quick toggles section
        self._create_quick_toggles()
        
        # Status section
        self._create_status_display()
    
    def _create_recording_controls(self) -> None:
        """Create main recording control buttons."""
        controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=15, pady=5)
        
        # Recording buttons container
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Microphone recording button
        self.mic_button = RecordingButton(
            buttons_frame,
            "Microphone",
            "mic",
            on_start=self._on_mic_start_request,
            on_stop=self._on_mic_stop_request
        )
        self.mic_button.pack(side="left", padx=5)
        
        # System audio recording button
        self.system_button = RecordingButton(
            buttons_frame,
            "System Audio",
            "system",
            on_start=self._on_system_start_request,
            on_stop=self._on_system_stop_request
        )
        self.system_button.pack(side="left", padx=5)
    
    def _create_audio_visualizer(self) -> None:
        """Create audio visualization canvas."""
        viz_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#3c3c3c",
            corner_radius=6
        )
        viz_frame.pack(fill="x", padx=15, pady=5)
        
        viz_label = ctk.CTkLabel(
            viz_frame,
            text="Audio Level",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color="#cccccc"
        )
        viz_label.pack(pady=(5, 0))
        
        # Canvas for audio visualization
        self.visualizer_canvas = tk.Canvas(
            viz_frame,
            height=40,
            bg="#3c3c3c",
            highlightthickness=0
        )
        self.visualizer_canvas.pack(fill="x", padx=10, pady=5)
        
        # Initialize visualizer
        self.audio_visualizer = AudioVisualizer(self.visualizer_canvas)
    
    def _create_quick_toggles(self) -> None:
        """Create quick toggle switches."""
        toggles_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        toggles_frame.pack(fill="x", padx=15, pady=5)
        
        toggles_label = ctk.CTkLabel(
            toggles_frame,
            text="Quick Toggles",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION, Typography.FONT_WEIGHT_BOLD),
            text_color="#ffffff"
        )
        toggles_label.pack(anchor="w")
        
        switches_frame = ctk.CTkFrame(toggles_frame, fg_color="transparent")
        switches_frame.pack(fill="x", pady=(5, 0))
        
        # Microphone toggle
        mic_toggle_frame = ctk.CTkFrame(switches_frame, fg_color="transparent")
        mic_toggle_frame.pack(side="left", padx=10)
        
        self.mic_toggle = ctk.CTkSwitch(
            mic_toggle_frame,
            text="Microphone",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            command=self._on_mic_toggle
        )
        self.mic_toggle.pack()
        
        # System audio toggle
        sys_toggle_frame = ctk.CTkFrame(switches_frame, fg_color="transparent")
        sys_toggle_frame.pack(side="left", padx=10)
        
        self.system_toggle = ctk.CTkSwitch(
            sys_toggle_frame,
            text="System Audio",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            command=self._on_system_toggle
        )
        self.system_toggle.pack()
    
    def _create_status_display(self) -> None:
        """Create status display."""
        status_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#3c3c3c",
            corner_radius=6
        )
        status_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to record",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color="#cccccc"
        )
        self.status_label.pack(pady=8)
    
    def subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe("audio_state_change", self._on_audio_state_change_event)
    
    def unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        self.event_bus.unsubscribe("audio_state_change", self._on_audio_state_change_event)
    
    def _on_audio_state_change_event(self, event: AudioStateEvent) -> None:
        """Handle audio state change events."""
        self.logger.debug(f"Audio state change: {event.source} - {event.is_active}")
        
        if event.source == "mic":
            self.mic_recording = event.is_active
            if self.mic_button is not None:
                self.mic_button.set_recording_state(event.is_active)
            if self.mic_toggle is not None:
                self.mic_toggle.select() if event.is_active else self.mic_toggle.deselect()
        elif event.source == "system":
            self.system_recording = event.is_active
            if self.system_button is not None:
                self.system_button.set_recording_state(event.is_active)
            if self.system_toggle is not None:
                self.system_toggle.select() if event.is_active else self.system_toggle.deselect()
        
        # Update visualizer
        any_recording = self.mic_recording or self.system_recording
        if self.audio_visualizer is not None:
            if any_recording and not self.audio_visualizer.animation_running:
                self.audio_visualizer.start_animation()
            elif not any_recording and self.audio_visualizer.animation_running:
                self.audio_visualizer.stop_animation()
        
        # Update status
        self._update_status()
    
    def _on_mic_start_request(self) -> None:
        """Handle microphone start request."""
        self.logger.info("Microphone start requested")
        if self.on_mic_start:
            self.on_mic_start()
    
    def _on_mic_stop_request(self) -> None:
        """Handle microphone stop request."""
        self.logger.info("Microphone stop requested")
        if self.on_mic_stop:
            self.on_mic_stop()
    
    def _on_system_start_request(self) -> None:
        """Handle system audio start request."""
        self.logger.info("System audio start requested")
        if self.on_system_start:
            self.on_system_start()
    
    def _on_system_stop_request(self) -> None:
        """Handle system audio stop request."""
        self.logger.info("System audio stop requested")
        if self.on_system_stop:
            self.on_system_stop()
    
    def _on_mic_toggle(self) -> None:
        """Handle microphone toggle switch."""
        if self.mic_toggle is not None:
            if self.mic_toggle.get():
                self._on_mic_start_request()
            else:
                self._on_mic_stop_request()
    
    def _on_system_toggle(self) -> None:
        """Handle system audio toggle switch."""
        if self.system_toggle is not None:
            if self.system_toggle.get():
                self._on_system_start_request()
            else:
                self._on_system_stop_request()
    
    def _update_status(self) -> None:
        """Update status display."""
        if self.mic_recording and self.system_recording:
            status = "🎤 Recording microphone and system audio"
            color = "#ff6b6b"
        elif self.mic_recording:
            status = "🎤 Recording microphone"
            color = "#4caf50"
        elif self.system_recording:
            status = "🔊 Recording system audio"
            color = "#ff9800"
        else:
            status = "Ready to record"
            color = "#cccccc"
        
        if self.status_label is not None:
            self.status_label.configure(text=status, text_color=color)
    
    def set_mic_enabled(self, enabled: bool) -> None:
        """Enable or disable microphone controls."""
        if self.mic_button is not None:
            self.mic_button.set_enabled(enabled)
        if self.mic_toggle is not None:
            state = "normal" if enabled else "disabled"
            self.mic_toggle.configure(state=state)
    
    def set_system_enabled(self, enabled: bool) -> None:
        """Enable or disable system audio controls."""
        if self.system_button is not None:
            self.system_button.set_enabled(enabled)
        if self.system_toggle is not None:
            state = "normal" if enabled else "disabled"
            self.system_toggle.configure(state=state)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up voice controls")
        
        # Stop visualizer
        if self.audio_visualizer:
            self.audio_visualizer.stop_animation()
        
        # Unsubscribe from events
        self.unsubscribe_from_events()