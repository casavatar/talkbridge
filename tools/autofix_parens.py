#!/usr/bin/env python3
"""
Automatic Parentheses Fixer for TalkBridge
==========================================

This script fixes unmatched closing parentheses in Python files,
typically from broken sys.path.append() statements.
"""

import re
import sys
import pathlib
from pathlib import Path

def fix_unmatched_parens(files):
    """Fix unmatched closing parentheses in the specified files."""
    
    # Pattern to match lines ending with too many closing parentheses
    patterns = [
        re.compile(r"\)\)\)\s*$"),      # triple closing paren
        re.compile(r"\)\)\s*$"),        # double closing paren at end of suspicious lines
    ]
    
    total_fixed = 0
    
    for file_path in files:
        if not file_path.strip():
            continue
            
        p = pathlib.Path(file_path)
        if not p.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
            
        try:
            text = p.read_text(encoding="utf-8")
        except Exception as e:
            print(f"❌ Cannot read {file_path}: {e}")
            continue
            
        lines = text.splitlines(True)
        fixed_lines = []
        changed = False
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Check for specific problematic patterns in context
            if ("sys.path.append" in line or 
                "Path(__file__)" in line or
                ".parent" in line):
                
                # Fix triple closing parens
                if patterns[0].search(line):
                    line = patterns[0].sub("))\n", line)
                    changed = True
                    print(f"  Line {i+1}: Fixed triple ')' -> double ')'")
                
                # Fix double closing parens in suspicious contexts
                elif (patterns[1].search(line) and 
                      ("sys.path" in line or ".parent" in line)):
                    line = patterns[1].sub(")\n", line)
                    changed = True
                    print(f"  Line {i+1}: Fixed double ')' -> single ')'")
            
            # Handle specific malformed patterns
            if ", '..', '..')))\"" in line:
                line = line.replace(", '..', '..')))\"", ", '..', '..'))")
                changed = True
                print(f"  Line {i+1}: Fixed malformed path join")
            
            fixed_lines.append(line)
        
        if changed:
            try:
                p.write_text("".join(fixed_lines), encoding="utf-8")
                print(f"✅ Patched: {file_path}")
                total_fixed += 1
            except Exception as e:
                print(f"❌ Cannot write {file_path}: {e}")
        else:
            print(f"ℹ️  No changes needed: {file_path}")
    
    return total_fixed

def main():
    """Main function to process files."""
    if len(sys.argv) < 2:
        print("Usage: python autofix_parens.py <file1> <file2> ...")
        print("   Or: python autofix_parens.py $(cat syntax_errors.txt)")
        sys.exit(1)
    
    files = sys.argv[1:]
    print(f"🔧 Fixing parentheses in {len(files)} files...")
    
    fixed_count = fix_unmatched_parens(files)
    
    print(f"\n📊 Summary: Fixed {fixed_count} files")
    
    if fixed_count > 0:
        print("✅ Run syntax check again to verify fixes")
    else:
        print("ℹ️  No files needed parentheses fixes")

if __name__ == "__main__":
    main()