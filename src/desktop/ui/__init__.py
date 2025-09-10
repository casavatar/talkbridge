#!/usr/bin/env python3
"""
TalkBridge Desktop - UI Module
=============================

UI components including theming and utilities.

Author: TalkBridge Team
Date: 2025-09-09
Version: 1.0
"""

from .theme import (
    ColorPalette, 
    Typography, 
    Dimensions, 
    ComponentThemes, 
    UIText, 
    Icons, 
    UXGuidelines
)
from .ui_utils import icon, clean_text, strip_variation_selectors

__all__ = [
    'ColorPalette',
    'Typography', 
    'Dimensions',
    'ComponentThemes',
    'UIText',
    'Icons',
    'UXGuidelines',
    'icon',
    'clean_text',
    'strip_variation_selectors'
]
