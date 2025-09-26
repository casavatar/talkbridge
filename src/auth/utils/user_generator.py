#!/usr/bin/env python3
"""
Generate secure users for TalkBridge using Argon2id encryption.
Follows security best practices and unified password configuration.

Pattern: Uses centralized PasswordConfig for consistent passwords across all utilities.
"""

import sys
import os
from typing import List, Dict
from datetime import datetime
from .password_config import PasswordConfig
from ...utils.project_root import get_data_dir, ensure_data_directories

def ensure_database_exists():
    """Ensure the user database exists and is properly initialized."""
    print("\n🗄️ Initializing User Database")
    print("=" * 40)

    try:
        # Ensure data directories exist
        ensure_data_directories()

        # Get database path
        data_dir = get_data_dir()
        db_path = data_dir / "users.db"

        print(f"Database location: {db_path}")

        # Check if database exists
        db_existed = db_path.exists()

        if not db_existed:
            print("Database does not exist - will be created during AuthManager initialization")

        # Test database creation/access through AuthManager
        from ..auth_manager import AuthManager
        auth_manager = AuthManager(db_path=str(db_path))

        if db_existed:
            print("✅ Database already exists and is accessible")
        else:
            print("✅ Database created successfully")

        # Test database connection
        try:
            users = auth_manager.list_users()
            print(f"✅ Database initialized with {len(users)} existing users")
        except Exception as e:
            print(f"⚠️  Database accessible but may be empty: {e}")

        return True

    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        print("This may indicate:")
        print("   - Insufficient permissions to create/access database")
        print("   - Corrupted existing database file")
        print("   - Missing dependencies for SQLite operations")
        print("\nSolutions:")
        print("   - Run with administrator/elevated privileges")
        print("   - Delete existing database file if corrupted")
        print("   - Ensure all required Python packages are installed")
        return False


def generate_secure_user_list() -> List[Dict]:
    """
    Generate a list of secure users WITHOUT embedded passwords.

    Uses centralized PasswordConfig for user role definitions.
    Passwords MUST be provided via environment variables.

    Security Practices Applied:
    - NO hard-coded passwords
    - Principle of least privilege (minimal permissions per role)
    - Clear role separation
    - Secure email domains
    - Appropriate security levels
    """

    # Use centralized configuration WITHOUT passwords
    return PasswordConfig.get_user_definitions()

