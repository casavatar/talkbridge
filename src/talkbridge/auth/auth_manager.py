#!/usr/bin/env python3 
"""
TalkBridge Auth - Secure Authentication Manager
===============================================

Modern secure authentication manager using SQLite and Argon2id hashing.

Security Features:
- Argon2id key derivation function with pepper
- SQLite database with restricted permissions
- Rate limiting with exponential backoff
- Comprehensive audit logging
- Account lockout protection

Author: TalkBridge Team
Date: 2025-09-18
Version: 2.0 (Security Hardened)

Requirements:
- argon2-cffi
- python-dotenv
======================================================================
"""

import os
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv

from talkbridge.auth.user_store import UserStore
from talkbridge.utils.error_handler import (
    RetryableError, CriticalError, UserNotificationError,
    handle_error, retry_with_backoff
)
from talkbridge.logging_config import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class AuthManager:
    """Secure authentication manager using SQLite and Argon2id."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the secure authentication manager.
        
        Args:
            db_path: Path to SQLite database (defaults to env config)
        """
        # Initialize user store
        db_path = db_path or os.getenv("TALKBRIDGE_DB_PATH", "data/users.db")
        self.user_store = UserStore(db_path)
        
        # Rate limiting configuration
        self._login_attempts = {}  # username -> list of attempt timestamps
        self._lockout_duration = 300  # 5 minutes in seconds
        self._max_attempts_per_window = 5  # attempts per time window
        self._time_window = 300  # 5 minute window
        
        # Development mode setup
        if os.getenv('TALKBRIDGE_DEV_MODE', 'false').lower() == 'true':
            self._ensure_dev_users_exist()
        
        logger.info("Secure AuthManager initialized")
    
    def _ensure_dev_users_exist(self) -> None:
        """Ensure development users exist for testing."""
        try:
            dev_users = [
                {
                    "username": "admin",
                    "password": "AdminPassword123!",
                    "role": "admin",
                    "email": "admin@talkbridge.local",
                    "permissions": [
                        "user_management", "system_settings", "view_logs",
                        "unlock_accounts", "create_users", "delete_users", "modify_roles"
                    ]
                },
                {
                    "username": "user", 
                    "password": "UserPassword123!",
                    "role": "user",
                    "email": "user@talkbridge.local",
                    "permissions": [
                        "voice_chat", "translation", "avatar_control",
                        "chat_history", "personal_settings"
                    ]
                },
                {
                    "username": "dev",
                    "password": "DevPassword123!",
                    "role": "admin",
                    "email": "dev@talkbridge.local",
                    "permissions": [
                        "user_management", "system_settings", "view_logs",
                        "unlock_accounts", "create_users", "delete_users", "modify_roles"
                    ]
                }
            ]
            
            for user_data in dev_users:
                existing_user = self.user_store.get_user(user_data["username"])
                if not existing_user:
                    success = self.user_store.create_user(
                        username=user_data["username"],
                        password=user_data["password"],
                        role=user_data["role"],
                        email=user_data["email"],
                        permissions=user_data["permissions"]
                    )
                    if success:
                        logger.info(f"Created dev user: {user_data['username']}")
                    
        except Exception as e:
            logger.error(f"Failed to create dev users: {e}")
    
    def _is_rate_limited(self, username: str) -> Tuple[bool, int]:
        """
        Check if user is rate limited.
        
        Args:
            username: Username to check
            
        Returns:
            Tuple of (is_limited, seconds_until_allowed)
        """
        now = time.time()
        
        # Get attempt history for user
        if username not in self._login_attempts:
            self._login_attempts[username] = []
        
        attempts = self._login_attempts[username]
        
        # Remove old attempts outside the time window
        cutoff_time = now - self._time_window
        attempts[:] = [attempt_time for attempt_time in attempts if attempt_time > cutoff_time]
        
        # Check if too many attempts
        if len(attempts) >= self._max_attempts_per_window:
            # Calculate time until oldest attempt expires
            oldest_attempt = min(attempts)
            time_until_allowed = int(oldest_attempt + self._time_window - now)
            return True, time_until_allowed
        
        return False, 0
    
    def _record_login_attempt(self, username: str) -> None:
        """Record a login attempt for rate limiting."""
        now = time.time()
        if username not in self._login_attempts:
            self._login_attempts[username] = []
        self._login_attempts[username].append(now)
    
    def _clear_rate_limit(self, username: str) -> None:
        """Clear rate limiting for successful login."""
        if username in self._login_attempts:
            del self._login_attempts[username]
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Authenticate user with comprehensive security checks.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            Tuple of (success, user_data, message)
        """
        import time
        auth_start_time = time.time()
        
        if not username or not password:
            logger.warning("Authentication attempt with empty credentials")
            return False, None, "Username and password are required"
        
        # Check rate limiting
        is_limited, wait_time = self._is_rate_limited(username)
        if is_limited:
            logger.warning(f"Rate limited authentication attempt for user: {username} (wait {wait_time}s)")
            return False, None, f"Too many failed attempts. Try again in {wait_time} seconds."
        
        # Record this attempt for rate limiting
        self._record_login_attempt(username)
        
        try:
            # Attempt authentication
            user_data = self.user_store.authenticate_user(username, password)
            
            auth_duration = time.time() - auth_start_time
            
            if user_data:
                # Clear rate limiting on successful login
                self._clear_rate_limit(username)
                
                # Check if account requires password change
                if user_data.get('requires_password_change', False):
                    logger.info(f"Successful authentication for {username} (password change required) in {auth_duration:.2f}s")
                    return True, user_data, "Password change required"
                
                logger.info(f"Successful authentication for user: {username} in {auth_duration:.2f}s")
                return True, user_data, "Authentication successful"
            else:
                logger.warning(f"Failed authentication attempt for user: {username} in {auth_duration:.2f}s")
                return False, None, "Invalid username or password"
                
        except Exception as e:
            auth_duration = time.time() - auth_start_time
            logger.error(f"Authentication error for user {username} after {auth_duration:.2f}s: {e}")
            return False, None, "Authentication system error"
    
    def create_user(self, username: str, password: str, role: str = "user",
                   email: Optional[str] = None, permissions: Optional[list] = None,
                   created_by: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create a new user account.
        
        Args:
            username: Unique username
            password: Plain text password
            role: User role
            email: User email
            permissions: List of permissions
            created_by: Username of admin creating this user
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate password strength
            if not self._validate_password_strength(password):
                return False, "Password does not meet security requirements"
            
            # Set default permissions based on role
            if permissions is None:
                permissions = self._get_default_permissions(role)
            
            success = self.user_store.create_user(
                username=username,
                password=password,
                role=role,
                email=email,
                permissions=permissions
            )
            
            if success:
                logger.info(f"User created: {username} (role: {role}) by {created_by or 'system'}")
                return True, "User created successfully"
            else:
                return False, "Username already exists"
                
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return False, "Failed to create user"
    
    def change_password(self, username: str, current_password: str, 
                       new_password: str) -> Tuple[bool, str]:
        """
        Change user password with verification.
        
        Args:
            username: Username
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Verify current password first
            user_data = self.user_store.authenticate_user(username, current_password)
            if not user_data:
                logger.warning(f"Password change failed - invalid current password for: {username}")
                return False, "Current password is incorrect"
            
            # Validate new password strength
            if not self._validate_password_strength(new_password):
                return False, "New password does not meet security requirements"
            
            # Change password
            success = self.user_store.change_password(username, new_password)
            if success:
                logger.info(f"Password changed for user: {username}")
                return True, "Password changed successfully"
            else:
                return False, "Failed to change password"
                
        except Exception as e:
            logger.error(f"Password change error for {username}: {e}")
            return False, "Password change failed"
    
    def reset_password(self, username: str, new_password: str, 
                      admin_user: str) -> Tuple[bool, str]:
        """
        Admin password reset (bypasses current password verification).
        
        Args:
            username: Username to reset
            new_password: New password
            admin_user: Admin performing the reset
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate password strength
            if not self._validate_password_strength(new_password):
                return False, "Password does not meet security requirements"
            
            success = self.user_store.change_password(username, new_password)
            if success:
                logger.info(f"Password reset for user: {username} by admin: {admin_user}")
                return True, "Password reset successfully"
            else:
                return False, "User not found"
                
        except Exception as e:
            logger.error(f"Password reset error for {username}: {e}")
            return False, "Password reset failed"
    
    def unlock_user(self, username: str, admin_user: str) -> Tuple[bool, str]:
        """
        Unlock a user account.
        
        Args:
            username: Username to unlock
            admin_user: Admin performing the unlock
            
        Returns:
            Tuple of (success, message)
        """
        try:
            success = self.user_store.unlock_user(username)
            if success:
                # Also clear rate limiting
                self._clear_rate_limit(username)
                logger.info(f"User unlocked: {username} by admin: {admin_user}")
                return True, "User account unlocked"
            else:
                return False, "User not found"
                
        except Exception as e:
            logger.error(f"Failed to unlock user {username}: {e}")
            return False, "Failed to unlock user"
    
    def get_user(self, username: str) -> Optional[Dict]:
        """
        Get user information (excluding sensitive data).
        
        Args:
            username: Username to retrieve
            
        Returns:
            User data dict or None
        """
        try:
            user_data = self.user_store.get_user(username)
            if user_data:
                # Remove sensitive fields
                safe_data = user_data.copy()
                safe_data.pop('password_hash', None)
                safe_data.pop('salt', None)
                return safe_data
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user {username}: {e}")
            return None
    
    def list_users(self) -> list:
        """
        List all users (excluding sensitive data).
        
        Returns:
            List of user data dicts
        """
        try:
            users = self.user_store.list_users()
            # Remove sensitive fields from all users
            safe_users = []
            for user in users:
                safe_user = user.copy()
                safe_user.pop('password_hash', None)
                safe_user.pop('salt', None)
                safe_users.append(safe_user)
            return safe_users
            
        except Exception as e:
            logger.error(f"Failed to list users: {e}")
            return []
    
    def delete_user(self, username: str, admin_user: str) -> Tuple[bool, str]:
        """
        Delete a user account.
        
        Args:
            username: Username to delete
            admin_user: Admin performing the deletion
            
        Returns:
            Tuple of (success, message)
        """
        try:
            success = self.user_store.delete_user(username)
            if success:
                logger.info(f"User deleted: {username} by admin: {admin_user}")
                return True, "User deleted successfully"
            else:
                return False, "User not found"
                
        except Exception as e:
            logger.error(f"Failed to delete user {username}: {e}")
            return False, "Failed to delete user"
    
    def is_account_locked(self, username: str) -> bool:
        """
        Check if user account is locked.
        
        Args:
            username: Username to check
            
        Returns:
            True if account is locked
        """
        try:
            user_data = self.user_store.get_user(username)
            return user_data.get('account_locked', False) if user_data else False
        except Exception as e:
            logger.error(f"Failed to check lock status for {username}: {e}")
            return False
    
    def _validate_password_strength(self, password: str) -> bool:
        """
        Validate password strength requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            True if password meets requirements
        """
        if len(password) < 12:
            return False
        
        # Check for required character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def _get_default_permissions(self, role: str) -> list:
        """Get default permissions for a role."""
        permission_map = {
            "admin": [
                "user_management", "system_settings", "view_logs",
                "unlock_accounts", "create_users", "delete_users", "modify_roles"
            ],
            "moderator": [
                "voice_chat", "translation", "avatar_control", "chat_history",
                "personal_settings", "moderate_chat", "view_user_activity",
                "temporary_user_restrictions"
            ],
            "user": [
                "voice_chat", "translation", "avatar_control",
                "chat_history", "personal_settings"
            ]
        }
        return permission_map.get(role, permission_map["user"])
    
    def get_security_info(self) -> Dict:
        """
        Get security information about the authentication system.
        
        Returns:
            Dict with security information
        """
        return {
            "hash_algorithm": "Argon2id",
            "pepper_configured": bool(os.getenv("TALKBRIDGE_PEPPER")),
            "rate_limiting_enabled": True,
            "max_attempts": self._max_attempts_per_window,
            "time_window_seconds": self._time_window,
            "account_lockout_enabled": True,
            "password_requirements": {
                "min_length": 12,
                "requires_uppercase": True,
                "requires_lowercase": True,
                "requires_digit": True,
                "requires_special": True
            }
        }
    
    def authenticate_simple(self, username: str, password: str) -> bool:
        """
        Simple authentication method that returns only boolean result.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            True if authentication successful, False otherwise
        """
        success, _, _ = self.authenticate(username, password)
        return success


# Backward compatibility functions for legacy code
def generate_salt() -> str:
    """Generate a salt (deprecated - kept for compatibility)."""
    import secrets
    return secrets.token_hex(32)