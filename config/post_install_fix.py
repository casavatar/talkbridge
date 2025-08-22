#!/usr/bin/env python3
"""
Post-Installation Verification and Fix Script
============================================

Script to verify and fix common issues after conda environment creation

Author: TalkBridge Team
Date: 2025-08-21
Version: 1.0
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

# Color codes for terminal output
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    HEADER = '\033[95m'

def print_success(message: str) -> None:
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message: str) -> None:
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message: str) -> None:
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_header(message: str) -> None:
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def check_module(module_name: str, install_cmd: str = None) -> bool:
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print_success(f"{module_name} is available")
        return True
    except ImportError:
        print_error(f"{module_name} not available")
        if install_cmd:
            print(f"  Install with: {install_cmd}")
        return False

def run_pip_install(packages: list, env_name: str = None) -> bool:
    """Install packages using pip in the specified environment"""
    if env_name:
        cmd = ["conda", "run", "-n", env_name, "pip", "install"] + packages
    else:
        cmd = ["pip", "install"] + packages
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def fix_qt_wayland_issue():
    """Fix Qt Wayland plugin issue for Linux"""
    print_header("FIXING QT WAYLAND ISSUE")
    
    # Set environment variables to prefer X11 over Wayland for Qt
    env_vars = {
        'QT_QPA_PLATFORM': 'xcb',  # Force X11
        'QT_QPA_PLATFORM_PLUGIN_PATH': '',  # Clear plugin path
        'XDG_SESSION_TYPE': 'x11'  # Prefer X11 session
    }
    
    activation_script = Path("fix_qt_environment.sh")
    script_content = "#!/bin/bash\n"
    script_content += "# Qt Environment Fix for TalkBridge Desktop\n"
    script_content += "# Run with: source fix_qt_environment.sh\n\n"
    
    for var, value in env_vars.items():
        script_content += f"export {var}='{value}'\n"
        os.environ[var] = value
    
    script_content += "\necho 'Qt environment variables set for X11 compatibility'\n"
    
    activation_script.write_text(script_content)
    activation_script.chmod(0o755)
    
    print_success("Created Qt environment fix script: fix_qt_environment.sh")
    print("Run: source fix_qt_environment.sh before starting the application")

def verify_and_fix_dependencies(env_name: str = "talkbridge-desktop-env"):
    """Verify and fix missing dependencies"""
    print_header("VERIFYING DEPENDENCIES")
    
    # Core dependencies to check
    dependencies = {
        'sounddevice': 'pip install sounddevice',
        'mediapipe': 'pip install mediapipe',
        'TTS': 'pip install TTS',
        'argostranslate': 'pip install argos-translate', 
        'transformers': 'pip install transformers torch',
        'PySide6': 'pip install PySide6'
    }
    
    missing_packages = []
    
    for module, install_cmd in dependencies.items():
        if not check_module(module, install_cmd):
            package_name = install_cmd.split()[-1] if 'pip install' in install_cmd else module
            missing_packages.append(package_name)
    
    if missing_packages:
        print_header("INSTALLING MISSING PACKAGES")
        print(f"Missing packages: {', '.join(missing_packages)}")
        
        if run_pip_install(missing_packages, env_name):
            print_success("Successfully installed missing packages")
        else:
            print_error("Failed to install some packages. Try manually:")
            for pkg in missing_packages:
                print(f"  conda run -n {env_name} pip install {pkg}")
    else:
        print_success("All dependencies are available!")

def create_launcher_script(env_name: str = "talkbridge-desktop-env"):
    """Create a launcher script that sets environment and starts the app"""
    print_header("CREATING LAUNCHER SCRIPT")
    
    launcher_content = f"""#!/bin/bash
# TalkBridge Desktop Launcher with Environment Fixes
# =================================================

# Set Qt environment for X11 compatibility
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORM_PLUGIN_PATH=""
export XDG_SESSION_TYPE=x11

# Initialize conda
eval "$(conda shell.bash hook)"

# Activate environment
echo "Activating TalkBridge Desktop environment..."
conda activate {env_name}

if [ $? -eq 0 ]; then
    echo "Environment activated successfully!"
    echo "Starting TalkBridge Desktop..."
    
    # Change to project root
    cd "$(dirname "$0")/.."
    
    # Start the application
    python src/desktop/main.py
else
    echo "Failed to activate environment: {env_name}"
    echo "Please check if the environment exists:"
    conda env list
    exit 1
fi
"""
    
    launcher_path = Path("launch_talkbridge_desktop.sh")
    launcher_path.write_text(launcher_content)
    launcher_path.chmod(0o755)
    
    print_success(f"Created launcher script: {launcher_path}")
    print(f"Run: ./{launcher_path} to start TalkBridge Desktop")

def main():
    """Main verification and fix function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify and fix TalkBridge Desktop installation")
    parser.add_argument("--env-name", default="talkbridge-desktop-env",
                       help="Conda environment name")
    parser.add_argument("--fix-qt", action="store_true",
                       help="Only fix Qt Wayland issues")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify dependencies")
    
    args = parser.parse_args()
    
    print_header("TALKBRIDGE DESKTOP - POST-INSTALLATION FIX")
    
    if args.fix_qt:
        fix_qt_wayland_issue()
        return
    
    if args.verify_only:
        verify_and_fix_dependencies(args.env_name)
        return
    
    # Full verification and fix process
    verify_and_fix_dependencies(args.env_name)
    fix_qt_wayland_issue()
    create_launcher_script(args.env_name)
    
    print_header("POST-INSTALLATION COMPLETE")
    print_success("TalkBridge Desktop is ready to use!")
    print("\nTo start the application:")
    print("1. Run: ./launch_talkbridge_desktop.sh")
    print("2. Or manually: source fix_qt_environment.sh && conda activate talkbridge-desktop-env && python src/desktop/main.py")

if __name__ == "__main__":
    main()
