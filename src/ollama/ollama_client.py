#!/usr/bin/env python3
"""
TalkBridge Ollama - Ollama Client
=================================

Cliente para conexiones externas

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- requests
======================================================================
Functions:
- __init__: Initialize Ollama client.
- ping: Verify if the Ollama server is available.
- get_server_info: Get server information.
- list_models: List available models.
- generate: Generate text using Ollama.
- _generate_stream: Generate streaming response.
- chat: Chat with Ollama model.
- _chat_stream: Chat with streaming response.
- pull_model: Pull a model from Ollama.
- delete_model: Delete a model.
======================================================================
"""

import requests
import json
import time
import threading
from typing import Optional, Dict, List, Callable, Any, Generator
import logging


class OllamaClient:
    """
    Enhanced Ollama client with advanced features.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TalkBridge-Ollama-Client/1.0'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def ping(self) -> bool:
        """
        Verify if the Ollama server is available.
        
        Returns:
            True if server is available, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/", timeout=self.timeout)
            response.raise_for_status()
            self.logger.info(f"Ollama server is available: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error connecting to Ollama server: {e}")
            return False
    
    def get_server_info(self) -> Optional[Dict[str, Any]]:
        """
        Get server information.
        
        Returns:
            Server information dictionary or None if error
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting server info: {e}")
            return None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.
        
        Returns:
            List of model information dictionaries
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error listing models: {e}")
            return []
    
    def generate(self, model: str, prompt: str, 
                system: Optional[str] = None,
                options: Optional[Dict[str, Any]] = None,
                stream: bool = False) -> Optional[str]:
        """
        Generate text using Ollama.
        
        Args:
            model: Model name to use
            prompt: Input prompt
            system: System message (optional)
            options: Generation options (optional)
            stream: Whether to stream the response
            
        Returns:
            Generated text or None if error
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if system:
            payload["system"] = system
        
        if options:
            payload["options"] = options
        
        try:
            if stream:
                return self._generate_stream(url, payload)
            else:
                response = self.session.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error generating response: {e}")
            return None
    
    def _generate_stream(self, url: str, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """
        Generate streaming response.
        
        Args:
            url: API endpoint URL
            payload: Request payload
            
        Yields:
            Generated text chunks
        """
        try:
            response = self.session.post(url, json=payload, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            yield data['response']
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error in streaming generation: {e}")
    
    def chat(self, model: str, messages: List[Dict[str, str]], 
             options: Optional[Dict[str, Any]] = None,
             stream: bool = False) -> Optional[str]:
        """
        Chat with Ollama model.
        
        Args:
            model: Model name to use
            messages: List of message dictionaries with 'role' and 'content'
            options: Generation options (optional)
            stream: Whether to stream the response
            
        Returns:
            Generated response or None if error
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        if options:
            payload["options"] = options
        
        try:
            if stream:
                return self._chat_stream(url, payload)
            else:
                response = self.session.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error in chat: {e}")
            return None
    
    def _chat_stream(self, url: str, payload: Dict[str, Any]) -> Generator[str, None, None]:
        """
        Chat with streaming response.
        
        Args:
            url: API endpoint URL
            payload: Request payload
            
        Yields:
            Generated text chunks
        """
        try:
            response = self.session.post(url, json=payload, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'message' in data and 'content' in data['message']:
                            yield data['message']['content']
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error in streaming chat: {e}")
    
    def pull_model(self, model: str, callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Pull a model from Ollama.
        
        Args:
            model: Model name to pull
            callback: Optional callback for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/api/pull"
        payload = {"name": model}
        
        try:
            response = self.session.post(url, json=payload, stream=True, timeout=None)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if callback and 'status' in data:
                            callback(data['status'])
                        if data.get('done', False):
                            return True
                    except json.JSONDecodeError:
                        continue
            
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error pulling model {model}: {e}")
            return False
    
    def delete_model(self, model: str) -> bool:
        """
        Delete a model.
        
        Args:
            model: Model name to delete
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/api/delete"
        payload = {"name": model}
        
        try:
            response = self.session.delete(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error deleting model {model}: {e}")
            return False
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """
        Get model information.
        
        Args:
            model: Model name
            
        Returns:
            Model information dictionary or None if error
        """
        url = f"{self.base_url}/api/show"
        payload = {"name": model}
        
        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error getting model info for {model}: {e}")
            return None
    
    def create_model(self, name: str, modelfile: str) -> bool:
        """
        Create a custom model.
        
        Args:
            name: Model name
            modelfile: Modelfile content
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/api/create"
        payload = {
            "name": name,
            "modelfile": modelfile
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=None)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating model {name}: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Health check results
        """
        health_status = {
            'server_available': False,
            'models_available': [],
            'server_info': None,
            'errors': []
        }
        
        # Check server availability
        if self.ping():
            health_status['server_available'] = True
            
            # Get server info
            server_info = self.get_server_info()
            if server_info:
                health_status['server_info'] = server_info
            
            # List models
            models = self.list_models()
            health_status['models_available'] = [model['name'] for model in models]
        else:
            health_status['errors'].append("Server not available")
        
        return health_status


if __name__ == "__main__":
    # Test the enhanced client
    client = OllamaClient()
    
    # Health check
    health = client.health_check()
    print("Health Check Results:")
    print(json.dumps(health, indent=2))
    
    # Test generation
    if health['server_available']:
        response = client.generate("llama2", "Hello, how are you?")
        print(f"\nGenerated response: {response}")