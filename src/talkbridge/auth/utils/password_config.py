#!/usr/bin/env python3
"""
TalkBridge Authentication Password Configuration
===============================================

Centralized password configuration for all authentication utilities.
Ensures consistency across user_generator and password_manager.
"""

from typing import Dict, List, Tuple
import secrets
import string


class PasswordConfig:
    """Centralized password configuration and generation."""

    # Security requirements
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True

    # Special characters allowed
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Production user password patterns
    # Format: (username, password, description)
    PRODUCTION_PASSWORDS = [
        ("admin", "AdminSecure123!", "System administrator with full privileges"),
        ("moderator", "ModeratorSecure123!", "Content and user moderation"),
        ("support", "SupportSecure123!", "Customer support representative"),
        ("analyst", "AnalystSecure123!", "Data analyst and reporting"),
        ("developer", "DeveloperSecure123!", "Software developer with debug access"),
        ("translator", "TranslatorSecure123!", "Language and translation specialist"),
        ("guest", "GuestSecure123!", "Limited access guest account"),
        ("demo", "DemoSecure123!", "Demonstration account for showcasing features"),
        ("auditor", "AuditorSecure123!", "Security auditor with read-only monitoring access"),
        ("operator", "OperatorSecure123!", "System operator for monitoring and basic maintenance"),
    ]

    @classmethod
    def get_production_users(cls) -> List[Dict]:
        """Get complete user definitions with unified passwords."""

        users = [
            {
                "username": "admin",
                "password": "AdminSecure123!",
                "role": "admin",
                "email": "admin@talkbridge.secure",
                "security_level": "high",
                "permissions": [
                    "user_management", "system_settings", "view_logs",
                    "unlock_accounts", "create_users", "delete_users",
                    "modify_roles", "backup_restore", "security_audit"
                ],
                "description": "System administrator with full privileges"
            },
            {
                "username": "moderator",
                "password": "ModeratorSecure123!",
                "role": "moderator",
                "email": "moderator@talkbridge.secure",
                "security_level": "high",
                "permissions": [
                    "moderate_chat", "view_user_activity", "temporary_user_restrictions",
                    "content_management", "user_warnings", "chat_history_review"
                ],
                "description": "Content and user moderation"
            },
            {
                "username": "support",
                "password": "SupportSecure123!",
                "role": "support",
                "email": "support@talkbridge.secure",
                "security_level": "medium",
                "permissions": [
                    "view_user_activity", "user_assistance", "basic_troubleshooting",
                    "ticket_management", "user_communication"
                ],
                "description": "Customer support representative"
            },
            {
                "username": "analyst",
                "password": "AnalystSecure123!",
                "role": "analyst",
                "email": "analyst@talkbridge.secure",
                "security_level": "medium",
                "permissions": [
                    "view_analytics", "generate_reports", "data_export",
                    "performance_monitoring", "usage_statistics"
                ],
                "description": "Data analyst and reporting"
            },
            {
                "username": "developer",
                "password": "DeveloperSecure123!",
                "role": "developer",
                "email": "developer@talkbridge.secure",
                "security_level": "high",
                "permissions": [
                    "system_debug", "log_access", "api_testing",
                    "development_tools", "feature_flags"
                ],
                "description": "Software developer with debug access"
            },
            {
                "username": "translator",
                "password": "TranslatorSecure123!",
                "role": "translator",
                "email": "translator@talkbridge.secure",
                "security_level": "medium",
                "permissions": [
                    "translation_management", "language_packs", "content_localization",
                    "translation_review", "linguistic_validation"
                ],
                "description": "Language and translation specialist"
            },
            {
                "username": "guest",
                "password": "GuestSecure123!",
                "role": "guest",
                "email": "guest@talkbridge.secure",
                "security_level": "low",
                "permissions": [
                    "basic_voice_chat", "limited_translation", "read_only_access"
                ],
                "description": "Limited access guest account"
            },
            {
                "username": "demo",
                "password": "DemoSecure123!",
                "role": "demo",
                "email": "demo@talkbridge.secure",
                "security_level": "low",
                "permissions": [
                    "voice_chat", "translation", "demo_features",
                    "limited_avatar_control", "basic_settings"
                ],
                "description": "Demonstration account for showcasing features"
            },
            {
                "username": "auditor",
                "password": "AuditorSecure123!",
                "role": "auditor",
                "email": "auditor@talkbridge.secure",
                "security_level": "high",
                "permissions": [
                    "security_audit", "log_review", "compliance_check",
                    "access_monitoring", "audit_reports"
                ],
                "description": "Security auditor with read-only monitoring access"
            },
            {
                "username": "operator",
                "password": "OperatorSecure123!",
                "role": "operator",
                "email": "operator@talkbridge.secure",
                "security_level": "medium",
                "permissions": [
                    "system_monitoring", "service_restart", "basic_maintenance",
                    "health_checks", "performance_alerts"
                ],
                "description": "System operator for monitoring and basic maintenance"
            }
        ]

        return users

    @classmethod
    def get_production_passwords(cls) -> List[Tuple[str, str]]:
        """Get username and password pairs for production users."""
        return [(user["username"], user["password"]) for user in cls.get_production_users()]

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
    def generate_secure_password(cls, username: str, length: int = 16) -> str:
        """
        Generate a secure password for a given username.

        Args:
            username: Username to generate password for
            length: Desired password length (minimum 12)

        Returns:
            Secure password string
        """
        if length < cls.MIN_LENGTH:
            length = cls.MIN_LENGTH

        # Start with username capitalized
        base = username.capitalize()

        # Calculate remaining length needed
        remaining = length - len(base)

        if remaining < 6:  # Need minimum space for "Secure123!"
            # Use shorter pattern
            password = f"{base}123!"
            # Fill remaining with random chars
            needed = length - len(password)
            if needed > 0:
                random_chars = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(needed))
                password = f"{base}{random_chars}123!"
        else:
            # Use standard "Secure123!" pattern
            password = f"{base}Secure123!"
            # Add random chars if more length needed
            needed = length - len(password)
            if needed > 0:
                random_chars = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(needed))
                password = f"{base}Secure{random_chars}123!"

        return password

    @classmethod
    def get_password_for_user(cls, username: str) -> str:
        """Get the standard password for a specific username."""
        for user_data in cls.get_production_users():
            if user_data["username"] == username:
                return user_data["password"]

        # If not found in production users, generate one
        return cls.generate_secure_password(username)

    @classmethod
    def get_password_summary(cls) -> Dict[str, str]:
        """Get a summary of all usernames and their passwords."""
        return {user["username"]: user["password"] for user in cls.get_production_users()}


