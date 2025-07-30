#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: Ollama Model Manager Module
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - ollama Python package
# - json Python package
# - time Python package
# - threading Python package
# - typing Python package
# - dataclasses Python package  
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - ModelInfo: Model information data class
# - OllamaModelManager: Ollama model manager class
#----------------------------------------------------------------------------------------------------------------------------

import json
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from .ollama_client import OllamaClient


@dataclass
class ModelInfo:
    """Model information data class."""
    name: str
    size: Optional[int] = None
    modified_at: Optional[str] = None
    digest: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class OllamaModelManager:
    """
    Manages Ollama models with advanced features.
    """
    
    def __init__(self, client: Optional[OllamaClient] = None):
        """
        Initialize model manager.
        
        Args:
            client: Ollama client instance
        """
        self.client = client or OllamaClient()
        self.models_cache = {}
        self.last_update = 0
        self.cache_duration = 60  # Cache for 60 seconds
        
    def list_models(self, force_refresh: bool = False) -> List[ModelInfo]:
        """
        List all available models.
        
        Args:
            force_refresh: Force refresh of cached models
            
        Returns:
            List of model information objects
        """
        current_time = time.time()
        
        if not force_refresh and current_time - self.last_update < self.cache_duration:
            return list(self.models_cache.values())
        
        try:
            models_data = self.client.list_models()
            self.models_cache.clear()
            
            for model_data in models_data:
                model_info = ModelInfo(
                    name=model_data.get('name', ''),
                    size=model_data.get('size'),
                    modified_at=model_data.get('modified_at'),
                    digest=model_data.get('digest'),
                    details=model_data
                )
                self.models_cache[model_info.name] = model_info
            
            self.last_update = current_time
            return list(self.models_cache.values())
            
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information or None if not found
        """
        try:
            model_data = self.client.get_model_info(model_name)
            if model_data:
                return ModelInfo(
                    name=model_name,
                    size=model_data.get('size'),
                    modified_at=model_data.get('modified_at'),
                    digest=model_data.get('digest'),
                    details=model_data
                )
        except Exception as e:
            print(f"Error getting model info for {model_name}: {e}")
        
        return None
    
    def install_model(self, model_name: str, 
                     progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Install a model.
        
        Args:
            model_name: Name of the model to install
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Installing model: {model_name}")
            
            def progress_handler(status: str):
                if progress_callback:
                    progress_callback(status)
                else:
                    print(f"Progress: {status}")
            
            success = self.client.pull_model(model_name, progress_handler)
            
            if success:
                print(f"Successfully installed model: {model_name}")
                # Refresh cache
                self.list_models(force_refresh=True)
            else:
                print(f"Failed to install model: {model_name}")
            
            return success
            
        except Exception as e:
            print(f"Error installing model {model_name}: {e}")
            return False
    
    def remove_model(self, model_name: str) -> bool:
        """
        Remove a model.
        
        Args:
            model_name: Name of the model to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Removing model: {model_name}")
            success = self.client.delete_model(model_name)
            
            if success:
                print(f"Successfully removed model: {model_name}")
                # Remove from cache
                if model_name in self.models_cache:
                    del self.models_cache[model_name]
            else:
                print(f"Failed to remove model: {model_name}")
            
            return success
            
        except Exception as e:
            print(f"Error removing model {model_name}: {e}")
            return False
    
    def model_exists(self, model_name: str) -> bool:
        """
        Check if a model exists.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model exists, False otherwise
        """
        models = self.list_models()
        return any(model.name == model_name for model in models)
    
    def get_model_size(self, model_name: str) -> Optional[int]:
        """
        Get model size in bytes.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model size in bytes or None if not found
        """
        model_info = self.get_model_info(model_name)
        return model_info.size if model_info else None
    
    def format_model_size(self, size_bytes: int) -> str:
        """
        Format model size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def get_models_summary(self) -> Dict[str, Any]:
        """
        Get summary of all models.
        
        Returns:
            Summary dictionary with model statistics
        """
        models = self.list_models()
        
        total_models = len(models)
        total_size = sum(model.size or 0 for model in models)
        
        # Group models by size
        size_groups = {
            'small': 0,    # < 1GB
            'medium': 0,   # 1GB - 10GB
            'large': 0,    # > 10GB
        }
        
        for model in models:
            if model.size:
                size_gb = model.size / (1024**3)
                if size_gb < 1:
                    size_groups['small'] += 1
                elif size_gb < 10:
                    size_groups['medium'] += 1
                else:
                    size_groups['large'] += 1
        
        return {
            'total_models': total_models,
            'total_size_bytes': total_size,
            'total_size_formatted': self.format_model_size(total_size),
            'size_groups': size_groups,
            'models': [model.name for model in models]
        }
    
    def create_custom_model(self, name: str, base_model: str, 
                          system_prompt: str, parameters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a custom model with a specific system prompt.
        
        Args:
            name: Name for the custom model
            base_model: Base model to use
            system_prompt: System prompt for the model
            parameters: Additional parameters (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create modelfile content
            modelfile_content = f"FROM {base_model}\n"
            modelfile_content += f"SYSTEM {system_prompt}\n"
            
            if parameters:
                for key, value in parameters.items():
                    modelfile_content += f"PARAMETER {key} {value}\n"
            
            print(f"Creating custom model: {name}")
            success = self.client.create_model(name, modelfile_content)
            
            if success:
                print(f"Successfully created custom model: {name}")
                # Refresh cache
                self.list_models(force_refresh=True)
            else:
                print(f"Failed to create custom model: {name}")
            
            return success
            
        except Exception as e:
            print(f"Error creating custom model {name}: {e}")
            return False
    
    def test_model(self, model_name: str, test_prompt: str = "Hello, how are you?") -> Dict[str, Any]:
        """
        Test a model with a simple prompt.
        
        Args:
            model_name: Name of the model to test
            test_prompt: Test prompt to use
            
        Returns:
            Test results dictionary
        """
        try:
            print(f"Testing model: {model_name}")
            start_time = time.time()
            
            response = self.client.generate(model_name, test_prompt)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response:
                return {
                    'success': True,
                    'response': response,
                    'response_time': response_time,
                    'model': model_name
                }
            else:
                return {
                    'success': False,
                    'error': 'No response generated',
                    'model': model_name
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': model_name
            }
    
    def batch_test_models(self, models: List[str], 
                         test_prompt: str = "Hello, how are you?") -> Dict[str, Dict[str, Any]]:
        """
        Test multiple models.
        
        Args:
            models: List of model names to test
            test_prompt: Test prompt to use
            
        Returns:
            Dictionary of test results for each model
        """
        results = {}
        
        for model_name in models:
            print(f"\nTesting model: {model_name}")
            results[model_name] = self.test_model(model_name, test_prompt)
        
        return results
    
    def cleanup_unused_models(self, keep_models: List[str]) -> List[str]:
        """
        Remove models not in the keep list.
        
        Args:
            keep_models: List of models to keep
            
        Returns:
            List of removed model names
        """
        all_models = self.list_models()
        models_to_remove = []
        
        for model in all_models:
            if model.name not in keep_models:
                models_to_remove.append(model.name)
        
        removed_models = []
        for model_name in models_to_remove:
            if self.remove_model(model_name):
                removed_models.append(model_name)
        
        return removed_models
    
    def export_model_list(self, filename: str) -> bool:
        """
        Export model list to JSON file.
        
        Args:
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            models = self.list_models()
            model_data = []
            
            for model in models:
                model_data.append({
                    'name': model.name,
                    'size': model.size,
                    'modified_at': model.modified_at,
                    'digest': model.digest,
                    'size_formatted': self.format_model_size(model.size) if model.size else None
                })
            
            with open(filename, 'w') as f:
                json.dump(model_data, f, indent=2)
            
            print(f"Exported model list to: {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting model list: {e}")
            return False
    
    def import_model_list(self, filename: str) -> List[str]:
        """
        Import model list from JSON file and install missing models.
        
        Args:
            filename: Input filename
            
        Returns:
            List of installed model names
        """
        try:
            with open(filename, 'r') as f:
                model_data = json.load(f)
            
            installed_models = []
            
            for model_info in model_data:
                model_name = model_info['name']
                if not self.model_exists(model_name):
                    print(f"Installing model from list: {model_name}")
                    if self.install_model(model_name):
                        installed_models.append(model_name)
                else:
                    print(f"Model already exists: {model_name}")
            
            return installed_models
            
        except Exception as e:
            print(f"Error importing model list: {e}")
            return []


if __name__ == "__main__":
    # Test the model manager
    manager = OllamaModelManager()
    
    # List models
    models = manager.list_models()
    print(f"Available models: {[model.name for model in models]}")
    
    # Get summary
    summary = manager.get_models_summary()
    print(f"Models summary: {summary}")
    
    # Test a model if available
    if models:
        test_result = manager.test_model(models[0].name)
        print(f"Test result: {test_result}") 