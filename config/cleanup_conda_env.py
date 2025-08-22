#!/usr/bin/env python3
"""
Cleanup Conda Environment
=========================

Script to forcefully remove problematic conda environments

Author: TalkBridge Team
Date: 2025-08-21
Version: 1.0
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Color codes for terminal output
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str) -> None:
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message: str) -> None:
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message: str) -> None:
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def run_command(command, description):
    """Run command and return success status"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"{description} - Success")
            return True
        else:
            print_warning(f"{description} - Warning: {result.stderr.strip()}")
            return False
    except Exception as e:
        print_error(f"{description} - Error: {e}")
        return False

def cleanup_environment(env_name: str) -> bool:
    """Forcefully cleanup a conda environment"""
    print(f"\n{Colors.BOLD}Cleaning up environment: {env_name}{Colors.ENDC}")
    
    # Method 1: Standard conda remove
    print("\n1. Trying standard conda env remove...")
    if run_command(f"conda env remove -n {env_name} -y", "Standard removal"):
        return True
    
    # Method 2: Force remove with --all
    print("\n2. Trying force removal...")
    if run_command(f"conda env remove -n {env_name} --all -y", "Force removal"):
        return True
    
    # Method 3: Alternative conda remove
    print("\n3. Trying alternative removal...")
    if run_command(f"conda remove -n {env_name} --all -y", "Alternative removal"):
        return True
    
    # Method 4: Direct directory removal
    print("\n4. Trying direct directory removal...")
    try:
        # Get conda info to find environments directory
        result = subprocess.run("conda info --envs", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if env_name in line and '/envs/' in line:
                    env_path = line.split()[-1]
                    if Path(env_path).exists():
                        print(f"Found environment at: {env_path}")
                        shutil.rmtree(env_path)
                        print_success("Directory removed successfully")
                        return True
    except Exception as e:
        print_error(f"Directory removal failed: {e}")
    
    # Method 5: Manual cleanup instructions
    print(f"\n5. Manual cleanup required:")
    print_warning("Please try the following commands manually:")
    print(f"   conda clean --all")
    print(f"   conda env remove -n {env_name}")
    print(f"   rm -rf $(conda info --base)/envs/{env_name}")
    
    return False

def main():
    """Main cleanup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup problematic conda environments")
    parser.add_argument("env_name", help="Name of the environment to cleanup")
    parser.add_argument("--force", action="store_true", help="Skip confirmation")
    
    args = parser.parse_args()
    
    if not args.force:
        response = input(f"Are you sure you want to remove environment '{args.env_name}'? (y/N): ")
        if response.lower() not in ('y', 'yes'):
            print("Cleanup cancelled")
            return
    
    if cleanup_environment(args.env_name):
        print_success(f"Environment '{args.env_name}' has been removed")
    else:
        print_error(f"Failed to remove environment '{args.env_name}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
