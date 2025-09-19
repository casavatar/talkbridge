#!/usr/bin/env python3
"""
CI Guard: Syntax Error Checker
==============================

This script is designed to be run in CI to ensure no syntax errors
are introduced into the codebase.
"""

import sys
import os
from pathlib import Path

# Import our syntax checker
sys.path.insert(0, str(Path(__file__).parent))
from check_syntax import check_syntax

def main():
    """Main CI guard function."""
    print("🚀 Running CI syntax check...")
    
    success = check_syntax()
    
    if success:
        print("✅ CI Check PASSED: No syntax errors found")
        return 0
    else:
        print("❌ CI Check FAILED: Syntax errors detected")
        print("💡 Run 'python tools/check_syntax.py' locally to see details")
        return 1

if __name__ == "__main__":
    sys.exit(main())