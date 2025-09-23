"""
TalkBridge Auth - User Store
============================

Secure SQLite-based user storage with Argon2id hashing and pepper support.

Author: TalkBridge Team
Date: 2025-09-18
Version: 1.0

Security Features:
- Argon2id key derivation function
- Secret pepper from environment variables
- SQLite database with restricted permissions
- Prepared statements to prevent SQL injection
======================================================================
"""

import sqlite3
import os
import stat
import secrets
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError

from talkbridge.logging_config import get_logger

logger = get_logger(__name__)


class UserStore:
    """Secure SQLite-based user storage with Argon2id hashing."""
    
    def __init__(self, db_path: str = "data/users.db"):
        """
        Initialize the user store.
        
        Args:
            db_path: Path to the SQLite database file
        """
        # Get the project root directory (going up from src/talkbridge/auth to project root)
        project_root = Path(__file__).parent.parent.parent.parent
        self.db_path = project_root / db_path
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize Argon2 password hasher with optimized parameters
        # Balanced for security and performance
        self.ph = PasswordHasher(
            time_cost=2,      # Number of iterations (reduced from 3 for better performance)
            memory_cost=32768,  # Memory usage in KiB (32 MB, reduced from 64 MB)
            parallelism=1,    # Number of parallel threads
            hash_len=32,      # Length of hash in bytes
            salt_len=16       # Length of salt in bytes
        )
        
        # Initialize database
        self._init_database()
        self._set_secure_permissions()
    
    def _get_pepper(self) -> str:
        """
        Get the secret pepper from environment variables.
        
        Returns:
            Secret pepper string
            
        Raises:
            ValueError: If pepper is not configured
        """
        pepper = os.getenv("TALKBRIDGE_PEPPER")
        if not pepper:
            raise ValueError(
                "TALKBRIDGE_PEPPER environment variable not set. "
                "Please configure your .env file with a secure random pepper."
            )
        return pepper
    
    def _init_database(self) -> None:
        """Initialize the SQLite database with secure schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Create users table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'user',
                        email TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        account_locked BOOLEAN DEFAULT FALSE,
                        failed_login_attempts INTEGER DEFAULT 0,
                        requires_password_change BOOLEAN DEFAULT TRUE,
                        security_level TEXT DEFAULT 'medium',
                        two_factor_enabled BOOLEAN DEFAULT FALSE,
                        session_timeout INTEGER DEFAULT 1800,
                        last_failed_login TIMESTAMP
                    )
                """)
                
                # Create permissions table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_permissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        permission TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                        UNIQUE (user_id, permission)
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_username ON users (username)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_permissions ON user_permissions (user_id)")
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _set_secure_permissions(self) -> None:
        """Set secure file permissions (600) on the database file."""
        try:
            # Set permissions to read/write for owner only
            os.chmod(self.db_path, stat.S_IRUSR | stat.S_IWUSR)
            logger.info(f"Set secure permissions (600) on {self.db_path}")
        except OSError as e:
            logger.error(f"Failed to set secure permissions on {self.db_path}: {e}")
            raise
    
    def _hash_password(self, password: str) -> Tuple[str, str]:
        """
        Hash password using Argon2id with pepper.
        
        Args:
            password: Plain text password
            
        Returns:
            Tuple of (password_hash, salt)
            
        Raises:
            HashingError: If password hashing fails
        """
        try:
            pepper = self._get_pepper()
            # Generate a unique salt for this password
            salt = secrets.token_hex(16)
            # Combine password with pepper and salt
            password_with_pepper = password + pepper + salt
            # Hash with Argon2id
            password_hash = self.ph.hash(password_with_pepper)
            return password_hash, salt
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise HashingError(f"Failed to hash password: {e}")
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            stored_hash: Stored Argon2id hash
            salt: Salt used for this password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            pepper = self._get_pepper()
            password_with_pepper = password + pepper + salt
            self.ph.verify(stored_hash, password_with_pepper)
            return True
        except VerifyMismatchError:
            return False
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def create_user(self, username: str, password: str, role: str = "user", 
                   email: Optional[str] = None, permissions: Optional[List[str]] = None) -> bool:
        """
        Create a new user with secure password hashing.
        
        Args:
            username: Unique username
            password: Plain text password
            role: User role (admin, moderator, user)
            email: User email address
            permissions: List of permission strings
            
        Returns:
            True if user created successfully, False if username exists
        """
        try:
            # Hash password with Argon2id + pepper
            password_hash, salt = self._hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                # Check if user already exists
                cursor = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    logger.warning(f"Attempted to create duplicate user: {username}")
                    return False
                
                # Insert user
                cursor = conn.execute("""
                    INSERT INTO users (
                        username, password_hash, salt, role, email,
                        password_changed_at, security_level, session_timeout
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    username, password_hash, salt, role, email,
                    datetime.now().isoformat(),
                    "high" if role == "admin" else "medium",
                    3600 if role == "admin" else 1800
                ))
                
                user_id = cursor.lastrowid
                
                # Add permissions
                if permissions:
                    permission_data = [(user_id, perm) for perm in permissions]
                    conn.executemany(
                        "INSERT INTO user_permissions (user_id, permission) VALUES (?, ?)",
                        permission_data
                    )
                
                conn.commit()
                logger.info(f"Created user: {username} with role: {role}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Database error creating user {username}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user with secure password verification.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            User data dict if authentication successful, None otherwise
        """
        import time
        auth_start_time = time.time()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get user data
                cursor = conn.execute("""
                    SELECT * FROM users WHERE username = ? AND account_locked = FALSE
                """, (username,))
                
                user_row = cursor.fetchone()
                if not user_row:
                    db_duration = time.time() - auth_start_time
                    logger.warning(f"Authentication failed for user: {username} (not found or locked) - DB lookup: {db_duration:.3f}s")
                    return None
                
                # Verify password (this is the slow operation)
                verify_start_time = time.time()
                if not self._verify_password(password, user_row['password_hash'], user_row['salt']):
                    # Update failed login attempts
                    self._update_failed_login(username)
                    verify_duration = time.time() - verify_start_time
                    total_duration = time.time() - auth_start_time
                    logger.warning(f"Authentication failed for user: {username} (invalid password) - Verify: {verify_duration:.3f}s, Total: {total_duration:.3f}s")
                    return None
                
                verify_duration = time.time() - verify_start_time
                
                # Get user permissions
                perm_cursor = conn.execute("""
                    SELECT permission FROM user_permissions WHERE user_id = ?
                """, (user_row['id'],))
                permissions = [row[0] for row in perm_cursor.fetchall()]
                
                # Reset failed login attempts and update last login
                conn.execute("""
                    UPDATE users SET 
                        failed_login_attempts = 0,
                        last_login = ?,
                        last_failed_login = NULL
                    WHERE username = ?
                """, (datetime.now().isoformat(), username))
                
                conn.commit()
                
                # Convert to dict and add permissions
                user_data = dict(user_row)
                user_data['permissions'] = permissions
                
                total_duration = time.time() - auth_start_time
                logger.info(f"Successful authentication for user: {username} - Verify: {verify_duration:.3f}s, Total: {total_duration:.3f}s")
                return user_data
                
        except sqlite3.Error as e:
            total_duration = time.time() - auth_start_time
            logger.error(f"Database error during authentication for {username} after {total_duration:.3f}s: {e}")
            return None
        except Exception as e:
            total_duration = time.time() - auth_start_time
            logger.error(f"Authentication error for {username} after {total_duration:.3f}s: {e}")
            return None
    
    def _update_failed_login(self, username: str) -> None:
        """Update failed login attempts and potentially lock account."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Increment failed attempts
                conn.execute("""
                    UPDATE users SET 
                        failed_login_attempts = failed_login_attempts + 1,
                        last_failed_login = ?
                    WHERE username = ?
                """, (datetime.now().isoformat(), username))
                
                # Check if account should be locked (after 5 failed attempts)
                cursor = conn.execute("""
                    SELECT failed_login_attempts FROM users WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                if row and row[0] >= 5:
                    conn.execute("""
                        UPDATE users SET account_locked = TRUE WHERE username = ?
                    """, (username,))
                    logger.warning(f"Account locked due to failed attempts: {username}")
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Failed to update failed login for {username}: {e}")
    
    def unlock_user(self, username: str) -> bool:
        """
        Unlock a user account and reset failed login attempts.
        
        Args:
            username: Username to unlock
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE users SET 
                        account_locked = FALSE,
                        failed_login_attempts = 0,
                        last_failed_login = NULL
                    WHERE username = ?
                """, (username,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Unlocked user account: {username}")
                    return True
                else:
                    logger.warning(f"User not found for unlock: {username}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"Failed to unlock user {username}: {e}")
            return False
    
    def change_password(self, username: str, new_password: str) -> bool:
        """
        Change user password with secure hashing.
        
        Args:
            username: Username
            new_password: New plain text password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            password_hash, salt = self._hash_password(new_password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE users SET 
                        password_hash = ?,
                        salt = ?,
                        password_changed_at = ?,
                        requires_password_change = FALSE
                    WHERE username = ?
                """, (password_hash, salt, datetime.now().isoformat(), username))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Password changed for user: {username}")
                    return True
                else:
                    logger.warning(f"User not found for password change: {username}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to change password for {username}: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """
        Get user data by username.
        
        Args:
            username: Username to retrieve
            
        Returns:
            User data dict if found, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
                user_row = cursor.fetchone()
                
                if not user_row:
                    return None
                
                # Get permissions
                perm_cursor = conn.execute("""
                    SELECT permission FROM user_permissions WHERE user_id = ?
                """, (user_row['id'],))
                permissions = [row[0] for row in perm_cursor.fetchall()]
                
                user_data = dict(user_row)
                user_data['permissions'] = permissions
                return user_data
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get user {username}: {e}")
            return None
    
    def list_users(self) -> List[Dict]:
        """
        List all users (excluding sensitive data).
        
        Returns:
            List of user data dicts
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT id, username, role, email, created_at, last_login,
                           account_locked, failed_login_attempts, security_level,
                           two_factor_enabled, requires_password_change
                    FROM users ORDER BY username
                """)
                
                users = []
                for row in cursor.fetchall():
                    user_data = dict(row)
                    
                    # Get permissions for this user
                    perm_cursor = conn.execute("""
                        SELECT permission FROM user_permissions WHERE user_id = ?
                    """, (user_data['id'],))
                    user_data['permissions'] = [p[0] for p in perm_cursor.fetchall()]
                    
                    users.append(user_data)
                
                return users
                
        except sqlite3.Error as e:
            logger.error(f"Failed to list users: {e}")
            return []
    
    def delete_user(self, username: str) -> bool:
        """
        Delete a user account.
        
        Args:
            username: Username to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM users WHERE username = ?", (username,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Deleted user: {username}")
                    return True
                else:
                    logger.warning(f"User not found for deletion: {username}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"Failed to delete user {username}: {e}")
            return False