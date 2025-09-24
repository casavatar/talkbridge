#!/usr/bin/env python3
"""
TalkBridge - Robust Project Root Resolution
==========================================

Provides a reliable way to find the project root directory from anywhere in the codebase.
This module prevents the creation of incorrect paths like `src/data` by providing
a centralized, reliable project root resolver.

Author: TalkBridge Team
Date: 2025-09-23
Version: 1.0

Features:
- Multiple fallback strategies for finding project root
- Environment variable override support (TALKBRIDGE_DATA_DIR)
- Caching for performance
- Type-safe Path objects
- Validation to ensure correct directory structure
"""

import os
from pathlib import Path
from typing import Optional
import logging

# Cache for project root to avoid repeated filesystem operations
_cached_project_root: Optional[Path] = None


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """
    Find the TalkBridge project root directory using multiple strategies.

    This function searches for the project root by looking for characteristic
    files and directory structures that uniquely identify the TalkBridge project.

    Args:
        start_path: Path to start searching from (defaults to this file's location)

    Returns:
        Path object pointing to the project root directory

    Raises:
        RuntimeError: If project root cannot be determined

    Strategies (in order):
    1. Environment variable TALKBRIDGE_PROJECT_ROOT
    2. Look for pyproject.toml with TalkBridge metadata
    3. Look for characteristic directory structure (src/talkbridge, data, etc.)
    4. Traverse up from start_path looking for markers
    """
    global _cached_project_root

    # Return cached value if available
    if _cached_project_root is not None:
        return _cached_project_root

    # Strategy 1: Check environment variable
    env_root = os.getenv("TALKBRIDGE_PROJECT_ROOT")
    if env_root:
        project_root = Path(env_root).resolve()
        if _validate_project_root(project_root):
            _cached_project_root = project_root
            return project_root
        else:
            logging.warning(f"TALKBRIDGE_PROJECT_ROOT points to invalid directory: {env_root}")

    # Strategy 2: Start from provided path or this file's location
    if start_path is None:
        start_path = Path(__file__).resolve().parent
    else:
        start_path = Path(start_path).resolve()

    # Strategy 3: Look for project markers
    current = start_path
    max_depth = 10  # Prevent infinite loops
    depth = 0

    while depth < max_depth:
        # Check for TalkBridge-specific markers
        markers = [
            current / "pyproject.toml",
            current / "src" / "talkbridge",
            current / "README.md",
        ]

        # If we find pyproject.toml, verify it's TalkBridge's
        pyproject_file = current / "pyproject.toml"
        if pyproject_file.exists():
            try:
                content = pyproject_file.read_text(encoding='utf-8')
                if 'name = "talkbridge"' in content or '"talkbridge"' in content:
                    if _validate_project_root(current):
                        _cached_project_root = current
                        return current
            except Exception:
                pass  # Continue searching

        # Check for characteristic directory structure
        if (current / "src" / "talkbridge").exists():
            if _validate_project_root(current):
                _cached_project_root = current
                return current

        # Move up one directory
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
        depth += 1

    # Strategy 4: Fallback - assume this file is in src/talkbridge/utils/
    # So project root should be ../../../ from here
    fallback_root = Path(__file__).resolve().parent.parent.parent.parent
    if _validate_project_root(fallback_root):
        _cached_project_root = fallback_root
        return fallback_root

    # If all strategies fail, raise an error
    raise RuntimeError(
        f"Could not determine TalkBridge project root. "
        f"Searched from: {start_path}. "
        f"Please set TALKBRIDGE_PROJECT_ROOT environment variable."
    )


def _validate_project_root(path: Path) -> bool:
    """
    Validate that a path is the correct TalkBridge project root.

    Args:
        path: Path to validate

    Returns:
        True if path appears to be the TalkBridge project root
    """
    if not path.is_dir():
        return False

    # Check for required directories and files
    required_items = [
        path / "src" / "talkbridge",
        path / "pyproject.toml",
    ]

    # At least these items should exist
    for item in required_items:
        if not item.exists():
            return False

    return True


def get_project_root() -> Path:
    """
    Get the TalkBridge project root directory.

    This is the main function to use throughout the codebase.

    Returns:
        Path object pointing to the project root directory
    """
    return find_project_root()


def get_data_dir() -> Path:
    """
    Get the data directory path with environment variable override support.

    Returns:
        Path object pointing to the data directory

    Environment Variables:
        TALKBRIDGE_DATA_DIR: Override the default data directory location
    """
    # Check for environment override
    env_data_dir = os.getenv("TALKBRIDGE_DATA_DIR")
    if env_data_dir:
        return Path(env_data_dir).resolve()

    # Default: data/ directory in project root
    return get_project_root() / "data"


def get_logs_dir() -> Path:
    """
    Get the logs directory path.

    Returns:
        Path object pointing to the logs directory (data/logs)
    """
    return get_data_dir() / "logs"


def ensure_data_directories() -> None:
    """
    Ensure all required data directories exist.

    Creates:
        - data/
        - data/logs/
        - data/audio/
        - data/models/
        - data/avatars/
        - data/temp/
    """
    data_dir = get_data_dir()

    directories = [
        data_dir,
        data_dir / "logs",
        data_dir / "audio",
        data_dir / "models",
        data_dir / "avatars",
        data_dir / "temp",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def reset_cache() -> None:
    """
    Reset the cached project root.

    This should only be used in tests or when the project structure changes.
    """
    global _cached_project_root
    _cached_project_root = None


# For convenience, expose the main function at module level
PROJECT_ROOT = get_project_root()
DATA_DIR = get_data_dir()
LOGS_DIR = get_logs_dir()