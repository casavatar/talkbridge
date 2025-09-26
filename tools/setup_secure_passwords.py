#!/usr/bin/env python3
"""
TalkBridge Secure Password Setup Script
=======================================

Wrapper script for the secure user generation functionality.
This script ensures database creation and provides easy access to user management.

IMPORTANT SECURITY NOTES:
- This script generates cryptographically secure passwords
- All passwords must be provided via environment variables
- Never commit passwords to version control

Author: TalkBridge Team
Date: 2025-01-15
Version: 1.0
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import sys
    sys.path.insert(0, 'src')
    from auth.utils.user_generator import main as run_user_generator
    from auth.utils.password_config import PasswordConfig
    from utils.config_validator import ConfigValidator
except ImportError as e:
    print(f"❌ Error importing TalkBridge modules: {e}")
    print("   Make sure you're running this from the project root directory")
    print("   and that all dependencies are installed.")
    sys.exit(1)


def show_help():
    """Display help information."""
    print("🔐 TalkBridge Secure Password Setup")
    print("=" * 40)
    print()
    print("This script helps you set up secure authentication for TalkBridge.")
    print("It creates the user database and generates secure passwords.")
    print()
    print("Usage:")
    print("  python setup_secure_passwords.py [OPTIONS]")
    print()
    print("Options:")
    print("  --help          Show this help message")
    print("  --generate      Generate password setup script (bash)")
    print("  --generate-ps1  Generate password setup script (PowerShell)")
    print("  --validate      Validate current configuration")
    print("  --setup-users   Create/update users in database")
    print()
    print("Examples:")
    print("  python setup_secure_passwords.py --setup-users    # Create users (requires env vars)")
    print("  python setup_secure_passwords.py --generate       # Generate password script")
    print("  python setup_secure_passwords.py --validate       # Check configuration")


def generate_password_script(powershell=False):
    """Generate a shell script to set environment variables."""
    script_type = "PowerShell" if powershell else "Shell"
    print(f"🔐 Generating Secure Password Setup Script ({script_type})")
    print("=" * 50)

    if powershell:
        script_content = PasswordConfig.generate_password_setup_script_powershell()
        script_file = Path("set_passwords.ps1")
        usage_cmd = ".\\set_passwords.ps1"
    else:
        script_content = PasswordConfig.generate_password_setup_script()
        script_file = Path("set_passwords.sh")
        usage_cmd = "./set_passwords.sh"

    # Write to file
    script_file.write_text(script_content, encoding='utf-8')

    # Make executable on Unix systems (for shell scripts)
    if not powershell and os.name != 'nt':
        os.chmod(script_file, 0o755)

    print(f"✅ Password setup script created: {script_file.absolute()}")
    print()
    print("⚠️  SECURITY WARNING:")
    print("   - This script contains secure passwords")
    print(f"   - Run it to set environment variables: {usage_cmd}")
    print("   - DELETE the script after use")
    print("   - Never commit it to version control")
    print()
    print("To use:")
    print("  chmod +x set_passwords.sh  # Make executable (Unix/Linux/Mac)")
    print("  ./set_passwords.sh         # Set environment variables")
    print("  rm set_passwords.sh        # Delete after use")


def validate_configuration():
    """Validate current security configuration."""
    print("🔍 Validating TalkBridge Security Configuration")
    print("=" * 50)

    validator = ConfigValidator()
    issues = validator.run_full_validation()

    validator.print_report()

    return not validator.has_critical_issues()


def main():
    """Main function."""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ["--help", "-h", "help"]:
            show_help()
            return

        elif arg == "--generate":
            generate_password_script()
            return

        elif arg == "--generate-ps1":
            generate_password_script(powershell=True)
            return

        elif arg == "--validate":
            is_valid = validate_configuration()
            sys.exit(0 if is_valid else 1)

        elif arg == "--setup-users":
            print("🔐 Setting up TalkBridge users with secure authentication")
            print("=" * 60)

            # Check environment variables first
            missing_vars = []
            for username in PasswordConfig.USER_ROLES.keys():
                env_var = f"TALKBRIDGE_PASSWORD_{username.upper()}"
                if not os.getenv(env_var):
                    missing_vars.append(env_var)

            if missing_vars:
                print("❌ Required environment variables are not set:")
                for var in missing_vars:
                    print(f"   - {var}")
                print()
                print("Options:")
                print("  1. Run: python setup_secure_passwords.py --generate")
                print("  2. Set environment variables manually")
                print("  3. Use the generated script to set variables")
                sys.exit(1)

            # Run user generation
            success = run_user_generator()
            sys.exit(0 if success else 1)

        else:
            print(f"Unknown option: {arg}")
            print("Run 'python setup_secure_passwords.py --help' for usage information.")
            sys.exit(1)

    else:
        # Interactive mode
        print("🚀 TalkBridge Interactive Security Setup")
        print("=" * 45)
        print()
        print("What would you like to do?")
        print("  1. Generate secure passwords (bash script)")
        print("  2. Generate secure passwords (PowerShell script)")
        print("  3. Setup users in database (requires environment variables)")
        print("  4. Validate current configuration")
        print("  5. Show help")
        print()

        try:
            choice = input("Enter your choice (1-5): ").strip()

            if choice == "1":
                generate_password_script()
            elif choice == "2":
                generate_password_script(powershell=True)
            elif choice == "3":
                main_with_args(["--setup-users"])
            elif choice == "4":
                validate_configuration()
            elif choice == "5":
                show_help()
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
                sys.exit(1)

        except KeyboardInterrupt:
            print("\n\n⏹️  Setup cancelled by user")
            sys.exit(1)


def main_with_args(args):
    """Helper to run main with specific arguments."""
    original_argv = sys.argv[:]
    sys.argv = [sys.argv[0]] + args
    try:
        main()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)