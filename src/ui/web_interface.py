#!/usr/bin/env python3
"""
TalkBridge UI - Web Interface
=============================

Module interface

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- Flask
======================================================================
Functions:
- main: Main entry point for the web interface.
- __init__: Initialize the web interface.
- setup_page_config: Configure the Streamlit page.
- load_custom_css: Load custom CSS from assets folder.
- run: Main application loop.
- show_login_page: Display the login page.
- show_dashboard: Display the main dashboard.
======================================================================
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from auth.auth_manager import AuthManager
from ui.components.dashboard import Dashboard
from ui.components.login import LoginComponent
from ui.components.audio_recorder import AudioRecorder
from ui.components.chat_interface import ChatInterface
from ui.components.avatar_display import AvatarDisplay
from ui.api.tts_api import TTSAPI
from ui.api.stt_api import STTAPI
from ui.api.llm_api import LLMAPI
from ui.api.translation_api import TranslationAPI
from ui.api.animation_api import AnimationAPI


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
        """Load custom CSS from assets folder."""
        css_file = Path(__file__).parent / "assets" / "style.css"
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
            </style>
            """, unsafe_allow_html=True)
    
    def run(self):
        """Main application loop."""
        self.setup_page_config()
        
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
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.chat_history = []
                st.session_state.current_audio = None
                st.rerun()
        
        # Main dashboard content
        dashboard = Dashboard()
        dashboard.render()


def main():
    """Main entry point for the web interface."""
    try:
        # Create necessary directories
        assets_dir = Path(__file__).parent / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Initialize and run the web interface
        app = TalkBridgeWebInterface()
        app.run()
        
    except Exception as e:
        logger.error(f"Web interface error: {e}")
        st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main() 