def main():
    """Display password configuration information."""

    print("🔐 TalkBridge Password Configuration")
    print("=" * 50)

    print(f"\n📋 Security Requirements:")
    print(f"   Minimum Length: {PasswordConfig.MIN_LENGTH}")
    print(f"   Uppercase Required: {PasswordConfig.REQUIRE_UPPERCASE}")
    print(f"   Lowercase Required: {PasswordConfig.REQUIRE_LOWERCASE}")
    print(f"   Digits Required: {PasswordConfig.REQUIRE_DIGITS}")
    print(f"   Special Chars Required: {PasswordConfig.REQUIRE_SPECIAL}")
    print(f"   Allowed Special Chars: {PasswordConfig.SPECIAL_CHARS}")

    print(f"\n👥 Production User Passwords:")
    passwords = PasswordConfig.get_password_summary()
    for username, password in passwords.items():
        is_valid, issues = PasswordConfig.validate_password(password)
        status = "✅" if is_valid else "❌"
        print(f"   {username:<12} {password:<20} {status}")

    print(f"\n🔍 Password Validation Test:")
    test_passwords = [
        "weak",
        "Admin123!",
        "AdminSecure123!",
        "VeryLongAndSecurePassword123!"
    ]

    for test_pass in test_passwords:
        is_valid, issues = PasswordConfig.validate_password(test_pass)
        status = "✅ VALID" if is_valid else f"❌ INVALID: {', '.join(issues)}"
        print(f"   {test_pass:<25} {status}")


if __name__ == "__main__":
    main()