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
from .controls import *
from .layouts import *
from .widgets import *

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
    'strip_variation_selectors',
    # Control factory functions
    'create_frame',
    'create_button',
    'create_label',
    'create_entry',
    'create_textbox',
    'create_checkbox',
    'create_combobox',
    # Layout utilities
    'create_header_layout',
    'create_section_layout',
    'create_card_layout',
    'create_button_row',
    'create_form_row',
    # Custom widgets
    'StatusIndicator',
    'ActionButton', 
    'InfoCard',
    'ProgressIndicator'
]
