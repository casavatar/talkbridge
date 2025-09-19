#!/usr/bin/env python3
"""
TalkBridge Web Interface
========================

Consolidated web interface module for TalkBridge

Author: TalkBridge Team
Date: 2025-09-18
Version: 2.0

Requirements:
- Flask
- Streamlit
======================================================================
Functions:
- main: Main entry point for the web interface.
- TalkBridgeWebInterface: Main web interface class.
======================================================================
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path

# Import centralized logging
from talkbridge.logging_config import get_logger

# Import local modules with proper package paths
from talkbridge.auth.auth_manager import AuthManager
from talkbridge.web.components.dashboard import Dashboard
from talkbridge.web.components.login import LoginComponent
from talkbridge.web.components.audio_recorder import AudioRecorder
from talkbridge.web.components.chat_interface import ChatInterface
from talkbridge.web.components.avatar_display import AvatarDisplay
from talkbridge.web.api.tts_api import TTSAPI
from talkbridge.web.api.stt_api import STTAPI
from talkbridge.web.api.llm_api import LLMAPI
from talkbridge.web.api.translation_api import TranslationAPI
from talkbridge.web.api.animation_api import AnimationAPI

# Import notification system
try:
    from ..web.notifier import notify, Level
    from ..web.notifier_adapter import WebNotificationBuffer
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

logger = get_logger(__name__)

class TalkBridgeWebInterface:
    """Main web interface class for TalkBridge application."""
    
    def __init__(self):
        """Initialize the web interface."""
        self.auth_manager = AuthManager()
        self.tts_api = TTSAPI()
        self.stt_api = STTAPI()
        self.llm_api = LLMAPI()
        self.translation_api = TranslationAPI()
        self.animation_api = AnimationAPI()
        
        # Initialize notification buffer if available
        self.notification_buffer = None
        if NOTIFICATIONS_AVAILABLE:
            try:
                self.notification_buffer = WebNotificationBuffer()
                logger.info("Web interface integrated with notification system")
            except Exception as e:
                logger.warning(f"Failed to initialize notification buffer: {e}")
        
        # Initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'current_audio' not in st.session_state:
            st.session_state.current_audio = None
    
    def setup_page_config(self):
        """Configure the Streamlit page."""
        st.set_page_config(
            page_title="TalkBridge",
            page_icon="🎤",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        self.load_custom_css()
    
    def load_custom_css(self):
        """Load custom CSS from static folder."""
        css_file = Path(__file__).parent / "static" / "style.css"
        if css_file.exists():
            with open(css_file, "r") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            # Fallback CSS
            st.markdown("""
            <style>
            .main-header {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
            .chat-message {
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .user-message {
                background-color: #f0f2f6;
            }
            .assistant-message {
                background-color: #e8f4fd;
            }
            .login-container {
                max-width: 400px;
                margin: 0 auto;
                padding: 2rem;
            }
            .notification-area {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                width: 300px;
            }
            .notification {
                padding: 1rem;
                margin-bottom: 0.5rem;
                border-radius: 5px;
                border-left: 4px solid;
                animation: slideIn 0.3s ease-out;
            }
            .notification.info {
                background-color: #e7f3ff;
                border-color: #2196F3;
                color: #0d47a1;
            }
            .notification.warning {
                background-color: #fff3cd;
                border-color: #ffc107;
                color: #856404;
            }
            .notification.error {
                background-color: #f8d7da;
                border-color: #dc3545;
                color: #721c24;
            }
            .notification.success {
                background-color: #d4edda;
                border-color: #28a745;
                color: #155724;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            </style>
            """, unsafe_allow_html=True)
    
    def render_notifications(self):
        """Render web notifications if available."""
        if self.notification_buffer and NOTIFICATIONS_AVAILABLE:
            notifications = self.notification_buffer.get_notifications()
            if notifications:
                notification_html = '<div class="notification-area">'
                for notification in notifications:
                    level_class = notification['level'].lower()
                    notification_html += f'''
                    <div class="notification {level_class}">
                        <strong>{notification['level']}:</strong> {notification['message']}
                        {f'<br><small>Category: {notification["category"]}</small>' if notification.get('category') else ''}
                    </div>
                    '''
                notification_html += '</div>'
                st.markdown(notification_html, unsafe_allow_html=True)
    
    def run(self):
        """Main application loop."""
        self.setup_page_config()
        
        # Render notifications at the top
        self.render_notifications()
        
        # Check authentication
        if not st.session_state.authenticated:
            self.show_login_page()
        else:
            self.show_dashboard()
    
    def show_login_page(self):
        """Display the login page."""
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; text-align: center; margin: 0;">🎤 TalkBridge</h1>
            <p style="color: white; text-align: center; margin: 0;">Real-time voice translation and communication</p>
        </div>
        """, unsafe_allow_html=True)
        
        login_component = LoginComponent(self.auth_manager)
        success, username = login_component.render()
        
        if success:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
            
            # Send notification for successful login
            if NOTIFICATIONS_AVAILABLE:
                try:
                    notify(f"User {username} logged in successfully", Level.SUCCESS, category="authentication")
                except Exception as e:
                    logger.warning(f"Failed to send login notification: {e}")
            
            st.rerun()
    
    def show_dashboard(self):
        """Display the main dashboard."""
        # Header
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(f"### 👤 {st.session_state.username}")
        
        with col2:
            st.markdown("""
            <h1 style="text-align: center; color: #667eea;">🎤 TalkBridge Dashboard</h1>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("🚪 Logout"):
                username = st.session_state.username
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.chat_history = []
                st.session_state.current_audio = None
                
                # Send notification for logout
                if NOTIFICATIONS_AVAILABLE:
                    try:
                        notify(f"User {username} logged out", Level.INFO, category="authentication")
                    except Exception as e:
                        logger.warning(f"Failed to send logout notification: {e}")
                
                st.rerun()
        
        # Main dashboard content
        dashboard = Dashboard()
        dashboard.render()

def main():
    """Main entry point for the web interface."""
    try:
        # Create necessary directories
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        
        templates_dir = Path(__file__).parent / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Initialize and run the web interface
        app = TalkBridgeWebInterface()
        app.run()
        
    except Exception as e:
        logger.error(f"Web interface error: {e}")
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()