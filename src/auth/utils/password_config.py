#!/usr/bin/env python3
"""
TalkBridge Authentication Password Configuration
===============================================

Secure password configuration for all authentication utilities.
NO HARD-CODED PASSWORDS - All passwords must be provided via environment variables.
"""

from typing import Dict, List, Tuple, Optional
import secrets
import string
import os
import logging

logger = logging.getLogger(__name__)


class PasswordConfig:
    """Secure password configuration and generation."""

    # Security requirements
    MIN_LENGTH = 16  # Increased from 12 for better security
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True

    # Special characters allowed
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # User role definitions (NO PASSWORDS)
    USER_ROLES = {
        "admin": {
            "email": "admin@talkbridge.secure",
            "security_level": "high",
            "permissions": [
                "user_management", "system_settings", "view_logs",
                "unlock_accounts", "create_users", "delete_users",
                "modify_roles", "backup_restore", "security_audit"
            ],
            "description": "System administrator with full privileges"
        },
        "moderator": {
            "email": "moderator@talkbridge.secure",
            "security_level": "high",
            "permissions": [
                "moderate_chat", "view_user_activity", "temporary_user_restrictions",
                "content_management", "user_warnings", "chat_history_review"
            ],
            "description": "Content and user moderation"
        },
        "support": {
            "email": "support@talkbridge.secure",
            "security_level": "medium",
            "permissions": [
                "view_user_activity", "user_assistance", "basic_troubleshooting",
                "ticket_management", "user_communication"
            ],
            "description": "Customer support representative"
        },
        "analyst": {
            "email": "analyst@talkbridge.secure",
            "security_level": "medium",
            "permissions": [
                "view_analytics", "generate_reports", "data_export",
                "performance_monitoring", "usage_statistics"
            ],
            "description": "Data analyst and reporting"
        },
        "developer": {
            "email": "developer@talkbridge.secure",
            "security_level": "high",
            "permissions": [
                "system_debug", "log_access", "api_testing",
                "development_tools", "feature_flags"
            ],
            "description": "Software developer with debug access"
        },
        "translator": {
            "email": "translator@talkbridge.secure",
            "security_level": "medium",
            "permissions": [
                "translation_management", "language_packs", "content_localization",
                "translation_review", "linguistic_validation"
            ],
            "description": "Language and translation specialist"
        },
        "guest": {
            "email": "guest@talkbridge.secure",
            "security_level": "low",
            "permissions": [
                "basic_voice_chat", "limited_translation", "read_only_access"
            ],
            "description": "Limited access guest account"
        },
        "demo": {
            "email": "demo@talkbridge.secure",
            "security_level": "low",
            "permissions": [
                "voice_chat", "translation", "demo_features",
                "limited_avatar_control", "basic_settings"
            ],
            "description": "Demonstration account for showcasing features"
        },
        "auditor": {
            "email": "auditor@talkbridge.secure",
            "security_level": "high",
            "permissions": [
                "security_audit", "log_review", "compliance_check",
                "access_monitoring", "audit_reports"
            ],
            "description": "Security auditor with read-only monitoring access"
        },
        "operator": {
            "email": "operator@talkbridge.secure",
            "security_level": "medium",
            "permissions": [
                "system_monitoring", "service_restart", "basic_maintenance",
                "health_checks", "performance_alerts"
            ],
            "description": "System operator for monitoring and basic maintenance"
        }
    }

    @classmethod
    def get_user_definitions(cls) -> List[Dict]:
        """Get complete user definitions WITHOUT passwords.

        Passwords must be provided via environment variables:
        - TALKBRIDGE_PASSWORD_ADMIN
        - TALKBRIDGE_PASSWORD_MODERATOR
        - etc.
        """
        users = []

        for username, role_data in cls.USER_ROLES.items():
            user_def = {
                "username": username,
                "role": username,
                **role_data
            }
            users.append(user_def)

        return users

    @classmethod
    def get_password_from_env(cls, username: str) -> Optional[str]:
        """Get password for a user from environment variables.

        Args:
            username: Username to get password for

        Returns:
            Password from environment or None if not set
        """
        env_var = f"TALKBRIDGE_PASSWORD_{username.upper()}"
        password = os.getenv(env_var)

        if not password:
            logger.warning(f"No password found in environment variable: {env_var}")
            return None

        # Validate password meets requirements
        is_valid, issues = cls.validate_password(password)
        if not is_valid:
            logger.error(f"Password for {username} does not meet security requirements: {issues}")
            return None

        return password

    @classmethod
    def get_all_required_env_vars(cls) -> List[str]:
        """Get list of all required environment variables for passwords."""
        return [f"TALKBRIDGE_PASSWORD_{username.upper()}" for username in cls.USER_ROLES.keys()]

    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against security requirements.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        if len(password) < cls.MIN_LENGTH:
            issues.append(f"Password must be at least {cls.MIN_LENGTH} characters")

        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")

        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")

        if cls.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")

        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARS for c in password):
            issues.append(f"Password must contain at least one special character: {cls.SPECIAL_CHARS}")

        return len(issues) == 0, issues

    @classmethod
    def generate_secure_password(cls, length: int = 20) -> str:
        """
        Generate a cryptographically secure random password.

        Args:
            length: Desired password length (minimum 16)

        Returns:
            Secure random password string
        """
        if length < cls.MIN_LENGTH:
            length = cls.MIN_LENGTH

        # Ensure we have at least one character from each required category
        password_chars = []

        if cls.REQUIRE_UPPERCASE:
            password_chars.append(secrets.choice(string.ascii_uppercase))
        if cls.REQUIRE_LOWERCASE:
            password_chars.append(secrets.choice(string.ascii_lowercase))
        if cls.REQUIRE_DIGITS:
            password_chars.append(secrets.choice(string.digits))
        if cls.REQUIRE_SPECIAL:
            password_chars.append(secrets.choice(cls.SPECIAL_CHARS))

        # Fill the rest with random characters from all categories
        all_chars = string.ascii_letters + string.digits + cls.SPECIAL_CHARS
        remaining_length = length - len(password_chars)

        for _ in range(remaining_length):
            password_chars.append(secrets.choice(all_chars))

        # Shuffle the password to avoid predictable patterns
        secrets.SystemRandom().shuffle(password_chars)

        return ''.join(password_chars)

    @classmethod
    def get_password_for_user(cls, username: str) -> Optional[str]:
        """Get password for a specific username from environment variables.

        Returns None if no password is configured.
        """
        return cls.get_password_from_env(username)

    @classmethod
    def generate_password_setup_script(cls) -> str:
        """Generate a script to set up environment variables for all users.

        Returns:
            Shell script content for setting environment variables
        """
        script_lines = [
            "#!/bin/bash",
            "# TalkBridge Secure Password Setup",
            "# Generate secure passwords and set environment variables",
            "# DO NOT COMMIT THIS SCRIPT TO VERSION CONTROL!",
            "",
            "echo 'Setting up secure passwords for TalkBridge...'",
            ""
        ]

        for username in cls.USER_ROLES.keys():
            env_var = f"TALKBRIDGE_PASSWORD_{username.upper()}"
            secure_password = cls.generate_secure_password()
            script_lines.extend([
                f"# Password for {username} ({cls.USER_ROLES[username]['description']})",
                f"export {env_var}='{secure_password}'",
                f"echo 'Set password for {username}'",
                ""
            ])

        script_lines.extend([
            "echo 'All passwords have been set in environment variables.'",
            "echo 'Remember to add these to your secure environment configuration.'"
        ])

        return "\n".join(script_lines)

    @classmethod
    def generate_password_setup_script_powershell(cls) -> str:
        """Generate a PowerShell script to set up environment variables for all users.

        Returns:
            PowerShell script content for setting environment variables
        """
        script_lines = [
            "# TalkBridge Secure Password Setup - PowerShell",
            "# ==============================================",
            "# Generate secure passwords and set environment variables",
            "# DO NOT COMMIT THIS SCRIPT TO VERSION CONTROL!",
            "",
            "Write-Host 'Setting up secure passwords for TalkBridge...' -ForegroundColor Green",
            "Write-Host ''"
        ]

        for username in cls.USER_ROLES.keys():
            env_var = f"TALKBRIDGE_PASSWORD_{username.upper()}"
            secure_password = cls.generate_secure_password()
            script_lines.extend([
                f"# Password for {username} ({cls.USER_ROLES[username]['description']})",
                f"$env:{env_var} = '{secure_password}'",
                f"[System.Environment]::SetEnvironmentVariable('{env_var}', '{secure_password}', 'User')",
                f"Write-Host 'Set password for {username}' -ForegroundColor Cyan",
                ""
            ])

        script_lines.extend([
            "Write-Host 'All passwords have been set in environment variables.' -ForegroundColor Green",
            "Write-Host 'Environment variables are set for current session and user profile.' -ForegroundColor Yellow",
            "Write-Host 'Restart PowerShell to ensure all variables are loaded.' -ForegroundColor Yellow"
        ])

        return "\n".join(script_lines)


