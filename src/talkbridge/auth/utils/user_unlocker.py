#!/usr/bin/env python3
"""
TalkBridge User Account Unlocker
===============================

Utility to unlock user accounts and fix authentication issues.
Handles locked accounts, password resets, and account recovery.
"""

import sys
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from talkbridge.auth.utils.password_config import PasswordConfig


class UserUnlocker:
    """Utility for unlocking and recovering user accounts."""

    def __init__(self):
        """Initialize the user unlocker."""
        self.auth_manager = None
        self._initialize_auth_manager()

    def _initialize_auth_manager(self):
        """Initialize the authentication manager."""
        try:
            from talkbridge.auth.auth_manager import AuthManager
            self.auth_manager = AuthManager()
            print("✅ Authentication manager initialized")
        except Exception as e:
            print(f"❌ Failed to initialize auth manager: {e}")
            raise

    def diagnose_user_issues(self, username: str) -> Dict[str, any]:
        """
        Diagnose authentication issues for a specific user.

        Args:
            username: Username to diagnose

        Returns:
            Dictionary with diagnosis information
        """
        print(f"\n🔍 Diagnosing User: {username}")
        print("-" * 40)

        diagnosis = {
            "username": username,
            "exists": False,
            "locked": False,
            "has_password": False,
            "expected_password": None,
            "issues": [],
            "recommendations": []
        }

        try:
            # Check if user exists
            user_data = self.auth_manager.get_user(username)
            if user_data:
                diagnosis["exists"] = True
                diagnosis["locked"] = user_data.get("account_locked", False)
                print(f"   ✅ User exists: {username}")
                print(f"   🔒 Account locked: {diagnosis['locked']}")
                print(f"   👤 Role: {user_data.get('role', 'unknown')}")
                print(f"   📧 Email: {user_data.get('email', 'none')}")
                print(f"   🔑 Security level: {user_data.get('security_level', 'unknown')}")

                # Check if this is a production user with known password
                diagnosis["expected_password"] = PasswordConfig.get_password_for_user(username)
                diagnosis["has_password"] = bool(diagnosis["expected_password"])

                if diagnosis["locked"]:
                    diagnosis["issues"].append("Account is locked")
                    diagnosis["recommendations"].append("Unlock the account")

                if not diagnosis["has_password"]:
                    diagnosis["issues"].append("No standard password found")
                    diagnosis["recommendations"].append("Reset password using standard pattern")

            else:
                diagnosis["issues"].append("User does not exist")
                diagnosis["recommendations"].append("Create user account")
                print(f"   ❌ User does not exist: {username}")

                # Check if this should be a production user
                expected_password = PasswordConfig.get_password_for_user(username)
                if expected_password != PasswordConfig.generate_secure_password(username):
                    # This is a known production user
                    diagnosis["expected_password"] = expected_password
                    diagnosis["recommendations"].append("Create as production user with standard password")

        except Exception as e:
            diagnosis["issues"].append(f"Error during diagnosis: {e}")
            print(f"   ❌ Error: {e}")

        return diagnosis

    def unlock_user(self, username: str, admin_user: str = "system_unlock") -> bool:
        """
        Unlock a user account.

        Args:
            username: Username to unlock
            admin_user: Admin user performing the unlock

        Returns:
            True if successful, False otherwise
        """
        try:
            success, message = self.auth_manager.unlock_user(username, admin_user)
            if success:
                print(f"   ✅ Unlocked user: {username}")
                return True
            else:
                print(f"   ❌ Failed to unlock {username}: {message}")
                return False
        except Exception as e:
            print(f"   ❌ Error unlocking {username}: {e}")
            return False

    def reset_user_password(self, username: str, admin_user: str = "system_reset") -> bool:
        """
        Reset user password to standard pattern.

        Args:
            username: Username to reset
            admin_user: Admin user performing the reset

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get standard password for user
            new_password = PasswordConfig.get_password_for_user(username)

            success, message = self.auth_manager.reset_password(username, new_password, admin_user)
            if success:
                print(f"   ✅ Password reset for user: {username}")
                print(f"   🔑 New password: {new_password}")
                return True
            else:
                print(f"   ❌ Failed to reset password for {username}: {message}")
                return False
        except Exception as e:
            print(f"   ❌ Error resetting password for {username}: {e}")
            return False

    def create_missing_user(self, username: str, admin_user: str = "system_create") -> bool:
        """
        Create a missing production user.

        Args:
            username: Username to create
            admin_user: Admin user performing the creation

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user configuration
            users = PasswordConfig.get_production_users()
            user_config = None

            for user in users:
                if user["username"] == username:
                    user_config = user
                    break

            if not user_config:
                print(f"   ❌ No configuration found for user: {username}")
                return False

            success, message = self.auth_manager.create_user(
                username=user_config["username"],
                password=user_config["password"],
                role=user_config["role"],
                email=user_config["email"],
                permissions=user_config["permissions"],
                created_by=admin_user
            )

            if success:
                print(f"   ✅ Created user: {username}")
                print(f"   👤 Role: {user_config['role']}")
                print(f"   🔑 Password: {user_config['password']}")
                return True
            else:
                print(f"   ❌ Failed to create {username}: {message}")
                return False

        except Exception as e:
            print(f"   ❌ Error creating user {username}: {e}")
            return False

    def fix_user_account(self, username: str) -> bool:
        """
        Automatically fix all issues with a user account.

        Args:
            username: Username to fix

        Returns:
            True if successful, False otherwise
        """
        print(f"\n🔧 Fixing User Account: {username}")
        print("=" * 50)

        # Diagnose issues
        diagnosis = self.diagnose_user_issues(username)

        if not diagnosis["issues"]:
            print(f"   ✅ No issues found with {username}")
            return True

        success = True

        # Fix each issue
        for issue in diagnosis["issues"]:
            print(f"\n🔨 Fixing: {issue}")

            if "does not exist" in issue:
                if not self.create_missing_user(username):
                    success = False

            elif "locked" in issue:
                if not self.unlock_user(username):
                    success = False

            elif "password" in issue:
                if not self.reset_user_password(username):
                    success = False

        # Verify fix
        if success:
            print(f"\n✅ Verification: Testing authentication for {username}")
            try:
                expected_password = PasswordConfig.get_password_for_user(username)
                auth_success, user_data, message = self.auth_manager.authenticate(username, expected_password)

                if auth_success:
                    print(f"   ✅ Authentication successful for {username}")
                else:
                    print(f"   ❌ Authentication still failing: {message}")
                    success = False

            except Exception as e:
                print(f"   ❌ Error during verification: {e}")
                success = False

        return success

    def fix_all_production_users(self) -> Tuple[int, int]:
        """
        Fix all production user accounts.

        Returns:
            Tuple of (fixed_count, total_count)
        """
        print("\n🔧 Fixing All Production User Accounts")
        print("=" * 60)

        users = PasswordConfig.get_production_users()
        fixed_count = 0

        for user_config in users:
            username = user_config["username"]
            if self.fix_user_account(username):
                fixed_count += 1

        return fixed_count, len(users)

    def list_problematic_users(self) -> List[Dict[str, any]]:
        """
        List all users with authentication issues.

        Returns:
            List of user diagnoses with issues
        """
        print("\n🔍 Scanning for Problematic Users")
        print("=" * 50)

        users = PasswordConfig.get_production_users()
        problematic = []

        for user_config in users:
            username = user_config["username"]
            diagnosis = self.diagnose_user_issues(username)

            if diagnosis["issues"]:
                problematic.append(diagnosis)

        return problematic


