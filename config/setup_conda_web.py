#!/usr/bin/env python3
"""
Setup Conda Web
===============

setup_conda_web module for TalkBridge Web Environment

Author: TalkBridge Team
Date: 2025-09-25
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
- check_environment_file: Check if the environment-web.yml file exists.
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
        logger = get_logger("talkbridge.config.setup_web")
        logger.info(f"WEB SETUP: {message}")
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(message: str) -> None:
    """Print a success message."""
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup_web")
        logger.info(f"SUCCESS: {message}")
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message: str) -> None:
    """Print a warning message."""
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup_web")
        logger.warning(message)
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message: str) -> None:
    """Print an error message."""
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup_web")
        logger.error(message)
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message: str) -> None:
    """Print an info message."""
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup_web")
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
        logger = get_logger("talkbridge.config.setup_web")
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
    """Check if the environment-web.yml file exists."""
    # We're running from config directory, so check current directory
    web_env_file = Path("environment-web.yaml")
    
    if web_env_file.exists():
        print_success(f"Environment file found: {web_env_file}")
        return True
    else:
        print_error("Environment file not found: environment-web.yaml")
        print_info("Please ensure the web environment file exists in the config/ directory")
        return False

def create_conda_environment(env_name: str = "talkbridge-web-env") -> bool:
    """Create the conda environment from the YAML file."""
    print_header("CREATING CONDA WEB ENVIRONMENT")
    
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
            except (subprocess.CalledProcessError, FileNotFoundError, OSError):
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
    
    # Create the environment
    web_env_file = Path("environment-web.yaml")
    
    print_info(f"Creating web environment from: {web_env_file}")
    success, _ = run_command(
        ["conda", "env", "create", "-f", "environment-web.yaml"],
        f"Creating conda web environment from {web_env_file}"
    )
    
    if success:
        print_success(f"Web environment '{env_name}' created successfully")
        return True
    else:
        print_error("Failed to create conda web environment")
        print_info("You can try manually with:")
        print_info(f"  conda env create -f environment-web.yaml")
        return False

def verify_installation(env_name: str = "talkbridge-web-env") -> bool:
    """Verify that the web installation was successful."""
    print_header("VERIFYING WEB INSTALLATION")
    
    # Test web-specific imports
    test_commands = [
        ("python", "-c", "import flask; print(f'Flask: {flask.__version__}')"),
        ("python", "-c", "import streamlit; print(f'Streamlit: {streamlit.__version__}')"),
        ("python", "-c", "import requests; print(f'Requests: {requests.__version__}')"),
        ("python", "-c", "import yaml; print('PyYAML: OK')"),
        ("python", "-c", "from flask_cors import CORS; print('Flask-CORS: OK')"),
        ("python", "-c", "import gunicorn; print(f'Gunicorn: {gunicorn.__version__}')"),
        ("python", "-c", "import ollama; print('Ollama client: OK')"),
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

def create_activation_scripts(env_name: str = "talkbridge-web-env") -> bool:
    """Create convenient activation scripts for different platforms."""
    print_header("CREATING WEB ACTIVATION SCRIPTS")
    
    # Windows batch script
    if platform.system() == "Windows":
        batch_content = f"""@echo off
REM TalkBridge Web - Conda Environment Activation Script
REM ===================================================

echo.
echo 🌐 Activating TalkBridge Web Environment...
echo.

call conda activate {env_name}

if %ERRORLEVEL% EQU 0 (
    echo ✓ Web environment activated successfully!
    echo.
    echo Available commands:
    echo   python src/talkbridge/web/server.py       - Start Flask web server
    echo   streamlit run src/talkbridge/web/interface.py - Start Streamlit app
    echo   gunicorn --bind 0.0.0.0:8080 talkbridge.web.server:app - Production server
    echo   pytest src/talkbridge/web/                - Run web tests
    echo.
    echo To deactivate: conda deactivate
    echo.
) else (
    echo ✗ Failed to activate web environment
    echo Please run: conda env create -f environment-web.yaml
    pause
)
"""
        
        script_path = Path("activate_web.bat")
        script_path.write_text(batch_content, encoding='utf-8')
        print_success(f"Created Windows web activation script: {script_path}")
    
    # Unix shell script
    shell_content = f"""#!/bin/bash
# TalkBridge Web - Conda Environment Activation Script
# ===================================================

echo ""
echo "🌐 Activating TalkBridge Web Environment..."
echo ""

# Initialize conda for shell
eval "$(conda shell.bash hook)"

# Activate environment
conda activate {env_name}