def main():
    """Display secure password configuration information."""

    print("🔐 TalkBridge Secure Password Configuration")
    print("=" * 50)

    print(f"\n📋 Security Requirements:")
    print(f"   Minimum Length: {PasswordConfig.MIN_LENGTH}")
    print(f"   Uppercase Required: {PasswordConfig.REQUIRE_UPPERCASE}")
    print(f"   Lowercase Required: {PasswordConfig.REQUIRE_LOWERCASE}")
    print(f"   Digits Required: {PasswordConfig.REQUIRE_DIGITS}")
    print(f"   Special Chars Required: {PasswordConfig.REQUIRE_SPECIAL}")
    print(f"   Allowed Special Chars: {PasswordConfig.SPECIAL_CHARS}")

    print(f"\n👥 Required Environment Variables:")
    required_vars = PasswordConfig.get_all_required_env_vars()
    for env_var in required_vars:
        username = env_var.replace("TALKBRIDGE_PASSWORD_", "").lower()
        is_set = "✅ SET" if os.getenv(env_var) else "❌ NOT SET"
        print(f"   {env_var:<30} {is_set}")

    print(f"\n🔑 User Roles Configuration:")
    for username, role_data in PasswordConfig.USER_ROLES.items():
        print(f"   {username:<12} {role_data['description']}")

    print(f"\n🔍 Password Validation Test:")
    test_passwords = [
        "weak",
        "Admin123!",
        PasswordConfig.generate_secure_password(16),
        PasswordConfig.generate_secure_password(24)
    ]

    for test_pass in test_passwords:
        is_valid, issues = PasswordConfig.validate_password(test_pass)
        status = "✅ VALID" if is_valid else f"❌ INVALID: {', '.join(issues)}"
        # Don't show actual passwords in output for security
        display_pass = "[SECURE_PASSWORD]" if len(test_pass) > 15 else test_pass
        print(f"   {display_pass:<25} {status}")

    print(f"\n⚠️  SECURITY WARNING:")
    print(f"   - No passwords are stored in source code")
    print(f"   - All passwords must be provided via environment variables")
    print(f"   - Use the generate_password_setup_script() method to create secure passwords")
    print(f"   - Never commit passwords to version control")


if __name__ == "__main__":
    main()