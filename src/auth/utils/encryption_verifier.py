#!/usr/bin/env python3
"""
Verify that TalkBridge is using the new Argon2id encryption and data/users.db database.
Only after verification will we proceed with cleanup and user generation.
"""

import sys
import os
import sqlite3
from pathlib import Path

def verify_database_location():
    """Verify the application is using data/users.db."""

    print("🔍 Verifying Database Location")
    print("=" * 50)

    # Check that data/users.db exists and is being used
    db_path = Path("data/users.db")
    if not db_path.exists():
        print("❌ data/users.db not found")
        return False

    print(f"✅ Database file exists: {db_path}")
    print(f"   Size: {db_path.stat().st_size} bytes")
    print(f"   Permissions: {oct(db_path.stat().st_mode)[-3:]}")

    # Verify database schema has new structure
    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.execute("PRAGMA table_info(users)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}

            required_columns = {
                'password_hash': 'TEXT',
                'salt': 'TEXT',
                'security_level': 'TEXT',
                'failed_login_attempts': 'INTEGER',
                'account_locked': 'BOOLEAN'
            }

            missing_columns = []
            for col, col_type in required_columns.items():
                if col not in columns:
                    missing_columns.append(col)

            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return False

            print("✅ Database schema has all required columns for new encryption")
            return True

    except Exception as e:
        print(f"❌ Error checking database schema: {e}")
        return False

def verify_encryption_method():
    """Verify the application is using Argon2id encryption."""

    print("\n🔐 Verifying Encryption Method")
    print("=" * 50)

    try:
        # Try relative imports first, then absolute imports as fallback
        try:
            from ..user_store import UserStore
            from ..auth_manager import AuthManager
        except ImportError:
            # Fallback to absolute imports if relative imports fail
            import sys
            from pathlib import Path
            # Add project root to path if needed
            project_root = Path(__file__).parent.parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root / 'src'))
            
            from auth.user_store import UserStore
            from auth.auth_manager import AuthManager

        # Check that Argon2 is available
        try:
            from argon2 import PasswordHasher  # type: ignore
            print("✅ Argon2 library available")
        except ImportError:
            print("❌ Argon2 library not available")
            return False

        # Check UserStore initialization
        user_store = UserStore("data/users.db")
        print("✅ UserStore initializes with Argon2")

        # Check AuthManager configuration
        auth_manager = AuthManager()
        security_info = auth_manager.get_security_info()

        if security_info.get('hash_algorithm') == 'Argon2id':
            print("✅ AuthManager configured for Argon2id")
        else:
            print(f"❌ AuthManager using: {security_info.get('hash_algorithm', 'unknown')}")
            return False

        if security_info.get('pepper_configured'):
            print("✅ Pepper configured for additional security")
        else:
            print("❌ Pepper not configured")
            return False

        return True

    except Exception as e:
        print(f"❌ Error verifying encryption method: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_existing_users():
    """Check what users exist and their encryption status."""

    print("\n👥 Checking Existing Users")
    print("=" * 50)

    try:
        # Try relative imports first, then absolute imports as fallback
        try:
            from ..user_store import UserStore
        except ImportError:
            # Fallback to absolute imports if relative imports fail
            import sys
            from pathlib import Path
            # Add project root to path if needed
            project_root = Path(__file__).parent.parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root / 'src'))
            
            from auth.user_store import UserStore

        user_store = UserStore("data/users.db")
        users = user_store.list_users()

        print(f"Found {len(users)} users in database:")

        # Check if any users have old SHA-256 hashes
        with sqlite3.connect("data/users.db") as conn:
            cursor = conn.execute("SELECT username, password_hash FROM users")

            argon2_users = 0
            potentially_old_users = 0

            for username, password_hash in cursor.fetchall():
                if password_hash.startswith('$argon2'):
                    argon2_users += 1
                    status = "✅ Argon2"
                else:
                    potentially_old_users += 1
                    status = "⚠️  Non-Argon2"

                print(f"   {username:<15} {status}")

        print(f"\nEncryption Summary:")
        print(f"   Argon2 users: {argon2_users}")
        print(f"   Non-Argon2 users: {potentially_old_users}")

        return potentially_old_users == 0

    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return False

def find_old_databases():
    """Find any old database files that might need cleanup."""

    print("\n🗂️  Checking for Old Database Files")
    print("=" * 50)

    old_db_patterns = [
        "users.db",
        "auth.db",
        "talkbridge.db",
        "database.db",
        "*.sqlite",
        "*.sqlite3"
    ]

    old_files = []

    # Check current directory and common locations
    search_paths = [
        Path("."),
        Path("data"),
        Path("src"),
        Path("database"),
        Path("db")
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        for pattern in old_db_patterns:
            for file_path in search_path.glob(pattern):
                # Skip the current database
                if file_path.name == "users.db" and file_path.parent.name == "data":
                    continue

                old_files.append(file_path)

    if old_files:
        print("Found potential old database files:")
        for file_path in old_files:
            print(f"   {file_path}")
    else:
        print("✅ No old database files found")

    return old_files

def main():
    """Main verification function."""

    print("🔍 TalkBridge Encryption Migration Verification")
    print("=" * 60)

    # Step 1: Verify database location
    db_ok = verify_database_location()

    # Step 2: Verify encryption method
    encryption_ok = verify_encryption_method()

    # Step 3: Check existing users
    users_ok = check_existing_users()

    # Step 4: Find old databases
    old_files = find_old_databases()

    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    checks = [
        ("Database Location", db_ok),
        ("Encryption Method", encryption_ok),
        ("User Encryption Status", users_ok)
    ]

    for check_name, passed in checks:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {check_name:<25} {status}")

    all_passed = all(result for _, result in checks)

    if all_passed:
        print("\n🎉 VERIFICATION SUCCESSFUL!")
        print("✅ Application is using new Argon2id encryption")
        print("✅ Database location is correct (data/users.db)")
        print("✅ All users are using secure encryption")

        if old_files:
            print(f"\n⚠️  Found {len(old_files)} old database files for cleanup")
        else:
            print("\n✅ No old database files found")

        return True, old_files
    else:
        print("\n❌ VERIFICATION FAILED")
        print("   Cannot proceed with cleanup until issues are resolved")
        return False, []

if __name__ == "__main__":
    success, old_files = main()

    if success:
        print("\n✅ Ready to proceed with secure user generation")
        sys.exit(0)
    else:
        print("\n❌ Fix verification issues before proceeding")
        sys.exit(1)