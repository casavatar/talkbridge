#!/usr/bin/env python3
"""
Setup Conda Desktop
===================

setup_conda_desktop module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- None
======================================================================
Functions:
- print_header: Print a formatted header message.
- print_success: Print a success message.
- print_warning: Print a warning message.
- print_error: Print an error message.
- print_info: Print an info message.
- run_command: Run a shell command with proper error handling.
- check_conda_installation: Check if conda is installed and accessible.
- check_environment_file: Check if the environment.yml file exists.
- create_conda_environment: Create the conda environment from the YAML file.
- verify_installation: Verify that the installation was successful.
======================================================================
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path
from typing import List, Optional, Tuple

# Add the src directory to path to import centralized logging
config_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(config_dir)
src_dir = os.path.join(project_root, 'src')
try:
    from logging_config import get_logger, log_exception
    USE_CENTRALIZED_LOGGING = True
except ImportError:
    USE_CENTRALIZED_LOGGING = False

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message: str) -> None:
    """Print a formatted header message."""
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup")
        logger.info(f"SETUP: {message}")
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(message: str) -> None:
    """Print a success message."""
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup")
        logger.info(f"SUCCESS: {message}")
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message: str) -> None:
    """Print a warning message."""
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup")
        logger.warning(message)
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message: str) -> None:
    """Print an error message."""
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup")
        logger.error(message)
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message: str) -> None:
    """Print an info message."""
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup")
        logger.info(message)
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def run_command(command: List[str], description: str, capture_output: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Run a shell command with proper error handling.
    
    Args:
        command: Command to execute as list
        description: Description of what the command does
        capture_output: Whether to capture and return output
        
    Returns:
        Tuple of (success, output)
    """
    print_info(f"Running: {description}")
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup")
        logger.debug(f"Command: {' '.join(command)}")
    else:
        print(f"Command: {' '.join(command)}")
    
    try:
        if capture_output:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return True, result.stdout.strip()
        else:
            subprocess.run(command, check=True)
            return True, None
    except subprocess.CalledProcessError as e:
        print_error(f"Failed: {description}")
        if hasattr(e, 'stderr') and e.stderr:
            print_error(f"Error: {e.stderr}")
        return False, None
    except FileNotFoundError:
        print_error(f"Command not found: {command[0]}")
        return False, None

def check_conda_installation() -> bool:
    """Check if conda is installed and accessible."""
    print_header("CHECKING CONDA INSTALLATION")
    
    success, output = run_command(["conda", "--version"], "Checking conda version", capture_output=True)
    if success and output:
        print_success(f"Conda found: {output}")
        return True
    else:
        print_error("Conda not found or not accessible")
        print_info("Please install Miniconda or Anaconda:")
        print_info("  - Miniconda: https://docs.conda.io/en/latest/miniconda.html")
        print_info("  - Anaconda: https://www.anaconda.com/products/distribution")
        return False

def check_environment_file() -> bool:
    """Check if the environment.yml file exists."""
    # We're running from config directory, so check current directory
    simple_env_file = Path("environment-desktop-simple.yaml")
    full_env_file = Path("environment-desktop.yaml")
    
    if simple_env_file.exists():
        print_success(f"Environment file found: {simple_env_file}")
        return True
    elif full_env_file.exists():
        print_success(f"Environment file found: {full_env_file}")
        return True
    else:
        print_error("Environment file not found: environment-desktop-simple.yaml or environment-desktop.yaml")
        return False

