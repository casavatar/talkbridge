#!/usr/bin/env python3
"""
TalkBridge Desktop - AI Actions Component
=========================================

Component for LLM interaction, prompt management, and AI-powered commands.
Handles chat input, message sending, and TTS triggering for responses.

Author: TalkBridge Team
Date: 2025-09-18
Version: 1.0
"""

import logging
import asyncio
from typing import Optional, Callable, List, Dict, Any
from pathlib import Path
import customtkinter as ctk

.parent.parent.parent))

from talkbridge.desktop.ui.events import EventBus, EventHandler
from talkbridge.desktop.ui.theme import (
    ColorPalette, Typography, Spacing, Dimensions, 
    ComponentThemes
)

class AIActions(EventHandler):
    """
    AI actions component for LLM interaction and commands.
    
    Features:
    - Text input for chat messages
    - AI model selection
    - Send button with loading state
    - TTS toggle for responses
    - Quick prompt templates
    - Conversation context management
    """
    
    def __init__(self, parent: ctk.CTkFrame, event_bus: EventBus,
                 on_send_message: Optional[Callable[[str, str], None]] = None,
                 on_tts_toggle: Optional[Callable[[bool], None]] = None):
        """Initialize AI actions component."""
        super().__init__(event_bus)
        self.parent = parent
        
        # Callbacks
        self.on_send_message = on_send_message  # (message, model) -> None
        self.on_tts_toggle = on_tts_toggle      # (enabled) -> None
        
        # State
        self.current_model = "llama3.2:3b"
        self.tts_enabled = True
        self.is_processing = False
        
        # Available models
        self.available_models = [
            "llama3.2:3b",
            "llama3.2:1b", 
            "llama3.1:8b",
            "codellama:7b",
            "mistral:7b",
            "gemma:2b"
        ]
        
        # Quick prompts
        self.quick_prompts = [
            "Summarize the conversation",
            "Translate to English",
            "Explain in simple terms",
            "What are the key points?",
            "Continue the discussion",
            "Provide examples"
        ]
        
        # UI components
        self.main_frame = None
        self.input_entry = None
        self.send_button = None
        self.model_combo = None
        self.tts_toggle = None
        self.quick_prompts_frame = None
        self.processing_indicator = None
        
        # Setup UI
        self.setup_ui()
        
        # Subscribe to events
        self.subscribe_to_events()
    
    def setup_ui(self) -> None:
        """Setup the AI actions UI."""
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
            text="AI Chat & Commands",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY, Typography.FONT_WEIGHT_BOLD),
            text_color="#ffffff"
        )
        title_label.pack(side="left")
        
        # Processing indicator
        self.processing_indicator = ctk.CTkLabel(
            title_frame,
            text="",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color="#ff9800"
        )
        self.processing_indicator.pack(side="right")
        
        # Settings section
        self._create_settings_section()
        
        # Input section
        self._create_input_section()
        
        # Quick prompts section
        self._create_quick_prompts_section()
    
    def _create_settings_section(self) -> None:
        """Create AI settings controls."""
        settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        settings_frame.pack(fill="x", padx=15, pady=5)
        
        # Model selection
        model_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        model_frame.pack(side="left", fill="x", expand=True)
        
        model_label = ctk.CTkLabel(
            model_frame,
            text="Model:",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color="#cccccc",
            width=60
        )
        model_label.pack(side="left", padx=(0, 10))
        
        self.model_combo = ctk.CTkComboBox(
            model_frame,
            values=self.available_models,
            width=150,
            height=28,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            command=self._on_model_selected
        )
        self.model_combo.pack(side="left")
        self.model_combo.set(self.current_model)
        
        # TTS toggle
        tts_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        tts_frame.pack(side="right")
        
        self.tts_toggle = ctk.CTkSwitch(
            tts_frame,
            text="🔊 TTS",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            command=self._on_tts_toggle
        )
        self.tts_toggle.pack()
        self.tts_toggle.select()  # Default enabled
    
    def _create_input_section(self) -> None:
        """Create message input controls."""
        input_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#3c3c3c",
            corner_radius=6
        )
        input_frame.pack(fill="x", padx=15, pady=5)
        
        # Input field with send button
        entry_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=10, pady=10)
        
        # Text input
        self.input_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Type your message or question...",
            height=35,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY),
            fg_color="#4a4a4a",
            border_color="#666666"
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_entry.bind("<Return>", self._on_enter_pressed)
        
        # Send button
        self.send_button = ctk.CTkButton(
            entry_frame,
            text="Send",
            width=80,
            height=35,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY, Typography.FONT_WEIGHT_BOLD),
            fg_color="#0078d4",
            hover_color="#106ebe",
            command=self._on_send_clicked
        )
        self.send_button.pack(side="right")
    
    def _create_quick_prompts_section(self) -> None:
        """Create quick prompt buttons."""
        prompts_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        prompts_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        # Title
        prompts_label = ctk.CTkLabel(
            prompts_frame,
            text="Quick Prompts",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION, Typography.FONT_WEIGHT_BOLD),
            text_color="#ffffff"
        )
        prompts_label.pack(anchor="w", pady=(0, 5))
        
        # Buttons container
        self.quick_prompts_frame = ctk.CTkFrame(prompts_frame, fg_color="transparent")
        self.quick_prompts_frame.pack(fill="x")
        
        # Create prompt buttons in rows
        current_row = None
        for i, prompt in enumerate(self.quick_prompts):
            if i % 3 == 0:  # New row every 3 buttons
                current_row = ctk.CTkFrame(self.quick_prompts_frame, fg_color="transparent")
                current_row.pack(fill="x", pady=1)
            
            button = ctk.CTkButton(
                current_row,
                text=prompt,
                width=140,
                height=25,
                font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
                fg_color="#555555",
                hover_color="#777777",
                command=lambda p=prompt: self._on_quick_prompt_clicked(p)
            )
            button.pack(side="left", padx=2)
    
    def subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        # AI Actions primarily sends events rather than receiving them
        pass
    
    def unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        pass
    
    def _on_model_selected(self, model_name: str) -> None:
        """Handle model selection."""
        self.current_model = model_name
        self.logger.info(f"Selected AI model: {model_name}")
    
    def _on_tts_toggle(self) -> None:
        """Handle TTS toggle."""
        self.tts_enabled = self.tts_toggle.get()
        self.logger.info(f"TTS enabled: {self.tts_enabled}")
        
        if self.on_tts_toggle:
            self.on_tts_toggle(self.tts_enabled)
    
    def _on_enter_pressed(self, event) -> None:
        """Handle Enter key press in input field."""
        self._send_message()
    
    def _on_send_clicked(self) -> None:
        """Handle send button click."""
        self._send_message()
    
    def _on_quick_prompt_clicked(self, prompt: str) -> None:
        """Handle quick prompt button click."""
        self.logger.info(f"Quick prompt selected: {prompt}")
        
        # Set the prompt in the input field
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, prompt)
        
        # Optionally send immediately or let user modify
        # For now, just populate the field
    
    def _send_message(self) -> None:
        """Send the current message."""
        message = self.input_entry.get().strip()
        
        if not message:
            self.logger.debug("Empty message, not sending")
            return
        
        if self.is_processing:
            self.logger.debug("Already processing, ignoring send request")
            return
        
        self.logger.info(f"Sending message: {message[:50]}...")
        
        # Clear input
        self.input_entry.delete(0, "end")
        
        # Set processing state
        self.set_processing(True)
        
        # Send via callback
        if self.on_send_message:
            self.on_send_message(message, self.current_model)
    
    def set_processing(self, processing: bool) -> None:
        """Set processing state."""
        self.is_processing = processing
        
        if processing:
            self.send_button.configure(
                text="...",
                state="disabled",
                fg_color="#666666"
            )
            self.processing_indicator.configure(text="🤖 Processing...")
            self.input_entry.configure(state="disabled")
        else:
            self.send_button.configure(
                text="Send",
                state="normal",
                fg_color="#0078d4"
            )
            self.processing_indicator.configure(text="")
            self.input_entry.configure(state="normal")
            
            # Focus back to input
            self.input_entry.focus()
    
    def add_quick_prompt(self, prompt: str) -> None:
        """Add a custom quick prompt."""
        if prompt not in self.quick_prompts:
            self.quick_prompts.append(prompt)
            self._recreate_quick_prompts()
            self.logger.info(f"Added quick prompt: {prompt}")
    
    def remove_quick_prompt(self, prompt: str) -> None:
        """Remove a quick prompt."""
        if prompt in self.quick_prompts:
            self.quick_prompts.remove(prompt)
            self._recreate_quick_prompts()
            self.logger.info(f"Removed quick prompt: {prompt}")
    
    def _recreate_quick_prompts(self) -> None:
        """Recreate quick prompt buttons after changes."""
        # Clear existing buttons
        for widget in self.quick_prompts_frame.winfo_children():
            widget.destroy()
        
        # Recreate buttons
        current_row = None
        for i, prompt in enumerate(self.quick_prompts):
            if i % 3 == 0:
                current_row = ctk.CTkFrame(self.quick_prompts_frame, fg_color="transparent")
                current_row.pack(fill="x", pady=1)
            
            button = ctk.CTkButton(
                current_row,
                text=prompt,
                width=140,
                height=25,
                font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
                fg_color="#555555",
                hover_color="#777777",
                command=lambda p=prompt: self._on_quick_prompt_clicked(p)
            )
            button.pack(side="left", padx=2)
    
    def set_input_text(self, text: str) -> None:
        """Set text in the input field."""
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, text)
    
    def get_input_text(self) -> str:
        """Get current text in the input field."""
        return self.input_entry.get()
    
    def clear_input(self) -> None:
        """Clear the input field."""
        self.input_entry.delete(0, "end")
    
    def set_model(self, model: str) -> None:
        """Set the AI model programmatically."""
        if model in self.available_models:
            self.current_model = model
            self.model_combo.set(model)
            self.logger.info(f"AI model set to: {model}")
    
    def get_model(self) -> str:
        """Get the current AI model."""
        return self.current_model
    
    def set_tts_enabled(self, enabled: bool) -> None:
        """Set TTS enabled state programmatically."""
        self.tts_enabled = enabled
        if enabled:
            self.tts_toggle.select()
        else:
            self.tts_toggle.deselect()
    
    def is_tts_enabled(self) -> bool:
        """Check if TTS is enabled."""
        return self.tts_enabled
    
    def focus_input(self) -> None:
        """Focus the input field."""
        self.input_entry.focus()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up AI actions")
        self.unsubscribe_from_events()