#!/usr/bin/env python3
"""
TalkBridge Desktop - Chat History Component
==========================================

Dedicated component for rendering chat messages and conversation flow.
Handles message bubbles, timestamps, language indicators, and auto-scrolling.

Author: TalkBridge Team
Date: 2025-09-26  
Version: 1.1 - Enhanced with robust null safety

Features:
- Safe handling of optional translation text
- Proper null checks for UI components
- Thread-safe UI operations
- Robust error handling and logging
- Type-safe message widget creation

Bug Fixes (v1.1):
- Fixed None handling for translation text in message rendering
- Added null safety checks for scroll_frame operations
- Enhanced error logging and graceful degradation
- Improved type annotations for better IDE support
"""

import logging
import time
from typing import List, Optional, Dict, Any
from pathlib import Path
import customtkinter as ctk

from src.desktop.ui.events import EventBus, EventHandler, TranscriptEvent, TranslationEvent, AudioSource
from src.desktop.ui.ui_utils import clean_text, strip_variation_selectors
from src.desktop.ui.theme import (
    ColorPalette, Typography, Spacing, Dimensions, 
    ComponentThemes, UIText
)

class MessageData:
    """Data structure for a chat message."""
    
    def __init__(self, text: str, is_user: bool = True, translation: Optional[str] = None,
                 timestamp: Optional[float] = None, source_language: str = "en",
                 target_language: str = "en", source_type: Optional[AudioSource] = None):
        self.text = text
        self.is_user = is_user
        self.translation = translation
        self.timestamp = timestamp or time.time()
        self.source_language = source_language
        self.target_language = target_language
        self.source_type = source_type
        self.id = id(self)  # Unique identifier
    
    def get_timestamp_str(self) -> str:
        """Get formatted timestamp string."""
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))

