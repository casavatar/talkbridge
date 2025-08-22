#!/usr/bin/env python3
"""
TalkBridge Desktop Diagnostic Script
===================================

Diagnose and report specific issues with the TalkBridge Desktop installation

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
    OKBLUE = '\033[94m'

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

def print_info(message: str) -> None:
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def test_import(module_name: str, package_name: str = None) -> dict:
    """Test module import and return status"""
    result = {
        'module': module_name,
        'package': package_name or module_name,
        'available': False,
        'error': None
    }
    
    try:
        importlib.import_module(module_name)
        result['available'] = True
        print_success(f"{module_name} - Available")
    except ImportError as e:
        result['error'] = str(e)
        print_error(f"{module_name} - Not available: {e}")
    except Exception as e:
        result['error'] = str(e)
        print_warning(f"{module_name} - Error: {e}")
    
    return result

def check_qt_environment():
    """Check Qt environment and Wayland issues"""
    print_header("QT ENVIRONMENT DIAGNOSIS")
    
    qt_vars = {
        'QT_QPA_PLATFORM': 'Qt platform abstraction',
        'QT_QPA_PLATFORM_PLUGIN_PATH': 'Qt plugin path',
        'XDG_SESSION_TYPE': 'Desktop session type',
        'WAYLAND_DISPLAY': 'Wayland display',
        'DISPLAY': 'X11 display'
    }
    
    for var, description in qt_vars.items():
        value = os.environ.get(var, 'Not set')
        print(f"{description}: {var} = {value}")
    
    # Recommendations
    print("\nRecommendations:")
    if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
        print_warning("Running on Wayland - this may cause Qt plugin issues")
        print("  Solution: export QT_QPA_PLATFORM=xcb")
    else:
        print_success("Not running on Wayland")
    
    return os.environ.get('XDG_SESSION_TYPE') != 'wayland'

def diagnose_audio_system():
    """Diagnose audio system issues"""
    print_header("AUDIO SYSTEM DIAGNOSIS")
    
    # Test ALSA/PulseAudio
    audio_tests = [
        ('aplay --list-devices', 'List ALSA devices'),
        ('pactl info', 'PulseAudio info'),
        ('pacmd list-sources', 'Audio sources'),
        ('pacmd list-sinks', 'Audio sinks')
    ]
    
    for cmd, description in audio_tests:
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print_success(f"{description} - OK")
            else:
                print_warning(f"{description} - Warning: {result.stderr.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print_warning(f"{description} - Command not found or timeout")
        except Exception as e:
            print_error(f"{description} - Error: {e}")

def generate_install_commands(missing_modules: list, env_name: str = "talkbridge-desktop-env") -> list:
    """Generate install commands for missing modules"""
    
    install_map = {
        'sounddevice': 'sounddevice',
        'mediapipe': 'mediapipe',
        'TTS': 'TTS>=0.22.0',
        'argostranslate': 'argos-translate>=1.9.0',
        'transformers': 'transformers torch',
        'PySide6': 'PySide6>=6.5.0 pyside6-tools',
        'pygame': 'pygame>=2.5.0',
        'librosa': 'librosa>=0.10.0',
        'soundfile': 'soundfile>=0.12.0',
        'pydub': 'pydub>=0.25.0'
    }
    
    commands = []
    for module in missing_modules:
        package = install_map.get(module['module'], module['module'])
        commands.append(f"conda run -n {env_name} pip install {package}")
    
    return commands

def main():
    """Main diagnostic function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Diagnose TalkBridge Desktop installation issues")
    parser.add_argument("--env-name", default="talkbridge-desktop-env",
                       help="Conda environment name to test")
    parser.add_argument("--fix", action="store_true",
                       help="Attempt to fix found issues")
    
    args = parser.parse_args()
    
    print_header("TALKBRIDGE DESKTOP - DIAGNOSTIC REPORT")
    
    # Test core modules that were reported as missing
    missing_modules = []
    core_modules = [
        ('sounddevice', 'sounddevice'),
        ('mediapipe', 'mediapipe'),
        ('TTS', 'TTS'),
        ('argostranslate', 'argos-translate'),
        ('transformers', 'transformers'),
        ('PySide6', 'PySide6'),
        ('PySide6.QtWidgets', 'PySide6'),
        ('pygame', 'pygame'),
        ('librosa', 'librosa'),
        ('soundfile', 'soundfile'),
        ('pydub', 'pydub')
    ]
    
    print_header("MODULE AVAILABILITY TEST")
    for module, package in core_modules:
        result = test_import(module, package)
        if not result['available']:
            missing_modules.append(result)
    
    # Check Qt environment
    qt_ok = check_qt_environment()
    
    # Check audio system
    diagnose_audio_system()
    
    # Generate report
    print_header("DIAGNOSTIC SUMMARY")
    
    if missing_modules:
        print_error(f"Found {len(missing_modules)} missing modules:")
        for module in missing_modules:
            print(f"  - {module['module']}")
        
        print("\nInstall commands:")
        commands = generate_install_commands(missing_modules, args.env_name)
        for cmd in commands:
            print(f"  {cmd}")
        
        if args.fix:
            print_info("Attempting to install missing packages...")
            for cmd in commands:
                try:
                    subprocess.run(cmd.split(), check=True)
                    print_success(f"Installed: {cmd.split()[-1]}")
                except subprocess.CalledProcessError as e:
                    print_error(f"Failed to install: {cmd.split()[-1]} - {e}")
    else:
        print_success("All required modules are available!")
    
    if not qt_ok:
        print_warning("Qt/Wayland issues detected - use post_install_fix.py to resolve")
    
    # Create fix script
    fix_script = Path("quick_fix.sh")
    script_content = "#!/bin/bash\n"
    script_content += "# Quick fix script for TalkBridge Desktop issues\n\n"
    
    if missing_modules:
        script_content += "echo 'Installing missing Python packages...'\n"
        for cmd in commands:
            script_content += f"{cmd}\n"
    
    if not qt_ok:
        script_content += "\necho 'Setting Qt environment for X11...'\n"
        script_content += "export QT_QPA_PLATFORM=xcb\n"
        script_content += "export QT_QPA_PLATFORM_PLUGIN_PATH=''\n"
    
    script_content += "\necho 'Fix script completed!'\n"
    
    fix_script.write_text(script_content)
    fix_script.chmod(0o755)
    
    print_info(f"Created quick fix script: {fix_script}")
    print("Run: ./quick_fix.sh to apply fixes")

if __name__ == "__main__":
    main()
