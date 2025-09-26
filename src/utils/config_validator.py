#!/usr/bin/env python3
"""
TalkBridge Configuration Validator
==================================

Validates configuration settings for security and correctness.
Ensures no hard-coded secrets and proper environment variable usage.

Author: TalkBridge Team
Date: 2025-01-15
Version: 1.0
"""

import os
import re
import warnings
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..logging_config import get_logger

logger = get_logger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationIssue:
    """Represents a configuration validation issue."""
    level: ValidationLevel
    category: str
    message: str
    location: Optional[str] = None
    recommendation: Optional[str] = None


class ConfigValidator:
    """
    Validates TalkBridge configuration for security and correctness.
    """

    def __init__(self):
        self.issues: List[ValidationIssue] = []
        self.required_env_vars = [
            "SESSION_SECRET",
            "TALKBRIDGE_PASSWORD_ADMIN",
            "TALKBRIDGE_PASSWORD_MODERATOR",
            "TALKBRIDGE_PASSWORD_SUPPORT",
            "TALKBRIDGE_PASSWORD_ANALYST",
            "TALKBRIDGE_PASSWORD_DEVELOPER",
            "TALKBRIDGE_PASSWORD_TRANSLATOR",
            "TALKBRIDGE_PASSWORD_GUEST",
            "TALKBRIDGE_PASSWORD_DEMO",
            "TALKBRIDGE_PASSWORD_AUDITOR",
            "TALKBRIDGE_PASSWORD_OPERATOR",
        ]

        # Patterns that indicate security issues
        self.security_patterns = {
            "hardcoded_password": re.compile(r'password\s*=\s*["\'][^"\']*[A-Z][^"\']*[0-9][^"\']*[!@#$%^&*][^"\']*["\']', re.IGNORECASE),
            "hardcoded_secret": re.compile(r'secret\s*=\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
            "hardcoded_token": re.compile(r'token\s*=\s*["\'][^"\']{16,}["\']', re.IGNORECASE),
            "hardcoded_key": re.compile(r'api_key\s*=\s*["\'][^"\']{16,}["\']', re.IGNORECASE),
            "weak_default": re.compile(r'(admin123|password123|secret|default)', re.IGNORECASE),
        }

    def validate_environment_variables(self) -> None:
        """Validate required environment variables."""
        logger.info("Validating environment variables...")

        missing_vars = []
        weak_vars = []

        for env_var in self.required_env_vars:
            value = os.getenv(env_var)

            if not value:
                missing_vars.append(env_var)
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.CRITICAL,
                    category="Missing Environment Variable",
                    message=f"Required environment variable '{env_var}' is not set",
                    recommendation=f"Set {env_var} environment variable with a secure value"
                ))
            else:
                # Check for weak values
                if env_var == "SESSION_SECRET" and len(value) < 32:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        category="Weak Session Secret",
                        message="SESSION_SECRET is too short (minimum 32 characters)",
                        recommendation="Generate a longer session secret using cryptographically secure methods"
                    ))

                if any(pattern.search(value) for pattern in [
                    re.compile(r'(admin|password|secret|default)123', re.IGNORECASE),
                    re.compile(r'^(admin|password|secret|default)$', re.IGNORECASE)
                ]):
                    weak_vars.append(env_var)
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        category="Weak Password",
                        message=f"Environment variable '{env_var}' contains a weak or default password",
                        recommendation="Use a strong, randomly generated password"
                    ))

        if not missing_vars and not weak_vars:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category="Environment Variables",
                message="All required environment variables are properly configured",
            ))

    def validate_source_code(self, src_dir: Path) -> None:
        """Validate source code for embedded secrets."""
        logger.info("Scanning source code for security issues...")

        python_files = list(src_dir.rglob("*.py"))
        issues_found = 0

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                    for line_num, line in enumerate(lines, 1):
                        for pattern_name, pattern in self.security_patterns.items():
                            if pattern.search(line):
                                issues_found += 1
                                self.issues.append(ValidationIssue(
                                    level=ValidationLevel.CRITICAL,
                                    category="Embedded Secret",
                                    message=f"Potential {pattern_name.replace('_', ' ')} found in source code",
                                    location=f"{file_path.relative_to(src_dir)}:{line_num}",
                                    recommendation="Remove hard-coded secrets and use environment variables"
                                ))

            except Exception as e:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="File Access",
                    message=f"Could not scan file {file_path}: {e}",
                ))

        if issues_found == 0:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category="Source Code Security",
                message="No embedded secrets detected in source code",
            ))

    def validate_configuration_files(self, config_dir: Path) -> None:
        """Validate configuration files for security issues."""
        logger.info("Validating configuration files...")

        config_files = [
            *config_dir.rglob("*.yaml"),
            *config_dir.rglob("*.yml"),
            *config_dir.rglob("*.json"),
            *config_dir.rglob("*.ini"),
            *config_dir.rglob("*.cfg"),
        ]

        issues_found = 0

        for file_path in config_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                    for line_num, line in enumerate(lines, 1):
                        # Check for embedded secrets in config files
                        for pattern_name, pattern in self.security_patterns.items():
                            if pattern.search(line):
                                issues_found += 1
                                self.issues.append(ValidationIssue(
                                    level=ValidationLevel.ERROR,
                                    category="Config Security",
                                    message=f"Potential {pattern_name.replace('_', ' ')} in config file",
                                    location=f"{file_path.relative_to(config_dir)}:{line_num}",
                                    recommendation="Use environment variable references instead of hard-coded values"
                                ))

            except Exception as e:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="Config File Access",
                    message=f"Could not scan config file {file_path}: {e}",
                ))

        if issues_found == 0:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                category="Configuration Security",
                message="No embedded secrets detected in configuration files",
            ))

    def validate_password_policies(self) -> None:
        """Validate password policy compliance."""
        logger.info("Validating password policies...")

        try:
            from ..auth.utils.password_config import PasswordConfig

            # Check password configuration
            if PasswordConfig.MIN_LENGTH < 16:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="Password Policy",
                    message=f"Minimum password length is {PasswordConfig.MIN_LENGTH}, recommend 16+ characters",
                    recommendation="Increase minimum password length to 16 or more characters"
                ))

            # Validate that all required character types are enforced
            requirements = [
                ("uppercase", PasswordConfig.REQUIRE_UPPERCASE),
                ("lowercase", PasswordConfig.REQUIRE_LOWERCASE),
                ("digits", PasswordConfig.REQUIRE_DIGITS),
                ("special characters", PasswordConfig.REQUIRE_SPECIAL),
            ]

            missing_requirements = [req for req, enabled in requirements if not enabled]
            if missing_requirements:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="Password Policy",
                    message=f"Password policy missing requirements: {', '.join(missing_requirements)}",
                    recommendation="Enable all character type requirements for stronger passwords"
                ))
            else:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    category="Password Policy",
                    message="Password policy meets security requirements",
                ))

        except ImportError:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                category="Password Configuration",
                message="Could not import PasswordConfig - password validation skipped",
            ))

    def validate_production_readiness(self) -> None:
        """Validate production readiness settings."""
        logger.info("Validating production readiness...")

        # Check for development mode indicators
        dev_indicators = [
            ("DEBUG", "true"),
            ("DEVELOPMENT_MODE", "true"),
            ("TALKBRIDGE_DEV_MODE", "true"),
            ("FLASK_DEBUG", "1"),
            ("FLASK_ENV", "development"),
        ]

        dev_mode_enabled = []
        for env_var, bad_value in dev_indicators:
            value = os.getenv(env_var, "").lower()
            if value == bad_value.lower():
                dev_mode_enabled.append(env_var)

        if dev_mode_enabled:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                category="Production Readiness",
                message=f"Development mode indicators found: {', '.join(dev_mode_enabled)}",
                recommendation="Disable development mode for production deployment"
            ))

        # Check for secure defaults
        security_vars = [
            ("LOG_LEVEL", ["DEBUG"], "Set to INFO or WARNING for production"),
        ]

        for env_var, bad_values, recommendation in security_vars:
            value = os.getenv(env_var, "").upper()
            if value in bad_values:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    category="Production Security",
                    message=f"{env_var} is set to '{value}' which may expose sensitive information",
                    recommendation=recommendation
                ))

    def run_full_validation(self, project_root: Optional[Path] = None) -> List[ValidationIssue]:
        """
        Run complete configuration validation.

        Args:
            project_root: Project root directory (auto-detected if None)

        Returns:
            List of validation issues found
        """
        logger.info("Starting comprehensive configuration validation...")

        if project_root is None:
            from .project_root import get_project_root
            project_root = get_project_root()

        src_dir = project_root / "src"
        config_dir = project_root / "config"

        # Clear previous issues
        self.issues = []

        # Run all validation checks
        self.validate_environment_variables()
        self.validate_password_policies()

        if src_dir.exists():
            self.validate_source_code(src_dir)

        if config_dir.exists():
            self.validate_configuration_files(config_dir)

        self.validate_production_readiness()

        logger.info(f"Configuration validation completed - {len(self.issues)} issues found")
        return self.issues

    def get_issues_by_level(self, level: ValidationLevel) -> List[ValidationIssue]:
        """Get issues filtered by severity level."""
        return [issue for issue in self.issues if issue.level == level]

    def get_summary(self) -> Dict[str, int]:
        """Get validation summary by severity level."""
        return {
            level.value: len(self.get_issues_by_level(level))
            for level in ValidationLevel
        }

    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return len(self.get_issues_by_level(ValidationLevel.CRITICAL)) > 0

    def print_report(self) -> None:
        """Print a detailed validation report."""
        print("\n🔍 TalkBridge Configuration Validation Report")
        print("=" * 60)

        summary = self.get_summary()
        total_issues = sum(summary.values())

        print(f"\n📊 SUMMARY")
        print("-" * 20)
        print(f"Total Issues: {total_issues}")
        for level in ValidationLevel:
            count = summary[level.value]
            icon = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "CRITICAL": "🚨"}[level.value]
            print(f"{icon} {level.value}: {count}")

        if not self.issues:
            print("\n✅ No issues found - configuration is secure!")
            return

        # Group issues by level for organized display
        for level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR, ValidationLevel.WARNING, ValidationLevel.INFO]:
            issues_at_level = self.get_issues_by_level(level)
            if not issues_at_level:
                continue

            icon = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "CRITICAL": "🚨"}[level.value]
            print(f"\n{icon} {level.value} ISSUES ({len(issues_at_level)})")
            print("-" * 40)

            for i, issue in enumerate(issues_at_level, 1):
                print(f"\n{i}. {issue.category}")
                print(f"   Message: {issue.message}")
                if issue.location:
                    print(f"   Location: {issue.location}")
                if issue.recommendation:
                    print(f"   Fix: {issue.recommendation}")

        # Overall security status
        print("\n" + "=" * 60)
        if self.has_critical_issues():
            print("🚨 CRITICAL SECURITY ISSUES DETECTED")
            print("   System is NOT safe for production use")
            print("   Fix critical issues immediately")
        elif summary[ValidationLevel.ERROR.value] > 0:
            print("⚠️ SECURITY ISSUES DETECTED")
            print("   System has security weaknesses")
            print("   Recommend fixing before production deployment")
        elif summary[ValidationLevel.WARNING.value] > 0:
            print("⚠️ MINOR ISSUES DETECTED")
            print("   System is usable but could be improved")
        else:
            print("✅ CONFIGURATION IS SECURE")
            print("   System passes all security validation checks")


def main():
    """CLI entry point for configuration validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate TalkBridge configuration")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    validator = ConfigValidator()
    issues = validator.run_full_validation(args.project_root)

    if args.json:
        import json
        result = {
            "summary": validator.get_summary(),
            "has_critical_issues": validator.has_critical_issues(),
            "issues": [
                {
                    "level": issue.level.value,
                    "category": issue.category,
                    "message": issue.message,
                    "location": issue.location,
                    "recommendation": issue.recommendation,
                }
                for issue in issues
            ]
        }
        print(json.dumps(result, indent=2))
    else:
        validator.print_report()

    # Exit with error code if critical issues found
    if validator.has_critical_issues():
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())