#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: Ollama Streaming Client Module
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
# - StreamingEvent: Streaming event data class
# - StreamingCallback: Base class for streaming callbacks
# - OllamaStreamingClient: Ollama streaming client class
#----------------------------------------------------------------------------------------------------------------------------

import json
import time
import threading
import queue
from typing import Dict, List, Optional, Callable, Any, Generator
from dataclasses import dataclass
from .ollama_client import OllamaClient


@dataclass
class StreamingEvent:
    """Streaming event data class."""
    event_type: str  # 'start', 'chunk', 'end', 'error'
    data: Any
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


class StreamingCallback:
    """Base class for streaming callbacks."""
    
    def on_start(self, prompt: str, model: str):
        """Called when streaming starts."""
        pass
    
    def on_chunk(self, chunk: str):
        """Called for each response chunk."""
        pass
    
    def on_end(self, full_response: str):
        """Called when streaming ends."""
        pass
    
    def on_error(self, error: str):
        """Called when an error occurs."""
        pass


class OllamaStreamingClient:
    """
    Real-time streaming client for Ollama interactions.
    """
    
    def __init__(self, client: Optional[OllamaClient] = None):
        """
        Initialize streaming client.
        
        Args:
            client: Ollama client instance
        """
        self.client = client or OllamaClient()
        self.callbacks: List[StreamingCallback] = []
        self.event_queue = queue.Queue()
        self.is_streaming = False
        self.current_stream_thread = None
        
    def add_callback(self, callback: StreamingCallback):
        """
        Add a streaming callback.
        
        Args:
            callback: Callback instance
        """
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: StreamingCallback):
        """
        Remove a streaming callback.
        
        Args:
            callback: Callback instance
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, event_type: str, data: Any):
        """
        Notify all callbacks of an event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        event = StreamingEvent(
            event_type=event_type,
            data=data,
            timestamp=time.time()
        )
        
        # Add to event queue
        self.event_queue.put(event)
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                if event_type == 'start':
                    callback.on_start(data['prompt'], data['model'])
                elif event_type == 'chunk':
                    callback.on_chunk(data)
                elif event_type == 'end':
                    callback.on_end(data)
                elif event_type == 'error':
                    callback.on_error(data)
            except Exception as e:
                print(f"Error in callback {callback.__class__.__name__}: {e}")
    
    def stream_generate(self, model: str, prompt: str,
                       system: Optional[str] = None,
                       options: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """
        Stream generate text from Ollama.
        
        Args:
            model: Model name
            prompt: Input prompt
            system: System message (optional)
            options: Generation options (optional)
            
        Yields:
            Response chunks
        """
        self.is_streaming = True
        full_response = ""
        
        try:
            # Notify start
            self._notify_callbacks('start', {
                'prompt': prompt,
                'model': model,
                'system': system,
                'options': options
            })
            
            # Stream response
            for chunk in self.client.generate(model, prompt, system, options, stream=True):
                full_response += chunk
                self._notify_callbacks('chunk', chunk)
                yield chunk
            
            # Notify end
            self._notify_callbacks('end', full_response)
            
        except Exception as e:
            error_msg = f"Error in streaming generation: {e}"
            self._notify_callbacks('error', error_msg)
            raise
        
        finally:
            self.is_streaming = False
    
    def stream_chat(self, model: str, messages: List[Dict[str, str]],
                   options: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """
        Stream chat with Ollama model.
        
        Args:
            model: Model name
            messages: List of message dictionaries
            options: Generation options (optional)
            
        Yields:
            Response chunks
        """
        self.is_streaming = True
        full_response = ""
        
        try:
            # Notify start
            self._notify_callbacks('start', {
                'messages': messages,
                'model': model,
                'options': options
            })
            
            # Stream response
            for chunk in self.client.chat(model, messages, options, stream=True):
                full_response += chunk
                self._notify_callbacks('chunk', chunk)
                yield chunk
            
            # Notify end
            self._notify_callbacks('end', full_response)
            
        except Exception as e:
            error_msg = f"Error in streaming chat: {e}"
            self._notify_callbacks('error', error_msg)
            raise
        
        finally:
            self.is_streaming = False
    
    def stream_with_callback(self, model: str, prompt: str,
                           callback: StreamingCallback,
                           system: Optional[str] = None,
                           options: Optional[Dict[str, Any]] = None) -> str:
        """
        Stream with a specific callback.
        
        Args:
            model: Model name
            prompt: Input prompt
            callback: Callback instance
            system: System message (optional)
            options: Generation options (optional)
            
        Returns:
            Full response
        """
        # Temporarily add callback
        self.add_callback(callback)
        
        try:
            full_response = ""
            for chunk in self.stream_generate(model, prompt, system, options):
                full_response += chunk
            
            return full_response
            
        finally:
            # Remove callback
            self.remove_callback(callback)
    
    def start_background_stream(self, model: str, prompt: str,
                              system: Optional[str] = None,
                              options: Optional[Dict[str, Any]] = None):
        """
        Start streaming in background thread.
        
        Args:
            model: Model name
            prompt: Input prompt
            system: System message (optional)
            options: Generation options (optional)
        """
        if self.current_stream_thread and self.current_stream_thread.is_alive():
            print("Stream already in progress")
            return
        
        def stream_worker():
            try:
                for chunk in self.stream_generate(model, prompt, system, options):
                    pass  # Chunks are handled by callbacks
            except Exception as e:
                print(f"Background stream error: {e}")
        
        self.current_stream_thread = threading.Thread(target=stream_worker)
        self.current_stream_thread.start()
    
    def stop_background_stream(self):
        """Stop background streaming."""
        self.is_streaming = False
        if self.current_stream_thread:
            self.current_stream_thread.join(timeout=1.0)
            self.current_stream_thread = None
    
    def get_event_queue(self) -> queue.Queue:
        """
        Get the event queue for processing events.
        
        Returns:
            Event queue
        """
        return self.event_queue
    
    def process_events(self, timeout: Optional[float] = None):
        """
        Process events from the queue.
        
        Args:
            timeout: Timeout for queue operations
        """
        while True:
            try:
                event = self.event_queue.get(timeout=timeout)
                print(f"Event: {event.event_type} - {event.data}")
                self.event_queue.task_done()
            except queue.Empty:
                break
    
    def clear_event_queue(self):
        """Clear the event queue."""
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
                self.event_queue.task_done()
            except queue.Empty:
                break


class ConsoleStreamingCallback(StreamingCallback):
    """Console-based streaming callback."""
    
    def __init__(self, show_timestamps: bool = False):
        """
        Initialize console callback.
        
        Args:
            show_timestamps: Whether to show timestamps
        """
        self.show_timestamps = show_timestamps
        self.start_time = None
    
    def on_start(self, prompt: str, model: str):
        """Called when streaming starts."""
        self.start_time = time.time()
        timestamp = f"[{time.strftime('%H:%M:%S')}] " if self.show_timestamps else ""
        print(f"{timestamp}🚀 Starting stream with model: {model}")
        print(f"{timestamp}📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print(f"{timestamp}💬 Response:")
    
    def on_chunk(self, chunk: str):
        """Called for each response chunk."""
        print(chunk, end='', flush=True)
    
    def on_end(self, full_response: str):
        """Called when streaming ends."""
        if self.start_time:
            duration = time.time() - self.start_time
            timestamp = f"[{time.strftime('%H:%M:%S')}] " if self.show_timestamps else ""
            print(f"\n{timestamp}✅ Stream completed in {duration:.2f}s")
            print(f"{timestamp}📊 Response length: {len(full_response)} characters")
    
    def on_error(self, error: str):
        """Called when an error occurs."""
        timestamp = f"[{time.strftime('%H:%M:%S')}] " if self.show_timestamps else ""
        print(f"\n{timestamp}❌ Error: {error}")


class FileStreamingCallback(StreamingCallback):
    """File-based streaming callback."""
    
    def __init__(self, filename: str, append: bool = True):
        """
        Initialize file callback.
        
        Args:
            filename: Output filename
            append: Whether to append to existing file
        """
        self.filename = filename
        self.append = append
        self.current_response = ""
        self.start_time = None
    
    def on_start(self, prompt: str, model: str):
        """Called when streaming starts."""
        self.start_time = time.time()
        self.current_response = ""
        
        mode = 'a' if self.append else 'w'
        with open(self.filename, mode) as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Stream started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Prompt: {prompt}\n")
            f.write(f"{'='*50}\n")
            f.write("Response:\n")
    
    def on_chunk(self, chunk: str):
        """Called for each response chunk."""
        self.current_response += chunk
        with open(self.filename, 'a') as f:
            f.write(chunk)
            f.flush()
    
    def on_end(self, full_response: str):
        """Called when streaming ends."""
        if self.start_time:
            duration = time.time() - self.start_time
            with open(self.filename, 'a') as f:
                f.write(f"\n\n{'='*50}\n")
                f.write(f"Stream completed in {duration:.2f}s\n")
                f.write(f"Response length: {len(full_response)} characters\n")
                f.write(f"{'='*50}\n")
    
    def on_error(self, error: str):
        """Called when an error occurs."""
        with open(self.filename, 'a') as f:
            f.write(f"\nERROR: {error}\n")


class PerformanceStreamingCallback(StreamingCallback):
    """Performance monitoring streaming callback."""
    
    def __init__(self):
        """Initialize performance callback."""
        self.start_time = None
        self.chunks_received = 0
        self.total_chars = 0
        self.chunk_times = []
    
    def on_start(self, prompt: str, model: str):
        """Called when streaming starts."""
        self.start_time = time.time()
        self.chunks_received = 0
        self.total_chars = 0
        self.chunk_times = []
        print(f"Performance monitoring started for model: {model}")
    
    def on_chunk(self, chunk: str):
        """Called for each response chunk."""
        self.chunks_received += 1
        self.total_chars += len(chunk)
        self.chunk_times.append(time.time())
    
    def on_end(self, full_response: str):
        """Called when streaming ends."""
        if self.start_time:
            duration = time.time() - self.start_time
            avg_chunk_time = sum(self.chunk_times) / len(self.chunk_times) if self.chunk_times else 0
            
            print(f"\nPerformance Summary:")
            print(f"  Total time: {duration:.2f}s")
            print(f"  Chunks received: {self.chunks_received}")
            print(f"  Total characters: {self.total_chars}")
            print(f"  Average chunk time: {avg_chunk_time:.3f}s")
            print(f"  Characters per second: {self.total_chars / duration:.1f}")
    
    def on_error(self, error: str):
        """Called when an error occurs."""
        print(f"Performance monitoring error: {error}")


if __name__ == "__main__":
    # Test the streaming client
    client = OllamaStreamingClient()
    
    # Add console callback
    console_callback = ConsoleStreamingCallback(show_timestamps=True)
    client.add_callback(console_callback)
    
    # Test streaming
    try:
        print("Testing streaming generation...")
        for chunk in client.stream_generate("llama2", "Hello, how are you?"):
            pass  # Chunks are handled by callbacks
        
        print("\nTesting streaming chat...")
        messages = [{"role": "user", "content": "What is the capital of France?"}]
        for chunk in client.stream_chat("llama2", messages):
            pass  # Chunks are handled by callbacks
            
    except Exception as e:
        print(f"Streaming test error: {e}") 