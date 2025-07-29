#----------------------------------------------------------------------------------------------------------------------------
# description: Ollama Python Client
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - ollama Python package
# - requests Python package
# - numpy Python package
# - sounddevice Python package
# - soundfile Python package
# - scipy Python package
# - matplotlib Python package
# - pandas Python package
# - seaborn Python package
# - dataclasses Python package
#-----------------------------------------------------------------------------------------------------------------------------
# functions:
# - OllamaClient: Advanced Ollama client with streaming
# - OllamaModelManager: Model management and operations
# - ConversationManager: Conversation management
# - PromptEngineer: Prompt engineering tools
# - OllamaStreamingClient: Ollama streaming client
#----------------------------------------------------------------------------------------------------------------------------   

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