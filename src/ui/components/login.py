#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: Login Component
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - streamlit Python package
# - ollama Python package
# - json Python package
# - time Python package
# - threading Python package
# - typing Python package
# - dataclasses Python package  
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - LoginComponent: Login component class
# - _handle_login: Handle login attempt
# - _show_register_form: Show user registration form
# - _handle_register: Handle user registration
# - _show_forgot_password_form: Show forgot password form
# - _handle_password_reset: Handle password reset
#----------------------------------------------------------------------------------------------------------------------------   

import streamlit as st
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class LoginComponent:
    """Login component for user authentication."""
    
    def __init__(self, auth_manager):
        """
        Initialize the login component.
        
        Args:
            auth_manager: Authentication manager instance
        """
        self.auth_manager = auth_manager
    
    def render(self) -> Tuple[bool, Optional[str]]:
        """
        Render the login interface.
        
        Returns:
            Tuple of (success, username) where success is True if login successful
        """
        st.markdown("""
        <div class="login-container">
            <h2 style="text-align: center; color: #667eea;">🔐 Login to TalkBridge</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Create login form
        with st.form("login_form"):
                    username = st.text_input("👤 Username", placeholder="Enter your username", key="username_login")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="password_login")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                submit_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit_button:
                return self._handle_login(username, password)
        
        # Show default credentials info
        with st.expander("ℹ️ Default Credentials"):
            st.markdown("""
            **Default Users:**
            - **Admin**: username: `admin`, password: `admin123`
            - **User**: username: `user`, password: `user123`
            
            *You can change these credentials after first login.*
            """)
        
        # Show additional options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👥 Register New User", use_container_width=True):
                st.session_state.show_register = True
        
        with col2:
            if st.button("🔑 Forgot Password", use_container_width=True):
                st.session_state.show_forgot_password = True
        
        # Handle registration
        if st.session_state.get('show_register', False):
            return self._show_register_form()
        
        # Handle forgot password
        if st.session_state.get('show_forgot_password', False):
            return self._show_forgot_password_form()
        
        return False, None
    
    def _handle_login(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Handle login attempt.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, username)
        """
        if not username or not password:
            st.error("Please enter both username and password.")
            return False, None
        
        if self.auth_manager.authenticate(username, password):
            logger.info(f"Login successful for user: {username}")
            return True, username
        else:
            st.error("❌ Invalid username or password. Please try again.")
            logger.warning(f"Login failed for user: {username}")
            return False, None
    
    def _show_register_form(self) -> Tuple[bool, Optional[str]]:
        """
        Show user registration form.
        
        Returns:
            Tuple of (success, username)
        """
        st.markdown("### 👥 Register New User")
        
        with st.form("register_form"):
            new_username = st.text_input("👤 New Username", placeholder="Enter new username", key="new_username_register")
            new_password = st.text_input("🔒 New Password", type="password", placeholder="Enter new password", key="new_password_register")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm password", key="confirm_password_register")
            email = st.text_input("📧 Email (optional)", placeholder="Enter email address")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                register_button = st.form_submit_button("✅ Register", use_container_width=True)
                cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel_button:
                st.session_state.show_register = False
                st.rerun()
            
            if register_button:
                return self._handle_register(new_username, new_password, confirm_password, email)
        
        return False, None
    
    def _handle_register(self, username: str, password: str, confirm_password: str, email: str) -> Tuple[bool, Optional[str]]:
        """
        Handle user registration.
        
        Args:
            username: New username
            password: New password
            confirm_password: Password confirmation
            email: User email
            
        Returns:
            Tuple of (success, username)
        """
        if not username or not password:
            st.error("Please enter both username and password.")
            return False, None
        
        if password != confirm_password:
            st.error("Passwords do not match.")
            return False, None
        
        if len(password) < 6:
            st.error("Password must be at least 6 characters long.")
            return False, None
        
        if self.auth_manager.add_user(username, password, email):
            st.success(f"✅ User '{username}' registered successfully!")
            st.session_state.show_register = False
            return True, username
        else:
            st.error("❌ Username already exists. Please choose a different username.")
            return False, None
    
    def _show_forgot_password_form(self) -> Tuple[bool, Optional[str]]:
        """
        Show forgot password form.
        
        Returns:
            Tuple of (success, username)
        """
        st.markdown("### 🔑 Reset Password")
        
        with st.form("forgot_password_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username", key="username_change_password")
            old_password = st.text_input("🔒 Current Password", type="password", placeholder="Enter current password", key="old_password_change")
            new_password = st.text_input("🔒 New Password", type="password", placeholder="Enter new password", key="new_password_change")
            confirm_password = st.text_input("🔒 Confirm New Password", type="password", placeholder="Confirm new password", key="confirm_password_change")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                reset_button = st.form_submit_button("🔄 Reset Password", use_container_width=True)
                cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel_button:
                st.session_state.show_forgot_password = False
                st.rerun()
            
            if reset_button:
                return self._handle_password_reset(username, old_password, new_password, confirm_password)
        
        return False, None
    
    def _handle_password_reset(self, username: str, old_password: str, new_password: str, confirm_password: str) -> Tuple[bool, Optional[str]]:
        """
        Handle password reset.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            confirm_password: Password confirmation
            
        Returns:
            Tuple of (success, username)
        """
        if not username or not old_password or not new_password:
            st.error("Please fill in all fields.")
            return False, None
        
        if new_password != confirm_password:
            st.error("New passwords do not match.")
            return False, None
        
        if len(new_password) < 6:
            st.error("New password must be at least 6 characters long.")
            return False, None
        
        if self.auth_manager.change_password(username, old_password, new_password):
            st.success("✅ Password changed successfully!")
            st.session_state.show_forgot_password = False
            return True, username
        else:
            st.error("❌ Invalid username or current password.")
            return False, None 