"""
TalkBridge Ollama -   Init   - Package Initialization
=====================================================

Inicialización del paquete

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- requests
"""

from .ollama_client import OllamaClient
from .model_manager import OllamaModelManager
from .conversation_manager import ConversationManager
from .prompt_engineer import PromptEngineer
from .streaming_client import OllamaStreamingClient

__all__ = [
    'OllamaClient',
    'OllamaModelManager', 
    'ConversationManager',
    'PromptEngineer',
    'OllamaStreamingClient'
]

__version__ = "1.0.0"