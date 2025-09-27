#!/usr/bin/env python3
"""
TalkBridge Translation - Translator
===================================

Translator module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- None
======================================================================
Functions:
- __init__: Function __init__
- translate: Function translate
======================================================================
"""

import requests
import time
from typing import Optional, Tuple

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    yaml = None  # type: ignore
    YAML_AVAILABLE = False


class Translator:
    def __init__(self, config_path: str = "config/config.yaml") -> None:
        # Set default values
        self.base_url = "http://localhost:11434"
        self.model = "llama2"
        
        if not YAML_AVAILABLE or yaml is None:
            print("Warning: YAML module not available, using default Ollama settings")
            return
            
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if 'ollama' not in config:
                raise KeyError("Missing 'ollama' configuration section")
                
            self.base_url = config['ollama']['base_url'].rstrip("/")
            self.model = config['ollama']['model']
        except (FileNotFoundError, KeyError) as e:
            # Fallback to default values if config is missing or invalid
            print(f"Warning: Config issue ({e}), using default Ollama settings")
        except Exception as e:
            # Handle YAML errors and other exceptions
            print(f"Warning: Config parsing error ({e}), using default Ollama settings")

    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[Optional[str], Optional[float]]:
        prompt = (
            f"Translate the following text from {source_lang} to {target_lang}:\n"
            f"Text: \"{text}\""
        )

        payload = {
            "model": self.model,
            "prompt": prompt
        }

        try:
            start_time = time.time()
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            result = response.json()
            latency = time.time() - start_time

            translation = result.get("response", "").strip()
            print(f"Translation received in {latency:.2f} seconds")
            return translation, latency

        except requests.exceptions.RequestException as e:
            print(f"Error in Deepseek inference: {e}")
            return None, None