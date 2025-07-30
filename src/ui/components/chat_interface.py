#! /usr/bin/env python3
#-------------------------------------------------------------------------------------------------
# description: Chat Interface Component
#-------------------------------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#
# requirements:
# - streamlit Python package
# - typing Python package
# - logging Python package
# - datetime Python package
#-------------------------------------------------------------------------------------------------  
# functions:
# - ChatInterface: Chat interface component class
# - render_chat_interface: Render the main chat interface
# - _display_chat_messages: Display chat messages
# - _display_message: Display a single chat message
# - _render_text_input: Render text input for manual messages
# - _add_user_message: Add a user message to chat history
# - add_assistant_message: Add an assistant message to chat history
# - render_chat_history_tab: Render the chat history tab
# - _display_filtered_history: Display filtered chat history
# - get_chat_statistics: Get chat statistics
# - export_chat_history: Export chat history
#-------------------------------------------------------------------------------------------------


import streamlit as st
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatInterface:
    """Chat interface component for web application."""
    
    def __init__(self):
        """Initialize the chat interface."""
        self.chat_history = []
        self.max_messages = 100
    
    def render_chat_interface(self) -> None:
        """Render the main chat interface."""
        st.markdown("#### 💬 Live Chat")
        
        # Chat messages container
        chat_container = st.container()
        
        with chat_container:
            self._display_chat_messages()
        
        # Manual text input
        self._render_text_input()
    
    def _display_chat_messages(self) -> None:
        """Display chat messages."""
        if st.session_state.get('chat_history'):
            for i, message in enumerate(st.session_state.chat_history[-10:]):  # Show last 10 messages
                self._display_message(message, i)
        else:
            st.info("No messages yet. Start recording to begin chatting!")
    
    def _display_message(self, message: Dict[str, Any], index: int) -> None:
        """
        Display a single chat message.
        
        Args:
            message: Message dictionary
            index: Message index
        """
        message_type = message.get('type', 'user')
        text = message.get('text', '')
        translated = message.get('translated', '')
        timestamp = message.get('timestamp', index)
        
        if message_type == 'user':
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You:</strong> {text}
                {f"<br><em>🌐 Translated: {translated}</em>" if translated else ''}
                <br><small>Message #{timestamp}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong> {text}
                <br><small>Message #{timestamp}</small>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_text_input(self) -> None:
        """Render text input for manual messages."""
        st.markdown("#### ✍️ Manual Input")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            manual_text = st.text_area("Type your message:", height=100, key="manual_input")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📤 Send", use_container_width=True):
                if manual_text.strip():
                    self._add_user_message(manual_text.strip())
                    st.success("Message sent!")
                    st.rerun()
                else:
                    st.warning("Please enter a message.")
    
    def _add_user_message(self, text: str, translated: str = None) -> None:
        """
        Add a user message to chat history.
        
        Args:
            text: Message text
            translated: Translated text (optional)
        """
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        message = {
            'type': 'user',
            'text': text,
            'translated': translated,
            'timestamp': len(st.session_state.chat_history),
            'timestamp_real': datetime.now().isoformat()
        }
        
        st.session_state.chat_history.append(message)
        
        # Keep history within limit
        if len(st.session_state.chat_history) > self.max_messages:
            st.session_state.chat_history = st.session_state.chat_history[-self.max_messages:]
        
        logger.info(f"Added user message: {text[:50]}...")
    
    def add_assistant_message(self, text: str) -> None:
        """
        Add an assistant message to chat history.
        
        Args:
            text: Message text
        """
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        message = {
            'type': 'assistant',
            'text': text,
            'timestamp': len(st.session_state.chat_history),
            'timestamp_real': datetime.now().isoformat()
        }
        
        st.session_state.chat_history.append(message)
        
        # Keep history within limit
        if len(st.session_state.chat_history) > self.max_messages:
            st.session_state.chat_history = st.session_state.chat_history[-self.max_messages:]
        
        logger.info(f"Added assistant message: {text[:50]}...")
    
    def render_chat_history_tab(self) -> None:
        """Render the chat history tab."""
        st.markdown("### 💬 Chat History")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox("Filter by Type", ["All", "User", "Assistant"])
        
        with col2:
            filter_language = st.selectbox("Filter by Language", ["All", "English", "Spanish", "French", "German"])
        
        with col3:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.chat_history = []
                st.success("Chat history cleared!")
        
        # Display filtered chat history
        self._display_filtered_history(filter_type, filter_language)
    
    def _display_filtered_history(self, filter_type: str, filter_language: str) -> None:
        """
        Display filtered chat history.
        
        Args:
            filter_type: Type filter
            filter_language: Language filter
        """
        if not st.session_state.get('chat_history'):
            st.info("No chat history available.")
            return
        
        filtered_messages = []
        
        for message in st.session_state.chat_history:
            # Apply type filter
            if filter_type != "All" and message['type'].title() != filter_type:
                continue
            
            # Apply language filter (basic implementation)
            if filter_language != "All":
                text = message.get('text', '').lower()
                if filter_language == "English" and not any(word in text for word in ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo']):
                    pass  # Keep English messages
                elif filter_language == "Spanish" and any(word in text for word in ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo']):
                    pass  # Keep Spanish messages
                elif filter_language == "French" and any(word in text for word in ['le', 'la', 'de', 'et', 'est', 'un', 'une', 'dans', 'pour', 'avec', 'sur']):
                    pass  # Keep French messages
                elif filter_language == "German" and any(word in text for word in ['der', 'die', 'das', 'und', 'ist', 'sind', 'in', 'auf', 'mit', 'von', 'zu']):
                    pass  # Keep German messages
                else:
                    continue
            
            filtered_messages.append(message)
        
        # Display filtered messages
        for i, message in enumerate(filtered_messages):
            self._display_message(message, i)
        
        if not filtered_messages:
            st.info(f"No messages match the current filters.")
    
    def get_chat_statistics(self) -> Dict[str, Any]:
        """
        Get chat statistics.
        
        Returns:
            Dictionary containing chat statistics
        """
        if not st.session_state.get('chat_history'):
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "average_message_length": 0
            }
        
        messages = st.session_state.chat_history
        
        user_messages = [m for m in messages if m['type'] == 'user']
        assistant_messages = [m for m in messages if m['type'] == 'assistant']
        
        total_length = sum(len(m.get('text', '')) for m in messages)
        avg_length = total_length / len(messages) if messages else 0
        
        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "average_message_length": round(avg_length, 1)
        }
    
    def export_chat_history(self, format: str = "json") -> Optional[str]:
        """
        Export chat history.
        
        Args:
            format: Export format (json, txt, csv)
            
        Returns:
            Exported data as string or None if failed
        """
        try:
            if not st.session_state.get('chat_history'):
                return None
            
            if format == "json":
                import json
                return json.dumps(st.session_state.chat_history, indent=2)
            
            elif format == "txt":
                lines = []
                for message in st.session_state.chat_history:
                    timestamp = message.get('timestamp_real', '')
                    msg_type = message['type']
                    text = message.get('text', '')
                    translated = message.get('translated', '')
                    
                    line = f"[{timestamp}] {msg_type.upper()}: {text}"
                    if translated:
                        line += f" (Translated: {translated})"
                    lines.append(line)
                
                return "\n".join(lines)
            
            elif format == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['Timestamp', 'Type', 'Text', 'Translated'])
                
                for message in st.session_state.chat_history:
                    writer.writerow([
                        message.get('timestamp_real', ''),
                        message['type'],
                        message.get('text', ''),
                        message.get('translated', '')
                    ])
                
                return output.getvalue()
            
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to export chat history: {e}")
            return None 