def create_conda_environment(env_name: str = "talkbridge-desktop-env") -> bool:
    """Create the conda environment from the YAML file."""
    print_header("CREATING CONDA ENVIRONMENT")
    
    # Check if environment already exists
    success, output = run_command(
        ["conda", "env", "list"], 
        "Listing existing environments", 
        capture_output=True
    )
    
    if success and output and env_name in output:
        print_warning(f"Environment '{env_name}' already exists")
        response = input(f"Do you want to remove and recreate it? (y/N): ").strip().lower()
        if response in ('y', 'yes'):
            print_info(f"Removing existing environment: {env_name}")
            
            # First try to deactivate if it's currently active
            try:
                run_command(
                    ["conda", "deactivate"],
                    "Deactivating current environment",
                    capture_output=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
                # Ignore if deactivate fails - environment might not be active
                pass
            
            # Force remove with --all flag
            success, _ = run_command(
                ["conda", "env", "remove", "-n", env_name, "--all", "-y"],
                f"Force removing environment {env_name}"
            )
            if not success:
                print_error("Failed to remove existing environment. Trying alternative method...")
                # Try conda remove with force
                success, _ = run_command(
                    ["conda", "remove", "-n", env_name, "--all", "-y"],
                    f"Alternative removal of environment {env_name}"
                )
                if not success:
                    print_error("Could not remove existing environment. Please remove manually:")
                    print_error(f"  conda env remove -n {env_name} --all")
                    return False
        else:
            print_info("Skipping environment creation")
            return True
    
    # Create the environment - try simple version first
    simple_env_file = Path("environment-desktop-simple.yaml")
    full_env_file = Path("environment-desktop.yaml")
    
    env_file_to_use = "environment-desktop-simple.yaml" if simple_env_file.exists() else "environment-desktop.yaml"
    
    print_info(f"Creating environment from: {env_file_to_use}")
    success, _ = run_command(
        ["conda", "env", "create", "-f", env_file_to_use],
        f"Creating conda environment from {env_file_to_use}"
    )
    
    if success:
        print_success(f"Environment '{env_name}' created successfully")
        return True
    else:
        print_error("Failed to create conda environment")
        print_info("You can try manually with:")
        print_info(f"  conda env create -f {env_file_to_use}")
        return False

def verify_installation(env_name: str = "talkbridge-desktop-env") -> bool:
    """Verify that the installation was successful."""
    print_header("VERIFYING INSTALLATION")
    
    # Test PySide6 import
    test_commands = [
        ("python", "-c", "from PySide6.QtWidgets import QApplication; print('PySide6: OK')"),
        ("python", "-c", "import torch; print(f'PyTorch: {torch.__version__}')"),
        ("python", "-c", "import numpy; print(f'NumPy: {numpy.__version__}')"),
        ("python", "-c", "import yaml; print('PyYAML: OK')"),
        ("python", "-c", "import librosa; print('Librosa: OK')"),
    ]
    
    all_success = True
    for test_cmd in test_commands:
        cmd = ["conda", "run", "-n", env_name] + list(test_cmd)
        success, output = run_command(cmd, f"Testing {test_cmd[2].split(';')[0]}", capture_output=True)
        if success and output:
            print_success(output)
        else:
            print_error(f"Failed: {test_cmd[2]}")
            all_success = False
    
    return all_success

def create_activation_scripts(env_name: str = "talkbridge-desktop-env") -> bool:
    """Create convenient activation scripts for different platforms."""
    print_header("CREATING ACTIVATION SCRIPTS")
    
    # Windows batch script
    if platform.system() == "Windows":
        batch_content = f"""@echo off
REM TalkBridge Desktop - Conda Environment Activation Script
REM =========================================================

echo.
echo 🚀 Activating TalkBridge Desktop Environment...
echo.

call conda activate {env_name}

if %ERRORLEVEL% EQU 0 (
    echo ✓ Environment activated successfully!
    echo.
    echo Available commands:
    echo   python src/desktop/main.py    - Start desktop application
    echo   pytest src/desktop/           - Run tests
    echo.
    echo To deactivate: conda deactivate
    echo.
) else (
    echo ✗ Failed to activate environment
    echo Please run: conda env create -f environment-desktop.yaml
    pause
)
"""
        
        script_path = Path("activate_desktop.bat")
        script_path.write_text(batch_content, encoding='utf-8')
        print_success(f"Created Windows activation script: {script_path}")
    
    # Unix shell script
    shell_content = f"""#!/bin/bash
# TalkBridge Desktop - Conda Environment Activation Script
# =========================================================

echo ""
echo "🚀 Activating TalkBridge Desktop Environment..."
echo ""

# Initialize conda for shell
eval "$(conda shell.bash hook)"

# Activate environment
conda activate {env_name}

if [ $? -eq 0 ]; then
    echo "✓ Environment activated successfully!"
    echo ""
    echo "Available commands:"
    echo "  python src/desktop/main.py    - Start desktop application"
    echo "  pytest src/desktop/           - Run tests"
    echo ""
    echo "To deactivate: conda deactivate"
    echo ""
    
    # Start a new shell with the environment activated
    exec bash
else
    echo "✗ Failed to activate environment"
    echo "Please run: conda env create -f environment-desktop.yaml"
fi
"""
    
    script_path = Path("activate_desktop.sh")
    script_path.write_text(shell_content, encoding='utf-8')
    script_path.chmod(0o755)  # Make executable
    print_success(f"Created Unix activation script: {script_path}")
    
    return True

def print_installation_summary(env_name: str = "talkbridge-desktop-env") -> None:
    """Print installation summary and next steps."""
    print_header("INSTALLATION COMPLETE")
    
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup")
        logger.info(f"TalkBridge Desktop environment {env_name} is ready!")
        logger.info(f"Environment details: Python 3.11, PySide6, PyTorch")
    
    print(f"{Colors.OKGREEN}🎉 TalkBridge Desktop environment is ready!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Environment Name:{Colors.ENDC} {env_name}")
    print(f"{Colors.BOLD}Python Version:{Colors.ENDC} 3.11")
    print(f"{Colors.BOLD}GUI Framework:{Colors.ENDC} PySide6")
    print(f"{Colors.BOLD}AI Framework:{Colors.ENDC} PyTorch\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"1. Activate the environment:")
    if platform.system() == "Windows":
        print(f"   {Colors.OKCYAN}activate_desktop.bat{Colors.ENDC}")
        print(f"   or: {Colors.OKCYAN}conda activate {env_name}{Colors.ENDC}")
    else:
        print(f"   {Colors.OKCYAN}source activate_desktop.sh{Colors.ENDC}")
        print(f"   or: {Colors.OKCYAN}conda activate {env_name}{Colors.ENDC}")
    
    print(f"\n2. Start the desktop application:")
    print(f"   {Colors.OKCYAN}python src/desktop/main.py{Colors.ENDC}")
    
    print(f"\n3. Run tests:")
    print(f"   {Colors.OKCYAN}pytest src/desktop/{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Advantages of Conda Installation:{Colors.ENDC}")
    print(f"✓ Better dependency management for GUI applications")
    print(f"✓ Optimized PyTorch with GPU support")
    print(f"✓ Pre-compiled scientific packages (faster installation)")
    print(f"✓ Isolated environment prevents conflicts")
    print(f"✓ Easy environment reproduction across systems")

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="TalkBridge Desktop Conda Setup")
    parser.add_argument("--env-name", default="talkbridge-desktop-env", 
                       help="Conda environment name (default: talkbridge-desktop-env)")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify existing installation")
    parser.add_argument("--create-scripts-only", action="store_true",
                       help="Only create activation scripts")
    
    args = parser.parse_args()
    
    print_header("TALKBRIDGE DESKTOP - CONDA SETUP")
    print_info(f"Platform: {platform.system()} {platform.release()}")
    print_info(f"Python: {sys.version}")
    print_info(f"Target Environment: {args.env_name}")
    
    # Change to config directory to find environment files
    script_dir = Path(__file__).parent  # Stay in config directory
    os.chdir(script_dir)
    
    if args.verify_only:
        success = verify_installation(args.env_name)
        sys.exit(0 if success else 1)
    
    if args.create_scripts_only:
        create_activation_scripts(args.env_name)
        sys.exit(0)
    
    # Full installation process
    steps = [
        ("Check Conda", lambda: check_conda_installation()),
        ("Check Environment File", lambda: check_environment_file()),
        ("Create Environment", lambda: create_conda_environment(args.env_name)),
        ("Verify Installation", lambda: verify_installation(args.env_name)),
        ("Create Scripts", lambda: create_activation_scripts(args.env_name)),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print_error(f"Setup failed at step: {step_name}")
            sys.exit(1)
    
    print_installation_summary(args.env_name)

if __name__ == "__main__":
    main()