if [ $? -eq 0 ]; then
    echo "✓ Web environment activated successfully!"
    echo ""
    echo "Available commands:"
    echo "  python src/talkbridge/web/server.py       - Start Flask web server"
    echo "  streamlit run src/talkbridge/web/interface.py - Start Streamlit app"
    echo "  gunicorn --bind 0.0.0.0:8080 talkbridge.web.server:app - Production server"
    echo "  pytest src/talkbridge/web/                - Run web tests"
    echo ""
    echo "To deactivate: conda deactivate"
    echo ""
    
    # Start a new shell with the environment activated
    exec bash
else
    echo "✗ Failed to activate web environment"
    echo "Please run: conda env create -f environment-web.yaml"
fi
"""
    
    script_path = Path("activate_web.sh")
    script_path.write_text(shell_content, encoding='utf-8')
    script_path.chmod(0o755)  # Make executable
    print_success(f"Created Unix web activation script: {script_path}")
    
    return True

def print_installation_summary(env_name: str = "talkbridge-web-env") -> None:
    """Print installation summary and next steps."""
    print_header("WEB INSTALLATION COMPLETE")
    
    if USE_CENTRALIZED_LOGGING:
        logger = get_logger("talkbridge.config.setup_web")
        logger.info(f"TalkBridge Web environment {env_name} is ready!")
        logger.info(f"Environment details: Python 3.11, Flask, Streamlit")
    
    print(f"{Colors.OKGREEN}🌐 TalkBridge Web environment is ready!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Environment Name:{Colors.ENDC} {env_name}")
    print(f"{Colors.BOLD}Python Version:{Colors.ENDC} 3.11")
    print(f"{Colors.BOLD}Web Framework:{Colors.ENDC} Flask + Streamlit")
    print(f"{Colors.BOLD}Production Server:{Colors.ENDC} Gunicorn")
    print(f"{Colors.BOLD}Size:{Colors.ENDC} ~200MB (87% smaller than desktop)\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}")
    print(f"1. Activate the web environment:")
    if platform.system() == "Windows":
        print(f"   {Colors.OKCYAN}activate_web.bat{Colors.ENDC}")
        print(f"   or: {Colors.OKCYAN}conda activate {env_name}{Colors.ENDC}")
    else:
        print(f"   {Colors.OKCYAN}source activate_web.sh{Colors.ENDC}")
        print(f"   or: {Colors.OKCYAN}conda activate {env_name}{Colors.ENDC}")
    
    print(f"\n2. Start the web application:")
    print(f"   Development (Flask): {Colors.OKCYAN}python src/talkbridge/web/server.py{Colors.ENDC}")
    print(f"   Development (Streamlit): {Colors.OKCYAN}streamlit run src/talkbridge/web/interface.py{Colors.ENDC}")
    print(f"   Production: {Colors.OKCYAN}gunicorn --bind 0.0.0.0:8080 talkbridge.web.server:app{Colors.ENDC}")
    
    print(f"\n3. Run web tests:")
    print(f"   {Colors.OKCYAN}pytest src/talkbridge/web/{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Web Environment Advantages:{Colors.ENDC}")
    print(f"✓ Lightweight deployment (~200MB vs ~1.5GB)")
    print(f"✓ Fast startup and installation")
    print(f"✓ Web-only dependencies (no GUI/audio overhead)")
    print(f"✓ Production-ready with Gunicorn/Uvicorn")
    print(f"✓ Container-friendly for Docker deployment")
    print(f"✓ Isolated environment prevents conflicts")

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="TalkBridge Web Conda Setup")
    parser.add_argument("--env-name", default="talkbridge-web-env", 
                       help="Conda environment name (default: talkbridge-web-env)")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify existing installation")
    parser.add_argument("--create-scripts-only", action="store_true",
                       help="Only create activation scripts")
    
    args = parser.parse_args()
    
    print_header("TALKBRIDGE WEB - CONDA SETUP")
    print_info(f"Platform: {platform.system()} {platform.release()}")
    print_info(f"Python: {sys.version}")
    print_info(f"Target Environment: {args.env_name}")
    print_info(f"Deployment Type: Web-only (Flask + Streamlit)")
    
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
        ("Create Web Environment", lambda: create_conda_environment(args.env_name)),
        ("Verify Web Installation", lambda: verify_installation(args.env_name)),
        ("Create Web Scripts", lambda: create_activation_scripts(args.env_name)),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print_error(f"Web setup failed at step: {step_name}")
            sys.exit(1)
    
    print_installation_summary(args.env_name)

if __name__ == "__main__":
    main()