#!/usr/bin/env python3
"""
Syntax Error Checker for TalkBridge
===================================

This script compiles every Python file in src/ and test/ directories
to identify SyntaxErrors that need to be fixed.
"""

import os
import sys
import py_compile
from pathlib import Path

def check_syntax():
    """Check syntax of all Python files in specified directories."""
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Directories to check for syntax errors
    code_dirs = [
        os.path.join(ROOT, "src"),
        os.path.join(ROOT, "test"),
    ]
    
    # Check if demo directory exists and add it
    demo_dir = os.path.join(ROOT, "demo")
    if os.path.exists(demo_dir):
        code_dirs.append(demo_dir)
    
    errors = []
    checked_files = []
    
    print("🔍 Checking syntax in Python files...")
    
    for base in code_dirs:
        if not os.path.exists(base):
            print(f"⚠️  Directory not found: {base}")
            continue
            
        print(f"📁 Checking {os.path.relpath(base, ROOT)}/")
        
        for dirpath, _, filenames in os.walk(base):
            for filename in filenames:
                if filename.endswith(".py"):
                    filepath = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(filepath, ROOT)
                    checked_files.append(rel_path)
                    
                    try:
                        py_compile.compile(filepath, doraise=True)
                    except py_compile.PyCompileError as e:
                        errors.append((rel_path, str(e)))
                    except SyntaxError as e:
                        errors.append((rel_path, f"SyntaxError: {e}"))
                    except Exception as e:
                        errors.append((rel_path, f"CompileError: {e}"))
    
    print(f"📊 Checked {len(checked_files)} Python files")
    
    if errors:
        print("\n❌ Syntax errors found:")
        for filepath, error in errors:
            print(f"- {filepath}: {error}")
        
        print(f"\n📋 Summary: {len(errors)} files with syntax errors")
        
        # Also write to a file for easy processing
        error_file = os.path.join(ROOT, "syntax_errors.txt")
        with open(error_file, "w") as f:
            for filepath, error in errors:
                f.write(f"{filepath}\n")
        
        print(f"📝 Error file list written to: {error_file}")
        return False
    else:
        print("\n✅ No syntax errors found.")
        
        # Remove error file if it exists
        error_file = os.path.join(ROOT, "syntax_errors.txt")
        if os.path.exists(error_file):
            os.remove(error_file)
        
        return True

if __name__ == "__main__":
    success = check_syntax()
    sys.exit(0 if success else 1)