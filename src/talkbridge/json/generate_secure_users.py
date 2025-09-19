#!/usr/bin/env python3
"""
TalkBridge UI - Generate Secure Users
=====================================

Generate secure users module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- Flask
======================================================================
Functions:
- generate_secure_password: Generate a cryptographically secure password.
- generate_salt: Generate a cryptographically secure salt.
- hash_password_with_salt: Hash password using SHA-256 with salt.
- create_user_data: Create user data with secure password and salt.
- generate_users_json: Generate the complete users.json file with secure passwords.
======================================================================
"""

import json
import hashlib
import secrets
import string
from datetime import datetime
from pathlib import Path
from talkbridge.logging_config import get_logger
from talkbridge.ui.notifier import notifier

logger = get_logger(__name__)

def generate_secure_password(length: int = 16) -> str:
    """Generate a cryptographically secure password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_salt() -> str:
    """Generate a cryptographically secure salt."""
    return secrets.token_hex(16)

def hash_password_with_salt(password: str, salt: str) -> str:
    """Hash password using SHA-256 with salt."""
    salted_password = password + salt
    return hashlib.sha256(salted_password.encode()).hexdigest()

def create_user_data(username: str, role: str, email: str, password_length: int = 16) -> dict:
    """Create user data with secure password and salt."""
    password = generate_secure_password(password_length)
    salt = generate_salt()
    hashed_password = hash_password_with_salt(password, salt)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Define permissions based on role
    permissions_map = {
        "admin": [
            "user_management", "system_settings", "view_logs", "unlock_accounts",
            "create_users", "delete_users", "modify_roles"
        ],
        "user": [
            "voice_chat", "translation", "avatar_control", "chat_history", "personal_settings"
        ],
        "moderator": [
            "voice_chat", "translation", "avatar_control", "chat_history", "personal_settings",
            "moderate_chat", "view_user_activity", "unlock_user_accounts"
        ],
        "guest": [
            "voice_chat", "translation", "avatar_control", "personal_settings"
        ],
        "translator": [
            "voice_chat", "translation", "avatar_control", "chat_history", "personal_settings",
            "advanced_translation", "translation_history", "language_management"
        ],
        "developer": [
            "voice_chat", "translation", "avatar_control", "chat_history", "personal_settings",
            "system_settings", "view_logs", "debug_mode", "api_access", "development_tools"
        ],
        "analyst": [
            "voice_chat", "translation", "avatar_control", "chat_history", "personal_settings",
            "view_analytics", "export_data", "view_user_activity", "translation_analytics"
        ],
        "support": [
            "voice_chat", "translation", "avatar_control", "chat_history", "personal_settings",
            "view_user_activity", "unlock_user_accounts", "reset_user_passwords", "view_support_tickets"
        ]
    }
    
    # Define security levels and session timeouts
    security_config = {
        "admin": {"level": "high", "timeout": 3600},
        "user": {"level": "medium", "timeout": 1800},
        "moderator": {"level": "medium", "timeout": 2400},
        "guest": {"level": "low", "timeout": 900},
        "translator": {"level": "medium", "timeout": 2400},
        "developer": {"level": "high", "timeout": 7200},
        "analyst": {"level": "medium", "timeout": 3600},
        "support": {"level": "medium", "timeout": 2400}
    }
    
    user_data = {
        "password": hashed_password,
        "salt": salt,
        "role": role,
        "email": email,
        "created_at": current_time,
        "last_login": None,
        "password_changed_at": current_time,
        "account_locked": False,
        "failed_login_attempts": 0,
        "requires_password_change": True,
        "permissions": permissions_map.get(role, ["voice_chat", "translation", "avatar_control"]),
        "security_level": security_config.get(role, {"level": "medium", "timeout": 1800})["level"],
        "two_factor_enabled": False,
        "session_timeout": security_config.get(role, {"level": "medium", "timeout": 1800})["timeout"]
    }
    
    return user_data, password

def generate_users_json():
    """Generate the complete users.json file with secure passwords."""
    
    # Define users to create
    users_to_create = {
        "admin": {"role": "admin", "email": "admin@talkbridge.local", "password_length": 20},
        "user": {"role": "user", "email": "user@talkbridge.local", "password_length": 16},
        "moderator": {"role": "moderator", "email": "moderator@talkbridge.local", "password_length": 16},
        "guest": {"role": "guest", "email": "guest@talkbridge.local", "password_length": 16},
        "translator": {"role": "translator", "email": "translator@talkbridge.local", "password_length": 16},
        "developer": {"role": "developer", "email": "developer@talkbridge.local", "password_length": 20},
        "analyst": {"role": "analyst", "email": "analyst@talkbridge.local", "password_length": 16},
        "support": {"role": "support", "email": "support@talkbridge.local", "password_length": 16},
        "test_user": {"role": "user", "email": "test@talkbridge.local", "password_length": 16},
        "demo_user": {"role": "user", "email": "demo@talkbridge.local", "password_length": 16}
    }
    
    users_data = {}
    passwords = {}
    
    logger.info("🔐 Generating secure user accounts...")
    logger.info("=" * 50)
    
    for username, config in users_to_create.items():
        user_data, password = create_user_data(
            username=username,
            role=config["role"],
            email=config["email"],
            password_length=config["password_length"]
        )
        
        users_data[username] = user_data
        passwords[username] = password
        
        logger.info(f"Created user: {username}")
        logger.info(f"   Role: {config['role']}")
        logger.info(f"   Email: {config['email']}")
        logger.debug(f"   Salt: {user_data['salt'][:8]}...")
        logger.info(f"   Security Level: {user_data['security_level']}")
        
        # Notify user of account creation
        notifier.notify_info(f"Created user '{username}' with role '{config['role']}'")
    
    # Save to users.json
    json_file = Path(__file__).parent / "users.json"
    with open(json_file, 'w') as f:
        json.dump(users_data, f, indent=2)
    
    logger.info(f"Saved secure users to: {json_file}")
    notifier.notify_info(f"Users database saved to {json_file}")
    
    # Save passwords to a separate file for reference (development only)
    passwords_file = Path(__file__).parent / "passwords_dev_only.txt"
    with open(passwords_file, 'w') as f:
        f.write("=== TALKBRIDGE USER PASSWORDS (DEVELOPMENT ONLY) ===\n")
        f.write("=== DELETE THIS FILE IN PRODUCTION ===\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for username, password in passwords.items():
            f.write(f"{username}: {password}\n")
    
    logger.info(f"Saved passwords to: {passwords_file}")
    notifier.notify_warn("WARNING: Delete passwords_dev_only.txt in production!")
    
    # Print summary
    logger.info("Generation Summary:")
    logger.info(f"   Total users created: {len(users_data)}")
    logger.info(f"   Roles: {set(config['role'] for config in users_to_create.values())}")
    logger.info(f"   Security levels: {set(user_data['security_level'] for user_data in users_data.values())}")
    logger.info("Security features enabled:")
    logger.info("- All users require password change on first login")
    logger.info("- Account locking enabled after 5 failed attempts")
    logger.info("- Enhanced security with salted password hashing")
    
    notifier.notify_info(f"Successfully generated {len(users_data)} secure user accounts")

if __name__ == "__main__":
    generate_users_json() 