def unlock_specific_user(username: str) -> bool:
    """
    Unlock a specific user account.

    Args:
        username: Username to unlock

    Returns:
        True if successful
    """
    try:
        unlocker = UserUnlocker()
        return unlocker.fix_user_account(username)
    except Exception as e:
        print(f"❌ Error unlocking user {username}: {e}")
        return False


def main():
    """Main function for user unlocking utility."""

    print("🔓 TalkBridge User Account Unlocker")
    print("=" * 70)

    try:
        unlocker = UserUnlocker()

        # Scan for issues
        problematic = unlocker.list_problematic_users()

        if not problematic:
            print("\n🎉 No user account issues found!")
            print("✅ All production users are properly configured")
            return True

        print(f"\n⚠️  Found {len(problematic)} users with issues:")
        for diagnosis in problematic:
            username = diagnosis["username"]
            issues = diagnosis["issues"]
            print(f"   ❌ {username}: {', '.join(issues)}")

        # Fix all issues
        print("\n🔧 Attempting to fix all issues...")
        fixed_count, total_count = unlocker.fix_all_production_users()

        # Summary
        print("\n" + "=" * 70)
        print("📊 USER UNLOCK SUMMARY")
        print("=" * 70)

        if fixed_count == total_count:
            print("🎉 ALL USERS FIXED SUCCESSFULLY!")
            print(f"✅ Fixed: {fixed_count}/{total_count} users")
            print("✅ All production users can now authenticate")
            return True
        else:
            print("⚠️  SOME ISSUES REMAIN")
            print(f"✅ Fixed: {fixed_count}/{total_count} users")
            print(f"❌ Failed: {total_count - fixed_count} users")
            return False

    except Exception as e:
        print(f"❌ Fatal error in user unlocker: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)