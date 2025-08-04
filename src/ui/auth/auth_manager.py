#! /usr/bin/env python3 
#-------------------------------------------------------------------------------------------------
# description: Authentication Manager
#-------------------------------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#-------------------------------------------------------------------------------------------------

# requirements:
# - json Python package
# - hashlib Python package
# - os Python package
# - pathlib Python package
# - typing Python package
#-------------------------------------------------------------------------------------------------
# functions:
# - AuthManager: Authentication manager class
# - _load_users: Load users from JSON file
# - _create_default_users: Create secure default users with salted passwords
# - _save_users: Save users to JSON file
# - _hash_password: Hash password using SHA-256 (legacy)
# - _hash_password_with_salt: Hash password with salt for enhanced security
# - _verify_password_with_salt: Verify password against salted hash
# - _update_login_success: Update user data after successful login
# - _update_login_failure: Update user data after failed login attempt
# - authenticate: Authenticate user with username and password
# - add_user: Add a new user to the system with enhanced security
# - remove_user: Remove a user from the system
# - change_password: Change user password with enhanced security
# - get_user_info: Get user information (without password)
# - list_users: Get list of all usernames
# - get_user_role: Get user role
# - is_admin: Check if user is admin
# - is_account_locked: Check if user account is locked
# - unlock_account: Unlock a user account
# - requires_password_change: Check if user requires password change
#-------------------------------------------------------------------------------------------------  

