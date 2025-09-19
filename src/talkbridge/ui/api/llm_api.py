#! /usr/bin/env python3
"""
TalkBridge UI - Llm Api
=======================

LLM API module for TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
- Flask
======================================================================
Functions:
- __init__: Initialize the LLM API.
- generate_response: Generate response using LLM.
- chat_conversation: Generate response in a conversation context.
- _format_conversation: Format conversation messages into a single prompt.
- _add_to_history: Add message to conversation history.
- get_available_models: Get list of available LLM models.
- set_model: Set the current model.
- get_conversation_history: Get conversation history.
- clear_conversation_history: Clear conversation history.
- get_model_info: Get information about the current model.
======================================================================
"""

import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

try:
    from talkbridge.ollama import OllamaClient
except ImportError:
    logging.warning("Ollama module not available")

logger = logging.getLogger(__name__)

class LLMAPI:
    """API interface for LLM functionality."""
    
    def __init__(self):
        """Initialize the LLM API."""
        self.client = None
        self.current_model = "llama2"
        self.conversation_history = []
        self.max_history = 50
        
        try:
            self.client = OllamaClient()
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama client: {e}")
    
    def generate_response(self, prompt: str, model: str = None) -> Optional[str]:
        """
        Generate response using LLM.
        
        Args:
            prompt: Input prompt
            model: Model to use (optional)
            
        Returns:
            Generated response or None if failed
        """
        try:
            if not self.client:
                logger.error("LLM client not available")
                return None
            
            if not prompt.strip():
                logger.warning("Empty prompt provided")
                return None
            
            # Use specified model or default
            model_to_use = model or self.current_model
            
            # Generate response
            response = self.client.generate(prompt, model=model_to_use)
            
            if response:
                # Add to conversation history
                self._add_to_history("user", prompt)
                self._add_to_history("assistant", response)
                
                logger.info(f"Generated response using model {model_to_use}")
                return response
            else:
                logger.error("No response generated")
                return None
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None
    
    def chat_conversation(self, messages: List[Dict[str, str]], model: str = None) -> Optional[str]:
        """
        Generate response in a conversation context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (optional)
            
        Returns:
            Generated response or None if failed
        """
        try:
            if not self.client:
                logger.error("LLM client not available")
                return None
            
            if not messages:
                logger.warning("No messages provided for conversation")
                return None
            
            # Use specified model or default
            model_to_use = model or self.current_model
            
            # Create conversation prompt
            conversation_prompt = self._format_conversation(messages)
            
            # Generate response
            response = self.client.generate(conversation_prompt, model=model_to_use)
            
            if response:
                logger.info(f"Generated conversation response using model {model_to_use}")
                return response
            else:
                logger.error("No conversation response generated")
                return None
                
        except Exception as e:
            logger.error(f"Conversation generation failed: {e}")
            return None
    
    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """
        Format conversation messages into a single prompt.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted conversation string
        """
        formatted = ""
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'user':
                formatted += f"User: {content}\n"
            elif role == 'assistant':
                formatted += f"Assistant: {content}\n"
            elif role == 'system':
                formatted += f"System: {content}\n"
        
        formatted += "Assistant: "
        return formatted
    
    def _add_to_history(self, role: str, content: str) -> None:
        """
        Add message to conversation history.
        
        Args:
            role: Message role (user/assistant)
            content: Message content
        """
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': len(self.conversation_history)
        })
        
        # Keep history within limit
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available LLM models.
        
        Returns:
            List of available model names
        """
        try:
            if self.client:
                return self.client.list_models()
            else:
                return ["llama2", "mistral", "codellama", "llama2:7b", "llama2:13b"]
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return ["llama2", "mistral", "codellama"]
    
    def set_model(self, model: str) -> bool:
        """
        Set the current model.
        
        Args:
            model: Model name to set
            
        Returns:
            True if model set successfully
        """
        try:
            available_models = self.get_available_models()
            if model in available_models:
                self.current_model = model
                logger.info(f"Set current model to: {model}")
                return True
            else:
                logger.warning(f"Model {model} not available")
                return False
        except Exception as e:
            logger.error(f"Failed to set model: {e}")
            return False
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()
    
    def clear_conversation_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Cleared conversation history")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "current_model": self.current_model,
            "available_models": self.get_available_models(),
            "conversation_length": len(self.conversation_history),
            "max_history": self.max_history
        }
    
    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate prompt for LLM generation.
        
        Args:
            prompt: Prompt to validate
            
        Returns:
            True if prompt is valid
        """
        if not prompt or not prompt.strip():
            return False
        
        # Check prompt length (reasonable limit)
        if len(prompt) > 4000:
            return False
        
        # Check for valid characters
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;:'\"()-")
        prompt_chars = set(prompt)
        
        if not prompt_chars.issubset(valid_chars):
            # Allow some special characters
            special_chars = set("áéíóúñüçàèìòùâêîôûäëïöüß")
            prompt_chars = prompt_chars - special_chars
            if not prompt_chars.issubset(valid_chars):
                return False
        
        return True
    
    def get_response_quality_score(self, response: str) -> float:
        """
        Get a quality score for the generated response.
        
        Args:
            response: Generated response
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            if not response:
                return 0.0
            
            score = 0.0
            
            # Length score (prefer responses of reasonable length)
            length = len(response)
            if 10 <= length <= 500:
                score += 0.3
            elif length > 500:
                score += 0.2
            else:
                score += 0.1
            
            # Completeness score (check for sentence structure)
            if response.endswith(('.', '!', '?')):
                score += 0.2
            
            # Content score (check for meaningful words)
            words = response.split()
            if len(words) >= 3:
                score += 0.3
            
            # Coherence score (check for repeated words)
            unique_words = set(words)
            if len(unique_words) / len(words) > 0.7:
                score += 0.2
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Failed to calculate response quality: {e}")
            return 0.5
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Get current LLM API status.
        
        Returns:
            Dictionary containing current status
        """
        return {
            "client_available": self.client is not None,
            "current_model": self.current_model,
            "conversation_history_length": len(self.conversation_history),
            "model_info": self.get_model_info()
        } 