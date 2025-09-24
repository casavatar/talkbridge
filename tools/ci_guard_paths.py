#!/usr/bin/env python3
"""
CI Guard: Path Validation for TalkBridge
========================================

This script validates that no code in the TalkBridge codebase creates or references
incorrect paths like `src/data`. It's designed to run in CI/CD pipelines to prevent
regression of the path issue.

Author: TalkBridge Team
Date: 2025-09-23
Version: 1.0

Exit Codes:
- 0: All checks passed
- 1: Found problematic path patterns
- 2: Script error (missing dependencies, file access issues, etc.)
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict
import argparse


class PathChecker:
    """
    Validates Python code for problematic path patterns that could create src/data.
    """

    # Patterns that are definitely problematic
    FORBIDDEN_PATTERNS = [
        # Direct references to src/data
        re.compile(r'["\']src/data["\']'),
        re.compile(r'["\']src\\data["\']'),

        # Path operations that could create src/data
        re.compile(r'Path\([^)]*\)\s*\/\s*["\']src["\']'),
        re.compile(r'os\.path\.join\([^)]*["\']src["\'].*["\']data["\']'),

        # Specific problematic patterns from the old code
        re.compile(r'Path\(__file__\)\.parent\.parent\s*\/\s*["\']data["\']'),
    ]

    # Patterns that need careful review
    SUSPICIOUS_PATTERNS = [
        # __file__.parent patterns that might resolve incorrectly
        re.compile(r'Path\(__file__\)\.parent\.parent(?!\.parent)'),  # Only 2 parents from src files

        # Relative path constructions
        re.compile(r'os\.path\.join\([^)]*\.\.[^)]*\.\.'),

        # String concatenation that might create bad paths
        re.compile(r'["\']\.\.\/\.\.["\'].*["\']data["\']'),
    ]

    # Files to ignore (these are known to be correct)
    IGNORE_FILES = {
        'scripts/migrate_users.py',  # Correctly uses parent.parent from scripts/
        'tools/ci_guard_paths.py',   # This file itself
        'test/',                     # Test files can have different patterns
        'src/talkbridge/web/test/',  # Web test files using parent.parent for web directory
    }

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[Dict] = []

    def check_file(self, file_path: Path) -> bool:
        """
        Check a single Python file for problematic path patterns.

        Args:
            file_path: Path to the Python file to check

        Returns:
            True if file is clean, False if issues found
        """
        # Skip ignored files
        rel_path = file_path.relative_to(self.project_root)
        for ignore_pattern in self.IGNORE_FILES:
            if str(rel_path).startswith(ignore_pattern):
                return True

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return True  # Skip unreadable files

        lines = content.splitlines()
        file_clean = True

        for line_num, line in enumerate(lines, 1):
            # Check forbidden patterns
            for pattern in self.FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    self.issues.append({
                        'file': str(rel_path),
                        'line': line_num,
                        'content': line.strip(),
                        'severity': 'ERROR',
                        'pattern': pattern.pattern,
                        'message': 'Forbidden path pattern detected'
                    })
                    file_clean = False

            # Check suspicious patterns
            for pattern in self.SUSPICIOUS_PATTERNS:
                if pattern.search(line):
                    # Additional validation for suspicious patterns
                    if self._is_suspicious_pattern_problematic(file_path, line, rel_path):
                        self.issues.append({
                            'file': str(rel_path),
                            'line': line_num,
                            'content': line.strip(),
                            'severity': 'WARNING',
                            'pattern': pattern.pattern,
                            'message': 'Suspicious path pattern - please verify correctness'
                        })

        return file_clean

    def _is_suspicious_pattern_problematic(self, file_path: Path, line: str, rel_path: Path) -> bool:
        """
        Additional validation for suspicious patterns to reduce false positives.
        """
        # If file is in src/talkbridge and uses .parent.parent, it's likely wrong
        if str(rel_path).startswith('src/talkbridge/') and 'parent.parent' in line:
            # Except for specific known-good patterns
            if 'get_project_root' in line or 'project_root' in line:
                return False  # Using our new resolver
            return True

        return False

    def check_directory_structure(self) -> bool:
        """
        Check that no src/data directory exists.

        Returns:
            True if clean, False if src/data exists
        """
        src_data = self.project_root / 'src' / 'data'
        if src_data.exists():
            self.issues.append({
                'file': 'filesystem',
                'line': 0,
                'content': f'Directory exists: {src_data}',
                'severity': 'ERROR',
                'pattern': 'directory_check',
                'message': 'src/data directory should not exist'
            })
            return False
        return True

    def run_all_checks(self) -> bool:
        """
        Run all path validation checks.

        Returns:
            True if all checks passed, False if issues found
        """
        print("Running TalkBridge path validation checks...")

        # Check directory structure first
        structure_ok = self.check_directory_structure()

        # Find all Python files
        python_files = list(self.project_root.rglob('*.py'))
        files_checked = 0
        files_clean = 0

        for py_file in python_files:
            try:
                if self.check_file(py_file):
                    files_clean += 1
                files_checked += 1
            except Exception as e:
                print(f"Error checking {py_file}: {e}")

        print(f"Checked {files_checked} Python files")
        print(f"Clean files: {files_clean}")

        # Report results
        error_count = len([i for i in self.issues if i['severity'] == 'ERROR'])
        warning_count = len([i for i in self.issues if i['severity'] == 'WARNING'])

        if self.issues:
            print(f"\nFound {error_count} errors and {warning_count} warnings:")
            for issue in self.issues:
                severity_icon = "❌" if issue['severity'] == 'ERROR' else "⚠️ "
                print(f"{severity_icon} {issue['file']}:{issue['line']}")
                print(f"   {issue['message']}")
                print(f"   Pattern: {issue['pattern']}")
                print(f"   Code: {issue['content']}")
                print()

        all_passed = structure_ok and error_count == 0

        if all_passed:
            print("✅ All path validation checks passed!")
        else:
            print("❌ Path validation checks failed!")

        return all_passed


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Validate TalkBridge codebase for correct path usage"
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        help="Path to project root (auto-detected if not provided)"
    )
    parser.add_argument(
        '--warnings-as-errors',
        action='store_true',
        help="Treat warnings as errors (fail the check)"
    )

    args = parser.parse_args()

    # Determine project root
    if args.project_root:
        project_root = args.project_root.resolve()
    else:
        # Auto-detect: assume this script is in tools/ directory
        project_root = Path(__file__).parent.parent.resolve()

    if not project_root.exists():
        print(f"Error: Project root does not exist: {project_root}")
        return 2

    # Validate project root
    if not (project_root / 'pyproject.toml').exists():
        print(f"Error: {project_root} does not appear to be TalkBridge project root")
        return 2

    # Run checks
    checker = PathChecker(project_root)
    checks_passed = checker.run_all_checks()

    # Determine exit code
    if not checks_passed:
        return 1  # Errors found

    if args.warnings_as_errors:
        warning_count = len([i for i in checker.issues if i['severity'] == 'WARNING'])
        if warning_count > 0:
            print(f"Treating {warning_count} warnings as errors")
            return 1

    return 0  # All good


if __name__ == '__main__':
    sys.exit(main())