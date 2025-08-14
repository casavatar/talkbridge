#!/usr/bin/env python3
"""
TalkBridge Desktop - Setup and Installation Script
==================================================

Script to configure and install dependencies for the TalkBridge desktop application.
Automates installation and verification.

Usage:
    python setup_desktop.py [--install] [--verify] [--dev]

Author: TalkBridge Team
Date: 2025
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


def check_python_version() -> bool:
    """
    Checks that the Python version is compatible.
    
    Returns:
        bool: True if the version is compatible
    """
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version >= min_version:
        print(f"✓ Python {'.'.join(map(str, current_version))} is compatible")
        return True
    else:
        print(f"✗ Python {'.'.join(map(str, current_version))} is not compatible")
        print(f"  Python {'.'.join(map(str, min_version))} or higher is required")
        return False


def check_pip() -> bool:
    """
    Checks that pip is available.
    
    Returns:
        bool: True if pip is available
    """
    try:
        import pip
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ pip available: {result.stdout.strip()}")
            return True
        else:
            print("✗ pip is not working properly")
            return False
    except ImportError:
        print("✗ pip is not installed")
        return False


def install_requirements(requirements_file: Path, dev: bool = False) -> bool:
    """
    Installs dependencies from a requirements file.
    
    Args:
        requirements_file: Requirements file
        dev: Whether to install development dependencies
        
    Returns:
        bool: True if installation was successful
    """
    if not requirements_file.exists():
        print(f"✗ File {requirements_file} not found")
        return False
    
    print(f"📦 Installing dependencies from {requirements_file.name}...")
    
    # Base command
    cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
    
    # Add upgrade flag
    cmd.append('--upgrade')
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies:")
        print(f"  Exit code: {e.returncode}")
        print(f"  STDOUT: {e.stdout}")
        print(f"  STDERR: {e.stderr}")
        return False


def verify_pyqt6_installation() -> bool:
    """
    Checks that PyQt6 is installed correctly.
    
    Returns:
        bool: True if PyQt6 works
    """
    try:
        print("🔍 Verifying PyQt6...")
        
        # Import main components
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QObject, pyqtSignal
        from PyQt6.QtGui import QFont
        
        # Create test application
        app = QApplication([])
        app.quit()
        
        print("✓ PyQt6 installed and working correctly")
        return True
        
    except ImportError as e:
        print(f"✗ Error importing PyQt6: {e}")
        return False
    except Exception as e:
        print(f"✗ Error verifying PyQt6: {e}")
        return False


def verify_core_modules() -> Tuple[bool, List[str]]:
    """
    Checks that TalkBridge core modules are available.
    
    Returns:
        Tuple[bool, List[str]]: Overall success and list of missing modules
    """
    print("🔍 Verifying TalkBridge core modules...")
    
    modules_to_check = [
        ('src.tts.synthesizer', 'TTS Synthesizer'),
        ('src.audio.capture', 'Audio Capture'),
        ('src.translation.translator', 'Translator'),
        ('src.ui.auth.auth_manager', 'Auth Manager'),
        ('src.ollama.ollama_client', 'Ollama Client'),
        ('src.animation.face_sync', 'Face Sync'),
        ('src.utils.logger', 'Logger Utilities')
    ]
    
    missing_modules = []
    available_count = 0
    
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
            available_count += 1
        except ImportError:
            print(f"  ⚠ {display_name} (optional)")
            missing_modules.append(display_name)
    
    success = available_count > len(modules_to_check) // 2
    
    if success:
        print(f"✓ {available_count}/{len(modules_to_check)} core modules available")
    else:
        print(f"⚠ Only {available_count}/{len(modules_to_check)} modules available")
    
    return success, missing_modules


def create_desktop_directories(project_root: Path) -> bool:
    """
    Creates the necessary folders for the desktop application.
    
    Args:
        project_root: Project root directory
        
    Returns:
        bool: True if created successfully
    """
    print("📁 Creating necessary directories...")
    
    directories = [
        'data/logs',
        'data/cache',
        'data/temp',
        'data/exports',
        'config/desktop',
        'src/desktop/resources/icons',
        'src/desktop/resources/images',
        'src/desktop/resources/sounds'
    ]
    
    try:
        for directory in directories:
            dir_path = project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
        print("✓ Directories created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error creating directories: {e}")
        return False


def generate_desktop_config(project_root: Path) -> bool:
    """
    Generates a desktop-specific configuration file.
    
    Args:
        project_root: Project root directory
        
    Returns:
        bool: True if generated successfully
    """
    print("⚙️  Generating desktop configuration...")
    
    desktop_config = """# TalkBridge Desktop Configuration
# ================================

desktop:
  # Main window configuration
  window:
    title: "TalkBridge Desktop"
    width: 1200
    height: 800
    min_width: 800
    min_height: 600
    center_on_screen: true
    remember_size: true
    remember_position: true
  
  # Theme and appearance
  theme:
    name: "dark"
    accent_color: "#0078d4"
    font_family: "Segoe UI"
    font_size: 10
  
  # Application behavior
  behavior:
    auto_save_interval: 300  # seconds
    show_splash_screen: true
    minimize_to_tray: false
    start_minimized: false
    check_updates_on_startup: true
  
  # Enabled services
  services:
    tts: true
    audio: true
    translation: true
    ollama: true
    animation: true
    camera: true
  
  # Desktop-specific logging
  logging:
    level: "INFO"
    file_rotation: "daily"
    max_file_size: "10MB"
    backup_count: 7