import json
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages user authentication using local JSON file."""
    
    def __init__(self, users_file: str = "../ui/json/users.json"):
        """
        Initialize the authentication manager.
        
        Args:
            users_file: Path to the JSON file containing user data
        """
        self.users_file = Path(__file__).parent.parent / users_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict[str, Dict]:
        """
        Load users from JSON file or create default if not exists.
        
        Returns:
            Dict containing user data
        """
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    users = json.load(f)
                logger.info(f"Loaded {len(users)} users from {self.users_file}")
                return users
            except Exception as e:
                logger.error(f"Failed to load users file: {e}")
                return self._create_default_users()
        else:
            return self._create_default_users()
    
    def _create_default_users(self) -> Dict[str, Dict]:
        """
        Create default users with enhanced security.
        
        Returns:
            Dict containing default user data
        """
        from datetime import datetime
        import secrets
        import string
        
        def generate_secure_password(length: int = 16) -> str:
            """Generate a cryptographically secure password."""
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(alphabet) for _ in range(length))
        
        def generate_salt() -> str:
            """Generate a cryptographically secure salt."""
            return secrets.token_hex(16)
        
        # Generate secure default passwords
        admin_password = generate_secure_password(20)  # Longer password for admin
        user_password = generate_secure_password(16)
        
        # Generate unique salts for each user
        admin_salt = generate_salt()
        user_salt = generate_salt()
        
        # Create timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        default_users = {
            "admin": {
                "password": self._hash_password_with_salt(admin_password, admin_salt),
                "salt": admin_salt,
                "role": "admin",
                "email": "admin@talkbridge.local",
                "created_at": current_time,
                "last_login": None,
                "password_changed_at": current_time,
                "account_locked": False,
                "failed_login_attempts": 0,
                "requires_password_change": True  # Force password change on first login
            },
            "user": {
                "password": self._hash_password_with_salt(user_password, user_salt),
                "salt": user_salt,
                "role": "user",
                "email": "user@talkbridge.local",
                "created_at": current_time,
                "last_login": None,
                "password_changed_at": current_time,
                "account_locked": False,
                "failed_login_attempts": 0,
                "requires_password_change": True  # Force password change on first login
            }
        }
        
        # Save default users
        self._save_users(default_users)
        
        # Log the generated passwords securely (only in development)
        if os.getenv('TALKBRIDGE_DEV_MODE', 'false').lower() == 'true':
            logger.info("=== DEFAULT USER CREDENTIALS (DEVELOPMENT ONLY) ===")
            logger.info(f"Admin username: admin")
            logger.info(f"Admin password: {admin_password}")
            logger.info(f"User username: user")
            logger.info(f"User password: {user_password}")
            logger.info("=== CHANGE THESE PASSWORDS IMMEDIATELY ===")
        else:
            logger.warning("Default users created with secure passwords. Check logs for credentials in development mode.")
        
        logger.info("Created secure default users with enhanced security features")
        return default_users
    
    def _save_users(self, users: Dict[str, Dict]) -> None:
        """
        Save users to JSON file.
        
        Args:
            users: User data to save
        """
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            logger.info(f"Saved users to {self.users_file}")
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256 (legacy method for backward compatibility).
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _hash_password_with_salt(self, password: str, salt: str) -> str:
        """
        Hash password using SHA-256 with salt for enhanced security.
        
        Args:
            password: Plain text password
            salt: Cryptographic salt
            
        Returns:
            Hashed password
        """
        # Combine password and salt
        salted_password = password + salt
        return hashlib.sha256(salted_password.encode()).hexdigest()
    
    def _verify_password_with_salt(self, password: str, salt: str, hashed_password: str) -> bool:
        """
        Verify password against salted hash.
        
        Args:
            password: Plain text password to verify
            salt: Cryptographic salt
            hashed_password: Stored hashed password
            
        Returns:
            True if password matches
        """
        return self._hash_password_with_salt(password, salt) == hashed_password
    
    def _update_login_success(self, username: str) -> None:
        """
        Update user data after successful login.
        
        Args:
            username: Username of the user who logged in
        """
        from datetime import datetime
        
        if username in self.users:
            self.users[username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.users[username]['failed_login_attempts'] = 0
            self.users[username]['account_locked'] = False
            self._save_users(self.users)
    
    def _update_login_failure(self, username: str) -> None:
        """
        Update user data after failed login attempt.
        
        Args:
            username: Username of the user who failed to log in
        """
        if username in self.users:
            self.users[username]['failed_login_attempts'] = self.users[username].get('failed_login_attempts', 0) + 1
            
            # Lock account after 5 failed attempts
            if self.users[username]['failed_login_attempts'] >= 5:
                self.users[username]['account_locked'] = True
                logger.warning(f"Account locked for user '{username}' due to multiple failed login attempts")
            
            self._save_users(self.users)
    
    def is_account_locked(self, username: str) -> bool:
        """
        Check if user account is locked.
        
        Args:
            username: Username to check
            
        Returns:
            True if account is locked
        """
        if username in self.users:
            return self.users[username].get('account_locked', False)
        return False
    
    def unlock_account(self, username: str) -> bool:
        """
        Unlock a user account.
        
        Args:
            username: Username to unlock
            
        Returns:
            True if account unlocked successfully
        """
        if username in self.users:
            self.users[username]['account_locked'] = False
            self.users[username]['failed_login_attempts'] = 0
            self._save_users(self.users)
            logger.info(f"Unlocked account for user '{username}'")
            return True
        return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            True if authentication successful, False otherwise
        """
        if username not in self.users:
            logger.warning(f"Authentication failed: user '{username}' not found")
            return False
        
        # Check if account is locked
        if self.is_account_locked(username):
            logger.warning(f"Authentication failed: account locked for user '{username}'")
            return False
        
        user = self.users[username]
        
        # Check if user has salt (new secure system)
        if 'salt' in user:
            # Use salted password verification
            if self._verify_password_with_salt(password, user['salt'], user['password']):
                self._update_login_success(username)
                logger.info(f"Authentication successful for user '{username}' (salted)")
                return True
            else:
                self._update_login_failure(username)
                logger.warning(f"Authentication failed: invalid password for user '{username}'")
                return False
        else:
            # Legacy password verification (backward compatibility)
            hashed_password = self._hash_password(password)
            if user['password'] == hashed_password:
                self._update_login_success(username)
                logger.info(f"Authentication successful for user '{username}' (legacy)")
                return True
            else:
                self._update_login_failure(username)
                logger.warning(f"Authentication failed: invalid password for user '{username}'")
                return False
    
    def add_user(self, username: str, password: str, email: str = "", role: str = "user") -> bool:
        """
        Add a new user to the system with enhanced security.
        
        Args:
            username: Username for the new user
            password: Plain text password
            email: User email (optional)
            role: User role (default: "user")
            
        Returns:
            True if user added successfully, False otherwise
        """
        if username in self.users:
            logger.warning(f"User '{username}' already exists")
            return False
        
        from datetime import datetime
        import secrets
        
        # Generate salt for new user
        salt = secrets.token_hex(16)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_user = {
            "password": self._hash_password_with_salt(password, salt),
            "salt": salt,
            "role": role,
            "email": email,
            "created_at": current_time,
            "last_login": None,
            "password_changed_at": current_time,
            "account_locked": False,
            "failed_login_attempts": 0,
            "requires_password_change": False
        }
        
        self.users[username] = new_user
        self._save_users(self.users)
        
        logger.info(f"Added new secure user '{username}'")
        return True
    
    def remove_user(self, username: str) -> bool:
        """
        Remove a user from the system.
        
        Args:
            username: Username to remove
            
        Returns:
            True if user removed successfully, False otherwise
        """
        if username not in self.users:
            logger.warning(f"User '{username}' not found")
            return False
        
        if username == "admin":
            logger.warning("Cannot remove admin user")
            return False
        
        del self.users[username]
        self._save_users(self.users)
        
        logger.info(f"Removed user '{username}'")
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change user password with enhanced security.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully, False otherwise
        """
        if not self.authenticate(username, old_password):
            logger.warning(f"Password change failed: invalid credentials for user '{username}'")
            return False
        
        from datetime import datetime
        import secrets
        
        # Generate new salt for password change
        new_salt = secrets.token_hex(16)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update user with new salted password
        self.users[username]['password'] = self._hash_password_with_salt(new_password, new_salt)
        self.users[username]['salt'] = new_salt
        self.users[username]['password_changed_at'] = current_time
        self.users[username]['requires_password_change'] = False
        
        self._save_users(self.users)
        
        logger.info(f"Changed password for user '{username}' with new salt")
        return True
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Get user information (without password).
        
        Args:
            username: Username
            
        Returns:
            User information dict or None if user not found
        """
        if username not in self.users:
            return None
        
        user_info = self.users[username].copy()
        user_info.pop('password', None)  # Remove password from response
        user_info['username'] = username
        return user_info
    
    def list_users(self) -> List[str]:
        """
        Get list of all usernames.
        
        Returns:
            List of usernames
        """
        return list(self.users.keys())
    
    def get_user_role(self, username: str) -> Optional[str]:
        """
        Get user role.
        
        Args:
            username: Username
            
        Returns:
            User role or None if user not found
        """
        if username not in self.users:
            return None
        
        return self.users[username].get('role', 'user')
    
    def is_admin(self, username: str) -> bool:
        """
        Check if user is admin.
        
        Args:
            username: Username
            
        Returns:
            True if user is admin, False otherwise
        """
        return self.get_user_role(username) == "admin"
    
    def requires_password_change(self, username: str) -> bool:
        """
        Check if user requires password change.
        
        Args:
            username: Username to check
            
        Returns:
            True if user requires password change
        """
        if username in self.users:
            return self.users[username].get('requires_password_change', False)
        return False 