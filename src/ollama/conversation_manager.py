"""
TalkBridge Ollama - Conversation Manager
========================================

Gestor/Manager del módulo

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- requests
======================================================================
Functions:
- __init__: Initialize conversation manager.
- create_conversation: Create a new conversation.
- get_conversation: Get a conversation by ID.
- list_conversations: List all conversations.
- add_message: Add a message to a conversation.
- send_message: Send a message and get response from the model.
- get_conversation_messages: Get all messages in a conversation.
- get_conversation_context: Get conversation context as a formatted string.
- delete_conversation: Delete a conversation.
- clear_conversation: Clear all messages from a conversation.
======================================================================
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Generator
from dataclasses import dataclass, asdict
from datetime import datetime
from .ollama_client import OllamaClient

@dataclass
class Message:
    """Message data class."""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Conversation:
    """Conversation data class."""
    id: str
    title: str
    model: str
    messages: List[Message]
    created_at: float
    updated_at: float
    metadata: Optional[Dict[str, Any]] = None

class ConversationManager:
    """
    Manages conversations with Ollama models.
    """
    
    def __init__(self, client: Optional[OllamaClient] = None):
        """
        Initialize conversation manager.
        
        Args:
            client: Ollama client instance
        """
        self.client = client or OllamaClient()
        self.conversations: Dict[str, Conversation] = {}
        self.current_conversation_id: Optional[str] = None
        self.max_context_length = 4096  # Maximum context length
        self.max_messages = 100  # Maximum messages per conversation
        
    def create_conversation(self, title: str, model: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new conversation.
        
        Args:
            title: Conversation title
            model: Model to use for this conversation
            metadata: Optional metadata
            
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        current_time = time.time()
        
        conversation = Conversation(
            id=conversation_id,
            title=title,
            model=model,
            messages=[],
            created_at=current_time,
            updated_at=current_time,
            metadata=metadata or {}
        )
        
        self.conversations[conversation_id] = conversation
        self.current_conversation_id = conversation_id
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation object or None if not found
        """
        return self.conversations.get(conversation_id)
    
    def list_conversations(self) -> List[Conversation]:
        """
        List all conversations.
        
        Returns:
            List of conversation objects
        """
        return list(self.conversations.values())
    
    def add_message(self, conversation_id: str, role: str, content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Message ID or None if error
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        message_id = str(uuid.uuid4())
        current_time = time.time()
        
        message = Message(
            id=message_id,
            role=role,
            content=content,
            timestamp=current_time,
            metadata=metadata or {}
        )
        
        conversation.messages.append(message)
        conversation.updated_at = current_time
        
        # Trim messages if exceeding limit
        if len(conversation.messages) > self.max_messages:
            conversation.messages = conversation.messages[-self.max_messages:]
        
        return message_id
    
    def send_message(self, conversation_id: str, content: str,
                    system_prompt: Optional[str] = None,
                    options: Optional[Dict[str, Any]] = None,
                    stream: bool = False) -> Optional[str]:
        """
        Send a message and get response from the model.
        
        Args:
            conversation_id: Conversation ID
            content: User message content
            system_prompt: Optional system prompt
            options: Generation options
            stream: Whether to stream the response
            
        Returns:
            Assistant message ID or None if error
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            print(f"Error: Conversation {conversation_id} not found")
            return None
        
        # Validate content
        if not content or not content.strip():
            print("Error: Message content cannot be empty")
            return None
        
        # Add user message
        user_message_id = self.add_message(conversation_id, 'user', content)
        if not user_message_id:
            print("Error: Failed to add user message")
            return None
        
        # Prepare messages for the model
        messages = []
        for msg in conversation.messages:
            messages.append({
                'role': msg.role,
                'content': msg.content
            })
        
        # Get response from model
        try:
            if stream:
                response_content = ""
                stream_response = self.client.chat(conversation.model, messages, options, stream=True)
                if stream_response:
                    for chunk in stream_response:
                        if chunk:  # Check if chunk is not None
                            response_content += chunk
                            # You could implement real-time streaming here
            else:
                response_content = self.client.chat(conversation.model, messages, options, stream=False)
            
            if response_content:
                # Add assistant message
                assistant_message_id = self.add_message(conversation_id, 'assistant', response_content)
                return assistant_message_id
            else:
                print(f"Warning: Empty response from model {conversation.model}")
                return None
                
        except Exception as e:
            print(f"Error getting response from model {conversation.model}: {e}")
            # Could add more specific error handling here
            return None
    
    def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """
        Get all messages in a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages
        """
        conversation = self.get_conversation(conversation_id)
        return conversation.messages if conversation else []
    
    def get_conversation_context(self, conversation_id: str, 
                               max_length: Optional[int] = None) -> str:
        """
        Get conversation context as a formatted string.
        
        Args:
            conversation_id: Conversation ID
            max_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        messages = self.get_conversation_messages(conversation_id)
        if not messages:
            return ""
        
        context_parts = []
        for message in messages:
            role_label = "User" if message.role == "user" else "Assistant"
            context_parts.append(f"{role_label}: {message.content}")
        
        context = "\n\n".join(context_parts)
        
        if max_length and len(context) > max_length:
            # Truncate from the beginning to keep recent messages
            context = context[-max_length:]
        
        return context
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful, False otherwise
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            
            # Update current conversation if needed
            if self.current_conversation_id == conversation_id:
                conversations = self.list_conversations()
                self.current_conversation_id = conversations[-1].id if conversations else None
            
            return True
        return False
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clear all messages from a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful, False otherwise
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.messages.clear()
            conversation.updated_at = time.time()
            return True
        return False
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """
        Update conversation title.
        
        Args:
            conversation_id: Conversation ID
            title: New title
            
        Returns:
            True if successful, False otherwise
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = time.time()
            return True
        return False
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation summary.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Summary dictionary
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        user_messages = [msg for msg in conversation.messages if msg.role == 'user']
        assistant_messages = [msg for msg in conversation.messages if msg.role == 'assistant']
        
        return {
            'id': conversation.id,
            'title': conversation.title,
            'model': conversation.model,
            'total_messages': len(conversation.messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'created_at': conversation.created_at,
            'updated_at': conversation.updated_at,
            'duration': conversation.updated_at - conversation.created_at,
            'metadata': conversation.metadata
        }
    
    def export_conversation(self, conversation_id: str, filename: str) -> bool:
        """
        Export conversation to JSON file.
        
        Args:
            conversation_id: Conversation ID
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        try:
            # Convert to dictionary
            conversation_dict = asdict(conversation)
            
            # Convert timestamps to readable format
            conversation_dict['created_at'] = datetime.fromtimestamp(conversation.created_at).isoformat()
            conversation_dict['updated_at'] = datetime.fromtimestamp(conversation.updated_at).isoformat()
            
            for message in conversation_dict['messages']:
                message['timestamp'] = datetime.fromtimestamp(message['timestamp']).isoformat()
            
            with open(filename, 'w') as f:
                json.dump(conversation_dict, f, indent=2)
            
            print(f"Exported conversation to: {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting conversation: {e}")
            return False
    
    def import_conversation(self, filename: str) -> Optional[str]:
        """
        Import conversation from JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            Conversation ID or None if error
        """
        try:
            with open(filename, 'r') as f:
                conversation_dict = json.load(f)
            
            # Convert timestamps back to float
            conversation_dict['created_at'] = datetime.fromisoformat(conversation_dict['created_at']).timestamp()
            conversation_dict['updated_at'] = datetime.fromisoformat(conversation_dict['updated_at']).timestamp()
            
            for message in conversation_dict['messages']:
                message['timestamp'] = datetime.fromisoformat(message['timestamp']).timestamp()
            
            # Create conversation object
            conversation = Conversation(
                id=conversation_dict['id'],
                title=conversation_dict['title'],
                model=conversation_dict['model'],
                messages=[Message(**msg) for msg in conversation_dict['messages']],
                created_at=conversation_dict['created_at'],
                updated_at=conversation_dict['updated_at'],
                metadata=conversation_dict.get('metadata', {})
            )
            
            self.conversations[conversation.id] = conversation
            print(f"Imported conversation: {conversation.title}")
            
            return conversation.id
            
        except Exception as e:
            print(f"Error importing conversation: {e}")
            return None
    
    def search_conversations(self, query: str) -> List[Conversation]:
        """
        Search conversations by title and content.
        
        Args:
            query: Search query
            
        Returns:
            List of matching conversations
        """
        query_lower = query.lower()
        matching_conversations = []
        
        for conversation in self.conversations.values():
            # Search in title
            if query_lower in conversation.title.lower():
                matching_conversations.append(conversation)
                continue
            
            # Search in messages
            for message in conversation.messages:
                if query_lower in message.content.lower():
                    matching_conversations.append(conversation)
                    break
        
        return matching_conversations
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all conversations.
        
        Returns:
            Statistics dictionary
        """
        total_conversations = len(self.conversations)
        total_messages = sum(len(conv.messages) for conv in self.conversations.values())
        
        # Group by model
        model_counts = {}
        for conversation in self.conversations.values():
            model = conversation.model
            model_counts[model] = model_counts.get(model, 0) + 1
        
        # Get recent conversations
        recent_conversations = sorted(
            self.conversations.values(),
            key=lambda x: x.updated_at,
            reverse=True
        )[:5]
        
        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'model_distribution': model_counts,
            'recent_conversations': [conv.title for conv in recent_conversations],
            'average_messages_per_conversation': total_messages / total_conversations if total_conversations > 0 else 0
        }

if __name__ == "__main__":
    # Test the conversation manager
    manager = ConversationManager()
    
    # Create a conversation
    conv_id = manager.create_conversation("Test Conversation", "llama2")
    print(f"Created conversation: {conv_id}")
    
    # Send a message
    response_id = manager.send_message(conv_id, "Hello, how are you?")
    print(f"Got response: {response_id}")
    
    # Get conversation summary
    summary = manager.get_conversation_summary(conv_id)
    print(f"Conversation summary: {summary}")
    
    # Get stats
    stats = manager.get_conversation_stats()
    print(f"Stats: {stats}") 