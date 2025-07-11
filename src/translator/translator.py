#-----------------------------------------------------------------------------
# description: This module provides a Translator class that interfaces with the Ollama API
# for text translation. It reads configuration from a YAML file and sends translation requests.
#-----------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#
# requirements:
# - requests
# - pyyaml
#------------------------------------------------------------------------------

import requests
import time
import yaml

class Translator:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.base_url = config['ollama']['base_url'].rstrip("/")
        self.model = config['ollama']['model']

    def translate(self, text, source_lang, target_lang):
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