class MessageWidget:
    """Widget for rendering individual chat messages with rich formatting."""
    
    def __init__(self, parent: ctk.CTkScrollableFrame, message: MessageData):
        self.parent = parent
        self.message = message
        self.logger = logging.getLogger("talkbridge.desktop.message_widget")
        
        # Theme colors
        self._setup_theme_colors()
        
        # Create the message UI
        self.container_frame = None
        self.setup_message_ui()
    
    def _setup_theme_colors(self) -> None:
        """Setup theme colors based on message type."""
        if self.message.is_user:
            self.bg_color = "#0e3a5f"  # Dark blue for user
            self.border_color = "#1e5a8a"
            self.sender_color = "#87CEEB"  # Light blue
            self.sender_text = "You"
        else:
            self.bg_color = "#2d1b3d"  # Dark purple for assistant
            self.border_color = "#4a2c5a"
            self.sender_color = "#DDA0DD"  # Light purple
            self.sender_text = "Assistant"
    
    def setup_message_ui(self) -> None:
        """Create and layout the message UI components."""
        # Message container
        self.container_frame = ctk.CTkFrame(self.parent)
        self.container_frame.pack(fill="x", padx=10, pady=5)
        
        # Inner frame for message content
        inner_frame = ctk.CTkFrame(
            self.container_frame,
            fg_color=self.bg_color,
            border_color=self.border_color,
            border_width=2,
            corner_radius=Dimensions.RADIUS_MD
        )
        inner_frame.pack(fill="x", padx=5, pady=5)
        
        # Header with sender and timestamp
        self._create_header(inner_frame)
        
        # Message content with language indicators
        self._create_content(inner_frame)
    
    def _create_header(self, parent: ctk.CTkFrame) -> None:
        """Create message header with sender and timestamp."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Sender label
        sender_label = ctk.CTkLabel(
            header_frame,
            text=self.sender_text,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY, Typography.FONT_WEIGHT_BOLD),
            text_color=self.sender_color
        )
        sender_label.pack(side="left")
        
        # Timestamp
        time_label = ctk.CTkLabel(
            header_frame,
            text=self.message.get_timestamp_str(),
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            text_color="#999999"
        )
        time_label.pack(side="right")
    
    def _create_content(self, parent: ctk.CTkFrame) -> None:
        """Create message content with text and optional translation."""
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=5)
        
        # Language/source indicator
        self._create_language_indicator(content_frame)
        
        # Main message text
        self._create_message_text(content_frame)
        
        # Translation if available
        if self.message.translation and self.message.translation != self.message.text:
            self._create_translation_text(content_frame)
    
    def _create_language_indicator(self, parent: ctk.CTkFrame) -> None:
        """Create language/source indicator badge."""
        # Determine source tag and color
        if self.message.source_type == "mic":
            source_tag = f"[Mic/{self.message.source_language.upper()}]"
            source_color = "#00ff88"  # Green for microphone
        elif self.message.source_type == "system":
            source_tag = f"[Sys/{self.message.source_language.upper()}]"
            source_color = "#ff8800"  # Orange for system audio
        else:
            source_tag = f"[{self.message.source_language.upper()}]"  # Manual input
            source_color = "#0078d4"  # Blue for manual
        
        lang_indicator = ctk.CTkLabel(
            parent,
            text=source_tag,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION, Typography.FONT_WEIGHT_BOLD),
            text_color=source_color,
            fg_color="#1e1e1e",
            corner_radius=4
        )
        lang_indicator.pack(anchor="w", pady=(0, 2))
    
    def _create_message_text(self, parent: ctk.CTkFrame) -> None:
        """Create main message text widget."""
        # Calculate height based on text length
        text_height = max(60, min(120, len(self.message.text) // 50 * 20 + 60))
        
        message_text = ctk.CTkTextbox(
            parent,
            height=text_height,
            wrap="word",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY),
            fg_color="transparent",
            scrollbar_button_color=self.border_color
        )
        message_text.pack(fill="both", expand=True, pady=(0, 5))
        
        # Insert and format text
        clean_message = strip_variation_selectors(self.message.text)
        message_text.insert("1.0", clean_message)
        message_text.configure(state="disabled")
    
    def _create_translation_text(self, parent: ctk.CTkFrame) -> None:
        """Create translation text widget."""
        translation_frame = ctk.CTkFrame(parent, fg_color="transparent")
        translation_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Translation language indicator
        trans_lang_indicator = ctk.CTkLabel(
            translation_frame,
            text=f"[→ {self.message.target_language.upper()}]",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION, Typography.FONT_WEIGHT_BOLD),
            text_color="#4CAF50",
            fg_color="#1e1e1e",
            corner_radius=4
        )
        trans_lang_indicator.pack(anchor="w", pady=(0, 2))
        
        # Translation text
        translation_text_content = self.message.translation or ""
        trans_height = max(40, min(80, len(translation_text_content) // 50 * 15 + 40))
        
        translation_text = ctk.CTkTextbox(
            translation_frame,
            height=trans_height,
            wrap="word",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION),
            fg_color="#2a2a2a",
            text_color="#cccccc",
            scrollbar_button_color=self.border_color
        )
        translation_text.pack(fill="both", expand=True)
        
        clean_translation = strip_variation_selectors(translation_text_content)
        translation_text.insert("1.0", clean_translation)
        translation_text.configure(state="disabled")
    
    def destroy(self) -> None:
        """Clean up the message widget."""
        if self.container_frame:
            self.container_frame.destroy()

class ChatHistory(EventHandler):
    """
    Chat history component for displaying conversation messages.
    
    Features:
    - Message rendering with rich formatting
    - Language indicators and source tags
    - Translation display
    - Auto-scrolling
    - Message management (add, clear, search)
    """
    
    def __init__(self, parent: ctk.CTkFrame, event_bus: EventBus):
        """Initialize chat history component."""
        super().__init__(event_bus)
        self.parent = parent
        
        # Logger
        self.logger = logging.getLogger("talkbridge.desktop.chat_history")
        
        # Message storage
        self.messages: List[MessageData] = []
        self.message_widgets: List[MessageWidget] = []
        
        # Settings
        self.auto_scroll = True
        self.max_messages = 100  # Limit for performance
        
        # UI components
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.scroll_frame: Optional[ctk.CTkScrollableFrame] = None
        self.setup_ui()
        
        # Subscribe to events
        self.subscribe_to_events()
    
    def setup_ui(self) -> None:
        """Setup the chat history UI."""
        # Main container
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="#1e1e1e")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Conversation",
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_BODY, Typography.FONT_WEIGHT_BOLD),
            text_color="#ffffff"
        )
        title_label.pack(side="left")
        
        # Auto-scroll toggle
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        auto_scroll_toggle = ctk.CTkCheckBox(
            header_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            command=self._on_auto_scroll_toggle,
            font=(Typography.FONT_FAMILY_PRIMARY, Typography.FONT_SIZE_CAPTION)
        )
        auto_scroll_toggle.pack(side="right")
        
        # Scrollable frame for messages
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="#2d2d2d",
            scrollbar_button_color="#555555"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
    
    def subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe("transcript", self.add_transcript)
        self.event_bus.subscribe("translation", self.add_translation)
    
    def unsubscribe_from_events(self) -> None:
        """Unsubscribe from events."""
        self.event_bus.unsubscribe("transcript", self.add_transcript)
        self.event_bus.unsubscribe("translation", self.add_translation)
    
    def add_user_message(self, text: str, language: str = "en", 
                        source: Optional[AudioSource] = None) -> None:
        """Add a user message to the chat history."""
        message = MessageData(
            text=text,
            is_user=True,
            source_language=language,
            source_type=source
        )
        self._add_message(message)
    
    def add_assistant_message(self, text: str, language: str = "en") -> None:
        """Add an assistant message to the chat history."""
        message = MessageData(
            text=text,
            is_user=False,
            source_language=language
        )
        self._add_message(message)
    
    def add_transcript(self, event: TranscriptEvent) -> None:
        """Handle transcript event by adding to chat history."""
        self.logger.debug(f"Adding transcript from {event.source}: {event.text[:50]}...")
        self.add_user_message(
            text=event.text,
            language=event.language,
            source=event.source
        )
    
    def add_translation(self, event: TranslationEvent) -> None:
        """Handle translation event by updating the last message."""
        self.logger.debug(f"Adding translation: {event.translated_text[:50]}...")
        
        # Find the most recent message with matching original text
        for message in reversed(self.messages):
            if (message.text == event.original_text and 
                message.source_type == event.source):
                message.translation = event.translated_text
                message.target_language = event.target_language
                
                # Re-render the message widget
                self._refresh_message_widget(message)
                break
        else:
            # If no matching message found, create a new one with translation
            message = MessageData(
                text=event.original_text,
                is_user=True,
                translation=event.translated_text,
                source_language=event.source_language,
                target_language=event.target_language,
                source_type=event.source
            )
            self._add_message(message)
    
    def _add_message(self, message: MessageData) -> None:
        """Internal method to add a message and create its widget."""
        # Ensure UI is initialized
        if not self.scroll_frame:
            self.logger.error("Cannot add message: scroll_frame not initialized")
            return
            
        # Limit message history for performance
        if len(self.messages) >= self.max_messages:
            self._remove_oldest_message()
        
        # Add message
        self.messages.append(message)
        
        # Create widget
        widget = MessageWidget(self.scroll_frame, message)
        self.message_widgets.append(widget)
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            self._scroll_to_bottom()
        
        self.logger.debug(f"Added message (total: {len(self.messages)})")
    
    def _remove_oldest_message(self) -> None:
        """Remove the oldest message and its widget."""
        if self.messages and self.message_widgets:
            # Remove from storage
            self.messages.pop(0)
            
            # Destroy and remove widget
            widget = self.message_widgets.pop(0)
            widget.destroy()
    
    def _refresh_message_widget(self, message: MessageData) -> None:
        """Refresh a specific message widget."""
        # Ensure UI is initialized
        if not self.scroll_frame:
            self.logger.error("Cannot refresh message: scroll_frame not initialized")
            return
            
        # Find the widget for this message
        for i, msg in enumerate(self.messages):
            if msg.id == message.id and i < len(self.message_widgets):
                # Destroy old widget
                self.message_widgets[i].destroy()
                
                # Create new widget
                new_widget = MessageWidget(self.scroll_frame, message)
                self.message_widgets[i] = new_widget
                break
    
    def _scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the conversation."""
        if not self.scroll_frame:
            self.logger.debug("Cannot scroll: scroll_frame not initialized")
            return
            
        try:
            # Schedule scroll after UI update
            self.scroll_frame.after(10, lambda: self.scroll_frame._parent_canvas.yview_moveto(1.0) if self.scroll_frame else None)
        except Exception as e:
            self.logger.debug(f"Scroll error (likely during initialization): {e}")
    
    def _on_auto_scroll_toggle(self) -> None:
        """Handle auto-scroll toggle."""
        self.auto_scroll = self.auto_scroll_var.get()
        self.logger.debug(f"Auto-scroll: {self.auto_scroll}")
        
        if self.auto_scroll:
            self._scroll_to_bottom()
    
    def clear_history(self) -> None:
        """Clear all messages from the chat history."""
        self.logger.info("Clearing chat history")
        
        # Destroy all widgets
        for widget in self.message_widgets:
            widget.destroy()
        
        # Clear storage
        self.messages.clear()
        self.message_widgets.clear()
    
    def get_message_count(self) -> int:
        """Get the number of messages in history."""
        return len(self.messages)
    
    def get_conversation_text(self) -> str:
        """Get the full conversation as plain text."""
        lines = []
        for message in self.messages:
            sender = "User" if message.is_user else "Assistant"
            timestamp = message.get_timestamp_str()
            lines.append(f"[{timestamp}] {sender}: {message.text}")
            
            if message.translation:
                lines.append(f"  Translation: {message.translation}")
        
        return "\n".join(lines)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Cleaning up chat history")
        self.unsubscribe_from_events()
        self.clear_history()