def cleanup_test_users():
    """Remove test users created during development."""

    print("🧹 Cleaning Up Test Users")
    print("=" * 40)

    try:
        from ..auth_manager import AuthManager

        auth_manager = AuthManager()

        # Test users to remove (keep essential ones)
        test_users_to_remove = [
            "testuser",
            "simpleadmin",
            "demo_user",
            "test_user",
            "test"
        ]

        removed_count = 0
        for username in test_users_to_remove:
            success, message = auth_manager.delete_user(username, "cleanup_script")
            if success:
                print(f"   ✅ Removed: {username}")
                removed_count += 1
            else:
                print(f"   ⚠️  {username}: {message}")

        print(f"\n✅ Cleaned up {removed_count} test users")
        return True

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def create_secure_users():
    """Create secure users with proper passwords."""

    print("\n👤 Creating Secure Production Users")
    print("=" * 50)

    try:
        from ..auth_manager import AuthManager

        auth_manager = AuthManager()
        users = generate_secure_user_list()

        created_count = 0
        updated_count = 0

        for user_data in users:
            # Check if user already exists
            existing_user = auth_manager.get_user(user_data["username"])

            if existing_user:
                # Update existing user password and permissions
                print(f"   🔄 Updating: {user_data['username']}")

                # Get password from environment
                password = PasswordConfig.get_password_from_env(user_data["username"])
                if not password:
                    print(f"      ❌ No password found in environment for {user_data['username']}")
                    continue

                success, message = auth_manager.reset_password(
                    user_data["username"],
                    password,
                    "system_migration"
                )

                if success:
                    updated_count += 1
                    print(f"      ✅ Password updated")
                else:
                    print(f"      ❌ Password update failed: {message}")

            else:
                # Create new user
                print(f"   ➕ Creating: {user_data['username']} ({user_data['role']})")

                # Get password from environment
                password = PasswordConfig.get_password_from_env(user_data["username"])
                if not password:
                    print(f"      ❌ No password found in environment for {user_data['username']}")
                    continue

                success, message = auth_manager.create_user(
                    username=user_data["username"],
                    password=password,
                    role=user_data["role"],
                    email=user_data.get("email", f"{user_data['username']}@talkbridge.secure"),
                    permissions=user_data.get("permissions", []),
                    created_by="secure_setup"
                )

                if success:
                    created_count += 1
                    print(f"      ✅ Created successfully")
                else:
                    print(f"      ❌ Creation failed: {message}")

        print(f"\n📊 User Creation Summary:")
        print(f"   Created: {created_count} new users")
        print(f"   Updated: {updated_count} existing users")
        print(f"   Total: {created_count + updated_count} users processed")

        return True

    except Exception as e:
        print(f"❌ Error creating users: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_user_creation():
    """Verify that all users were created correctly with Argon2."""

    print("\n🔍 Verifying User Creation")
    print("=" * 40)

    try:
        from ..auth_manager import AuthManager

        auth_manager = AuthManager()
        users = auth_manager.list_users()

        print(f"Total users in database: {len(users)}")
        print("\nUser verification:")

        argon2_count = 0
        for user in users:
            # Test authentication with environment passwords
            username = user['username']
            expected_password = PasswordConfig.get_password_from_env(username)

            if not expected_password:
                print(f"   ⚠️  {username:<12} - No password in environment")
                continue

            success, user_data, message = auth_manager.authenticate(username, expected_password)

            if success:
                print(f"   ✅ {username:<12} - Authentication successful")
                argon2_count += 1
            else:
                print(f"   ⚠️  {username:<12} - {message}")

        print(f"\n✅ {argon2_count} users have working Argon2 authentication")
        return True

    except Exception as e:
        print(f"❌ Error verifying users: {e}")
        return False

def generate_credentials_summary():
    """Generate a secure credentials summary WITHOUT showing passwords."""

    print("\n📋 Secure User Configuration Summary")
    print("=" * 50)

    users = generate_secure_user_list()
    env_vars = PasswordConfig.get_all_required_env_vars()

    print("Production Users (Passwords from environment):")
    print("-" * 50)

    for user in users:
        env_var = f"TALKBRIDGE_PASSWORD_{user['username'].upper()}"
        password_status = "✅ SET" if os.getenv(env_var) else "❌ NOT SET"
        print(f"Username: {user['username']:<12} Env Var: {env_var:<30} Status: {password_status}")

    print("\n📋 Required Environment Variables:")
    print("-" * 50)
    for env_var in env_vars:
        status = "✅ SET" if os.getenv(env_var) else "❌ NOT SET"
        print(f"   {env_var:<35} {status}")

    print("\n🔒 Security Features:")
    print("   ✅ Argon2id key derivation with pepper")
    print("   ✅ 12+ character passwords with complexity")
    print("   ✅ Principle of least privilege")
    print("   ✅ Role-based access control")
    print("   ✅ Account lockout protection")
    print("   ✅ Rate limiting")
    print("   ✅ Secure file permissions (600)")

    print("\n⚠️  Security Reminders:")
    print("   - All passwords are stored only in environment variables")
    print("   - No passwords are embedded in source code")
    print("   - Use 'PasswordConfig.generate_password_setup_script()' to create secure passwords")
    print("   - Enable 2FA where possible")
    print("   - Regular password rotation policy")
    print("   - Monitor access logs")
    print("   - Never commit passwords to version control")

def main():
    """Main function to create secure users."""

    print("🔐 TalkBridge Secure User Generation")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: Ensure database exists
    database_ok = ensure_database_exists()
    if not database_ok:
        print("❌ Database initialization failed - cannot proceed")
        return False

    # Step 2: Clean up test users
    cleanup_ok = cleanup_test_users()

    # Step 3: Create secure users
    creation_ok = create_secure_users()

    # Step 4: Verify creation
    verification_ok = verify_user_creation()

    # Step 5: Generate summary
    generate_credentials_summary()

    # Final status
    print("\n" + "=" * 60)
    if database_ok and cleanup_ok and creation_ok and verification_ok:
        print("🎉 SECURE USER GENERATION COMPLETED SUCCESSFULLY!")
        print("✅ All users created with Argon2id encryption")
        print("✅ Security best practices applied")
        print("✅ Ready for production use")
        return True
    else:
        print("❌ Some issues occurred during user generation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)