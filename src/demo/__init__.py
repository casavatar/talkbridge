#!/usr/bin/env python3
"""
TalkBridge Demo -   Init   - Package Initialization
===================================================

Inicialización del paquete

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
"""

from .demo_config import (
    is_demo_mode, get_demo_setting, get_demo_file_path,
    DEMO_MODE, DEMO_SETTINGS, DEMO_FILES, DEMO_CONVERSATION_FLOW,
    ensure_demo_files_exist
)

from .demo_runner import (
    DemoRunner, get_demo_runner, run_demo_conversation
)

from .demo_api import (
    DemoTTsAPI, DemoSTTAPI, DemoLLMAPI, DemoTranslationAPI,
    DemoAnimationAPI, DemoAudioAPI,
    get_api_instance, get_tts_api, get_stt_api, get_llm_api,
    get_translation_api, get_animation_api, get_audio_api
)

from .demo_ui import (
    render_demo_dashboard, render_demo_header, render_demo_status,
    render_demo_audio_recorder, render_demo_transcription,
    render_demo_translation, render_demo_llm_response,
    render_demo_voice_synthesis, render_demo_avatar,
    render_demo_conversation_log, render_demo_full_conversation,
    render_demo_settings
)

__all__ = [
    # Configuration
    'is_demo_mode', 'get_demo_setting', 'get_demo_file_path',
    'DEMO_MODE', 'DEMO_SETTINGS', 'DEMO_FILES', 'DEMO_CONVERSATION_FLOW',
    'ensure_demo_files_exist',
    
    # Runner
    'DemoRunner', 'get_demo_runner', 'run_demo_conversation',
    
    # APIs
    'DemoTTsAPI', 'DemoSTTAPI', 'DemoLLMAPI', 'DemoTranslationAPI',
    'DemoAnimationAPI', 'DemoAudioAPI',
    'get_api_instance', 'get_tts_api', 'get_stt_api', 'get_llm_api',
    'get_translation_api', 'get_animation_api', 'get_audio_api',
    
    # UI Components
    'render_demo_dashboard', 'render_demo_header', 'render_demo_status',
    'render_demo_audio_recorder', 'render_demo_transcription',
    'render_demo_translation', 'render_demo_llm_response',
    'render_demo_voice_synthesis', 'render_demo_avatar',
    'render_demo_conversation_log', 'render_demo_full_conversation',
    'render_demo_settings'
]

# Version info
__version__ = "1.0.0"
__author__ = "TalkBridge Team"
__email__ = "team@talkbridge.ai"

# Initialize demo files on import
try:
    ensure_demo_files_exist()
except Exception as e:
    print(f"Warning: Could not initialize demo files: {e}") 