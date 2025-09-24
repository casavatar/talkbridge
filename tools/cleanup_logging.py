#!/usr/bin/env python3
"""
TalkBridge - Logging Cleanup Utility
===================================

Utility script to find and help clean up scattered logging configurations
and print statements throughout the TalkBridge project.

Author: TalkBridge Team
Date: 2025-09-18
Version: 1.0

Features:
- Find remaining print() statements
- Identify logging.basicConfig() calls
- Check for inconsistent logger usage
- Generate cleanup recommendations
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class LoggingIssue:
    """Represents a logging issue found in the code."""
    file_path: str
    line_number: int
    line_content: str
    issue_type: str
    severity: str
    recommendation: str


class LoggingCleanupAnalyzer:
    """Analyzer for logging cleanup issues."""
    
    def __init__(self, project_root: str):
        """Initialize analyzer with project root."""
        self.project_root = Path(project_root)
        self.issues: List[LoggingIssue] = []
        
        # Patterns to detect logging issues
        self.patterns = {
            'print_statement': re.compile(r'^\s*print\s*\('),
            'basic_config': re.compile(r'logging\.basicConfig'),
            'old_logger': re.compile(r'logging\.getLogger'),
            'bare_except': re.compile(r'except\s*:\s*$'),
            'generic_except': re.compile(r'except\s+Exception\s*:\s*$'),
            'raise_exception': re.compile(r'raise\s+Exception\s*\('),
        }
        
        # File extensions to analyze
        self.source_extensions = {'.py'}
        
        # Directories to skip
        self.skip_dirs = {
            '__pycache__', '.git', '.pytest_cache', 
            'node_modules', 'venv', 'env'
        }
    
    def analyze_project(self) -> None:
        """Analyze the entire project for logging issues."""
        print(f"🔍 Analyzing project: {self.project_root}")
        print("=" * 50)
        
        for file_path in self._get_source_files():
            self._analyze_file(file_path)
        
        self._print_summary()
    
    def _get_source_files(self) -> List[Path]:
        """Get all source files to analyze."""
        source_files = []
        
        for path in self.project_root.rglob("*"):
            if (path.is_file() and 
                path.suffix in self.source_extensions and
                not any(skip_dir in path.parts for skip_dir in self.skip_dirs)):
                source_files.append(path)
        
        return source_files
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single file for logging issues."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            for line_num, line in enumerate(lines, 1):
                self._check_line(file_path, line_num, line)
                
        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")
    
    def _check_line(self, file_path: Path, line_num: int, line: str) -> None:
        """Check a single line for logging issues."""
        # Skip comments and docstrings
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            return
        
        # Check for print statements
        if self.patterns['print_statement'].search(line):
            # Skip certain acceptable prints (like in demos)
            if 'demo' in str(file_path).lower() or 'test' in str(file_path).lower():
                severity = "low"
                recommendation = "Consider using logger.info() for demo output"
            else:
                severity = "high"
                recommendation = "Replace with appropriate logger call (debug/info/warning/error)"
            
            self.issues.append(LoggingIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                line_content=line.strip(),
                issue_type="print_statement",
                severity=severity,
                recommendation=recommendation
            ))
        
        # Check for logging.basicConfig
        if self.patterns['basic_config'].search(line):
            self.issues.append(LoggingIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                line_content=line.strip(),
                issue_type="basic_config",
                severity="critical",
                recommendation="Remove and use centralized logging configuration"
            ))
        
        # Check for old logging.getLogger pattern
        if self.patterns['old_logger'].search(line) and 'from src.logging_config import get_logger' not in line:
            self.issues.append(LoggingIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                line_content=line.strip(),
                issue_type="old_logger",
                severity="medium",
                recommendation="Replace with 'from src.logging_config import get_logger'"
            ))
        
        # Check for bare except clauses
        if self.patterns['bare_except'].search(line):
            self.issues.append(LoggingIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                line_content=line.strip(),
                issue_type="bare_except",
                severity="high",
                recommendation="Use specific exception types from src.utils.exceptions"
            ))
        
        # Check for generic Exception catches
        if self.patterns['generic_except'].search(line):
            self.issues.append(LoggingIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                line_content=line.strip(),
                issue_type="generic_except",
                severity="medium",
                recommendation="Use specific exception types when possible"
            ))
        
        # Check for generic Exception raises
        if self.patterns['raise_exception'].search(line):
            self.issues.append(LoggingIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                line_content=line.strip(),
                issue_type="raise_exception",
                severity="high",
                recommendation="Use custom exception types from src.utils.exceptions"
            ))
    
    def _print_summary(self) -> None:
        """Print analysis summary."""
        print(f"\n📊 Analysis Summary")
        print("=" * 30)
        
        # Group issues by type
        issue_counts = {}
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for issue in self.issues:
            issue_counts[issue.issue_type] = issue_counts.get(issue.issue_type, 0) + 1
            severity_counts[issue.severity] += 1
        
        print(f"Total issues found: {len(self.issues)}")
        print(f"Critical: {severity_counts['critical']}")
        print(f"High: {severity_counts['high']}")
        print(f"Medium: {severity_counts['medium']}")
        print(f"Low: {severity_counts['low']}")
        
        print(f"\nIssue breakdown:")
        for issue_type, count in sorted(issue_counts.items()):
            print(f"  {issue_type}: {count}")
        
        # Print detailed issues for critical and high severity
        critical_and_high = [i for i in self.issues if i.severity in ["critical", "high"]]
        
        if critical_and_high:
            print(f"\n🚨 Critical & High Priority Issues:")
            print("=" * 40)
            
            for issue in critical_and_high[:20]:  # Limit to first 20
                print(f"\n📁 {issue.file_path}:{issue.line_number}")
                print(f"   Type: {issue.issue_type} ({issue.severity})")
                print(f"   Code: {issue.line_content}")
                print(f"   Fix:  {issue.recommendation}")
        
        if len(critical_and_high) > 20:
            print(f"\n... and {len(critical_and_high) - 20} more issues")
    
    def generate_cleanup_script(self, output_file: str = "cleanup_recommendations.md") -> None:
        """Generate a cleanup script with recommendations."""
        output_path = self.project_root / output_file
        
        with open(output_path, 'w') as f:
            f.write("# TalkBridge Logging Cleanup Recommendations\n\n")
            f.write("Generated by logging cleanup analyzer\n\n")
            
            # Group by file
            files_with_issues = {}
            for issue in self.issues:
                if issue.file_path not in files_with_issues:
                    files_with_issues[issue.file_path] = []
                files_with_issues[issue.file_path].append(issue)
            
            for file_path, file_issues in sorted(files_with_issues.items()):
                f.write(f"## {file_path}\n\n")
                
                for issue in file_issues:
                    f.write(f"**Line {issue.line_number}** ({issue.severity}): {issue.issue_type}\n")
                    f.write(f"```python\n{issue.line_content}\n```\n")
                    f.write(f"**Recommendation:** {issue.recommendation}\n\n")
        
        print(f"\n📝 Detailed recommendations written to: {output_path}")


def main():
    """Main entry point."""
    # Get project root (parent of this script's directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print("🧹 TalkBridge Logging Cleanup Analyzer")
    print("=" * 50)
    print(f"Project root: {project_root}")
    
    analyzer = LoggingCleanupAnalyzer(str(project_root))
    analyzer.analyze_project()
    analyzer.generate_cleanup_script()
    
    print(f"\n✅ Analysis complete!")
    print("\nNext steps:")
    print("1. Review cleanup_recommendations.md")
    print("2. Priority: Fix critical and high severity issues first")
    print("3. Update imports to use centralized logging")
    print("4. Replace print statements with logger calls")
    print("5. Update exception handling to use custom types")
    print("6. Re-run this analyzer to verify fixes")


if __name__ == "__main__":
    main()