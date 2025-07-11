#----------------------------------------------------------------------------------
# description: Ollama client for interacting with the Ollama API.
#----------------------------------------------------------------------------------
#
# author: ingekastel
# date: 2025-06-02
# version: 1.0
#
# requirements:
# - requests library
# - Python 3.6 or higher
#----------------------------------------------------------------------------------

import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    def ping(self):
        """Verify if the Ollama server is available."""
        try:
            response = requests.get(f"{self.base_url}/")
            response.raise_for_status()
            print(f"Ollama responds correctly: {response.status_code}")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error connecting with Ollama: {e}")
            return None

    def generate(self, model, prompt):
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"Error generating response: {e}")
            return None