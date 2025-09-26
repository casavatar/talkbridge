"""
TalkBridge Authentication Utilities
===================================

Authentication utility scripts for user management, security monitoring,
and system maintenance.

Modules:
- password_config: Centralized password configuration and validation
- password_manager: Secure password creation and management
- user_generator: Production user creation with security best practices
- user_unlocker: User account unlock and recovery utility
- security_monitor: Authentication log analysis and threat detection
- encryption_verifier: Verify Argon2id encryption migration status
"""

from .password_config import PasswordConfig
from .password_manager import main as create_secure_passwords
from .user_generator import main as generate_secure_users
from .user_unlocker import UserUnlocker, unlock_specific_user, main as unlock_users
from .security_monitor import SecurityMonitor, main as run_security_analysis
from .encryption_verifier import main as verify_encryption_migration

__all__ = [
    'PasswordConfig',
    'create_secure_passwords',
    'generate_secure_users',
    'UserUnlocker',
    'unlock_specific_user',
    'unlock_users',
    'SecurityMonitor',
    'run_security_analysis',
    'verify_encryption_migration'
]