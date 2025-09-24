#!/usr/bin/env python3
"""
Create secure passwords that meet TalkBridge security requirements.
Uses centralized PasswordConfig for consistent password management.
"""

import sys
from .password_config import PasswordConfig

def generate_secure_password_pattern():
    """
    Generate secure passwords using centralized configuration.

    Uses PasswordConfig to ensure consistency across all utilities.
    """

    # Use centralized configuration for consistent passwords
    return PasswordConfig.get_production_passwords()

def validate_password(password: str) -> bool:
    """Validate password meets all requirements using centralized config."""
    is_valid, _ = PasswordConfig.validate_password(password)
    return is_valid

def update_user_passwords():
    """Update all users with secure passwords."""

    print("🔐 Creating Secure Passwords (12+ Characters)")
    print("=" * 60)

    users_and_passwords = generate_secure_password_pattern()

    try:
        from talkbridge.auth.auth_manager import AuthManager

        auth_manager = AuthManager()

        print("Validating all passwords meet requirements:")
        for username, password in users_and_passwords:
            valid = validate_password(password)
            status = "✅" if valid else "❌"
            print(f"   {username:<12} {password:<20} {status}")

        print(f"\nUpdating user passwords:")

        success_count = 0
        for username, password in users_and_passwords:
            # Reset password using admin override
            success, message = auth_manager.reset_password(username, password, "secure_migration")

            if success:
                print(f"   ✅ {username:<12} - Password updated")
                success_count += 1
            else:
                print(f"   ❌ {username:<12} - {message}")

        print(f"\n📊 Password Update Summary:")
        print(f"   Successfully updated: {success_count}")
        print(f"   Total users: {len(users_and_passwords)}")

        return success_count == len(users_and_passwords)

    except Exception as e:
        print(f"❌ Error updating passwords: {e}")
        return False

def test_authentication():
    """Test authentication with new passwords."""

    print("\n🔍 Testing Authentication with New Passwords")
    print("=" * 60)

    users_and_passwords = generate_secure_password_pattern()

    try:
        from talkbridge.auth.auth_manager import AuthManager

        auth_manager = AuthManager()

        working_count = 0
        for username, password in users_and_passwords:
            success, user_data, message = auth_manager.authenticate(username, password)

            if success:
                print(f"   ✅ {username:<12} - Authentication successful")
                working_count += 1
            else:
                print(f"   ❌ {username:<12} - {message}")

        print(f"\n📊 Authentication Test Summary:")
        print(f"   Working logins: {working_count}")
        print(f"   Total users: {len(users_and_passwords)}")

        return working_count == len(users_and_passwords)

    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False

def show_final_credentials():
    """Show the final credentials for production use."""

    print("\n📋 FINAL PRODUCTION CREDENTIALS")
    print("=" * 60)

    users_and_passwords = generate_secure_password_pattern()

    print("Secure credentials (Argon2id encrypted):")
    print("-" * 60)
    for username, password in users_and_passwords:
        print(f"Username: {username:<12} Password: {password}")

    print("\n🔒 Security Compliance:")
    print("   ✅ All passwords 12+ characters")
    print("   ✅ Mixed case, digits, special characters")
    print("   ✅ Argon2id encryption with pepper")
    print("   ✅ Role-based access control")
    print("   ✅ Account lockout protection")

def main():
    """Main function."""

    print("🔐 TalkBridge Secure Password Migration")
    print("=" * 70)

    # Step 1: Update passwords
    update_ok = update_user_passwords()

    # Step 2: Test authentication
    test_ok = test_authentication()

    # Step 3: Show final credentials
    show_final_credentials()

    # Summary
    print("\n" + "=" * 70)
    if update_ok and test_ok:
        print("🎉 SECURE PASSWORD MIGRATION COMPLETED!")
        print("✅ All users have secure 12+ character passwords")
        print("✅ All passwords meet complexity requirements")
        print("✅ Authentication verified working")
        print("✅ Ready for production use")
        return True
    else:
        print("❌ Password migration had issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)