# UI services configuration
ui_services:
  dashboard:
    auto_refresh_interval: 5  # seconds
    show_service_details: true
    animate_status_changes: true
  
  audio:
    show_waveform: true
    show_volume_meter: true
    buffer_size: 1024
  
  tts:
    preview_enabled: true
    show_progress: true
    allow_interruption: true
"""
    
    try:
        config_file = project_root / "config" / "desktop" / "desktop.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(desktop_config)
        
        print(f"✓ Configuration generated at {config_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error generating configuration: {e}")
        return False


def create_launcher_scripts(project_root: Path) -> bool:
    """
    Creates launcher scripts for different platforms.
    
    Args:
        project_root: Project root directory
        
    Returns:
        bool: True if created successfully
    """
    print("🚀 Creating launcher scripts...")
    
    # Windows script
    windows_script = """@echo off
REM TalkBridge Desktop Launcher - Windows
REM =====================================

cd /d "%~dp0"

echo Starting TalkBridge Desktop...

REM Check that Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Run application
python src/desktop/main.py

REM Keep window open if there is an error
if errorlevel 1 (
    echo.
    echo Error running the application
    pause
)
"""
    
    # Linux/Mac script
    unix_script = """#!/bin/bash
# TalkBridge Desktop Launcher - Linux/Mac
# =======================================

cd "$(dirname "$0")"

echo "Starting TalkBridge Desktop..."

# Check that Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check dependencies
if ! python3 -c "from PyQt6.QtWidgets import QApplication" &> /dev/null; then
    echo "Error: PyQt6 not installed"
    echo "Run: pip install -r requirements-desktop.txt"
    exit 1
fi

# Run application
python3 src/desktop/main.py

# Show message if there is an error
if [ $? -ne 0 ]; then
    echo ""
    echo "Error running the application"
    read -p "Press Enter to continue..."
fi
"""
    
    try:
        # Create Windows script
        windows_file = project_root / "run_desktop.bat"
        with open(windows_file, 'w', encoding='utf-8') as f:
            f.write(windows_script)
        
        # Create Unix script
        unix_file = project_root / "run_desktop.sh"
        with open(unix_file, 'w', encoding='utf-8') as f:
            f.write(unix_script)
        
        # Make executable on Unix
        try:
            os.chmod(unix_file, 0o755)
        except:
            pass  # Ignore on Windows
        
        print("✓ Launcher scripts created")
        return True
        
    except Exception as e:
        print(f"✗ Error creating scripts: {e}")
        return False


def run_setup(install: bool = False, verify: bool = False, dev: bool = False) -> int:
    """
    Runs the complete setup process.
    
    Args:
        install: Whether to install dependencies
        verify: Whether to verify installation
        dev: Whether to include development dependencies
        
    Returns:
        int: Exit code (0 = success)
    """
    print("🏗️  TalkBridge Desktop Setup")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    
    # Basic checks
    if not check_python_version():
        return 1
    
    if not check_pip():
        return 1
    
    # Create directories
    if not create_desktop_directories(project_root):
        return 1
    
    # Install dependencies if requested
    if install:
        # Install base requirements first if exists
        base_requirements = project_root / "requirements.txt"
        if base_requirements.exists():
            if not install_requirements(base_requirements):
                print("⚠ Error installing base requirements, continuing...")
        
        # Install desktop requirements
        desktop_requirements = project_root / "requirements-desktop.txt"
        if not install_requirements(desktop_requirements, dev):
            return 1
    
    # Verify installation
    if verify or install:
        if not verify_pyqt6_installation():
            return 1
        
        success, missing = verify_core_modules()
        if missing:
            print(f"⚠ Optional modules missing: {', '.join(missing)}")
    
    # Generate configuration
    if not generate_desktop_config(project_root):
        print("⚠ Error generating configuration, continuing...")
    
    # Create launcher scripts
    if not create_launcher_scripts(project_root):
        print("⚠ Error creating launcher scripts, continuing...")
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nTo run TalkBridge Desktop:")
    print("  Windows: run_desktop.bat")
    print("  Linux/Mac: ./run_desktop.sh")
    print("  Manual: python src/desktop/main.py")
    
    return 0


def main():
    """Main function of the script."""
    parser = argparse.ArgumentParser(
        description="Setup script for TalkBridge Desktop"
    )
    parser.add_argument(
        '--install', 
        action='store_true',
        help='Install dependencies'
    )
    parser.add_argument(
        '--verify',
        action='store_true', 
        help='Verify existing installation'
    )
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Include development dependencies'
    )
    
    args = parser.parse_args()
    
    # If no flags specified, do install and verify
    if not any([args.install, args.verify]):
        args.install = True
        args.verify = True
    
    sys.exit(run_setup(args.install, args.verify, args.dev))


if __name__ == "__main__":
    main()