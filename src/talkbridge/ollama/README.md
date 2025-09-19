# Ollama Module for TalkBridge

This module provides comprehensive Ollama integration capabilities for the TalkBridge application, including advanced client features, model management, conversation handling, prompt engineering, and real-time streaming.

## Features

### 🤖 Advanced Ollama Client
- **Enhanced API integration** with comprehensive error handling
- **Streaming support** for real-time text generation
- **Health monitoring** and server status checking
- **Model management** (install, remove, test models)
- **Custom model creation** with Modelfile support

### 📊 Model Management
- **Model installation and removal** with progress tracking
- **Model information and statistics** with size formatting
- **Model testing and performance analysis**
- **Batch operations** for multiple models
- **Export/import** model lists and configurations

### 💬 Conversation Management
- **Chat conversation handling** with message history
- **Conversation state management** and persistence
- **Context management** and optimization
- **Search and filtering** capabilities
- **Export/import** conversations in JSON format

### 🎯 Prompt Engineering
- **Prompt templates** with variable substitution
- **Template management** and categorization
- **Prompt optimization** and testing
- **Performance analysis** and metrics
- **Batch testing** of multiple templates

### ⚡ Real-time Streaming
- **Streaming text generation** with callbacks
- **Event handling** and queue management
- **Multiple callback types** (console, file, performance)
- **Background streaming** with thread management
- **Performance monitoring** and logging

## Installation

Make sure you have Ollama installed and running:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Pull a model (optional)
ollama pull llama2
```

## Quick Start

### Basic Ollama Client

```python
from ollama import OllamaClient

# Create client
client = OllamaClient()

# Check server health
health = client.health_check()
print(f"Server available: {health['server_available']}")

# List available models
models = client.list_models()
print(f"Available models: {[model['name'] for model in models]}")

# Generate text
response = client.generate("llama2", "Hello, how are you?")
print(f"Response: {response}")

# Stream generation
for chunk in client.generate("llama2", "Tell me a story", stream=True):
    print(chunk, end='', flush=True)
```

### Model Management

```python
from ollama import OllamaModelManager

# Create model manager
manager = OllamaModelManager()

# List models
models = manager.list_models()
for model in models:
    print(f"Model: {model.name}, Size: {manager.format_model_size(model.size or 0)}")

# Install a model
def progress_callback(status):
    print(f"Progress: {status}")

success = manager.install_model("llama2", progress_callback)

# Test a model
test_result = manager.test_model("llama2", "What is 2+2?")
print(f"Test result: {test_result}")

# Get models summary
summary = manager.get_models_summary()
print(f"Total models: {summary['total_models']}")
print(f"Total size: {summary['total_size_formatted']}")
```

### Conversation Management

```python
from ollama import ConversationManager

# Create conversation manager
manager = ConversationManager()

# Create a conversation
conv_id = manager.create_conversation("My Chat", "llama2")

# Send a message and get response
response_id = manager.send_message(conv_id, "Hello, how are you?")

# Get conversation messages
messages = manager.get_conversation_messages(conv_id)
for message in messages:
    print(f"{message.role}: {message.content}")

# Get conversation summary
summary = manager.get_conversation_summary(conv_id)
print(f"Total messages: {summary['total_messages']}")

# Export conversation
manager.export_conversation(conv_id, "my_conversation.json")
```

### Prompt Engineering

```python
from ollama import PromptEngineer

# Create prompt engineer
engineer = PromptEngineer()

# List available templates
templates = engineer.list_templates()
for template in templates:
    print(f"Template: {template.name} - {template.description}")

# Use a template
variables = {"task": "Write a Python function to calculate fibonacci numbers"}
prompt = engineer.render_template("code_assistant", variables)

# Test the prompt
result = engineer.test_prompt(prompt, "llama2")
print(f"Response: {result.response}")

# Optimize a prompt
optimized = engineer.optimize_prompt(
    "Explain machine learning",
    "Machine learning is a subset of AI that enables computers to learn from data.",
    iterations=5
)
print(f"Optimized prompt: {optimized}")
```

### Streaming Client

```python
from ollama import OllamaStreamingClient
from ollama.streaming_client import ConsoleStreamingCallback, FileStreamingCallback

# Create streaming client
client = OllamaStreamingClient()

# Add console callback
console_callback = ConsoleStreamingCallback(show_timestamps=True)
client.add_callback(console_callback)

# Add file callback
file_callback = FileStreamingCallback("stream.log", append=True)
client.add_callback(file_callback)

# Stream generation
for chunk in client.stream_generate("llama2", "Write a poem about technology"):
    pass  # Chunks are handled by callbacks

# Stream chat
messages = [{"role": "user", "content": "What is the capital of France?"}]
for chunk in client.stream_chat("llama2", messages):
    pass  # Chunks are handled by callbacks
```

## Integration with TalkBridge

### Basic Integration

```python
from ollama import OllamaClient, ConversationManager
from audio import AudioGenerator

def setup_ollama_integration():
    # Initialize components
    client = OllamaClient()
    conv_manager = ConversationManager(client)
    audio_gen = AudioGenerator()
    
    # Create conversation
    conv_id = conv_manager.create_conversation("TalkBridge Chat", "llama2")
    
    return client, conv_manager, conv_id

def process_user_input(user_input: str, conv_manager: ConversationManager, conv_id: str):
    # Send user input and get response
    response_id = conv_manager.send_message(conv_id, user_input)
    
    # Get the response
    messages = conv_manager.get_conversation_messages(conv_id)
    if messages:
        latest_response = messages[-1].content
        
        # Generate audio for response
        audio = audio_gen.generate_sine_wave(440, 0.5)  # Notification sound
        audio_gen.play_audio(audio)
        
        return latest_response
    
    return None
```

### Advanced Integration with Streaming

```python
from ollama import OllamaStreamingClient
from ollama.streaming_client import ConsoleStreamingCallback
from audio import AudioGenerator

def setup_streaming_integration():
    # Initialize components
    streaming_client = OllamaStreamingClient()
    audio_gen = AudioGenerator()
    
    # Add console callback for real-time display
    console_callback = ConsoleStreamingCallback(show_timestamps=True)
    streaming_client.add_callback(console_callback)
    
    return streaming_client, audio_gen

def stream_response(prompt: str, streaming_client: OllamaStreamingClient, audio_gen: AudioGenerator):
    # Generate notification sound
    notification = audio_gen.generate_sine_wave(800, 0.3)
    audio_gen.play_audio(notification)
    
    # Stream response
    full_response = ""
    for chunk in streaming_client.stream_generate("llama2", prompt):
        full_response += chunk
    
    # Generate completion sound
    completion = audio_gen.generate_sine_wave(600, 0.2)
    audio_gen.play_audio(completion)
    
    return full_response
```

## Configuration

### Client Settings

```python
# Custom client configuration
client = OllamaClient(
    base_url="http://localhost:11434",  # Ollama server URL
    timeout=30  # Request timeout in seconds
)
```

### Model Manager Settings

```python
# Model manager with custom client
manager = OllamaModelManager(client)

# Custom cache duration
manager.cache_duration = 120  # Cache for 2 minutes
```

### Conversation Manager Settings

```python
# Conversation manager with custom settings
manager = ConversationManager(client)
manager.max_context_length = 8192  # Maximum context length
manager.max_messages = 200  # Maximum messages per conversation
```

### Prompt Engineer Settings

```python
# Prompt engineer with custom model
engineer = PromptEngineer(client)
engineer.default_model = "llama2"  # Default model for testing
```

## Demo

Run the comprehensive demo to see all Ollama capabilities in action:

```bash
cd src
python ollama_demo.py
```

This will showcase:
- Basic Ollama client functionality
- Model management and testing
- Conversation handling and persistence
- Prompt engineering and optimization
- Real-time streaming with callbacks
- Integration between components
- Advanced features and performance monitoring

## API Reference

### OllamaClient

- `ping()` - Check server availability
- `health_check()` - Comprehensive health check
- `list_models()` - List available models
- `generate(model, prompt, system, options, stream)` - Generate text
- `chat(model, messages, options, stream)` - Chat with model
- `pull_model(model, callback)` - Install model
- `delete_model(model)` - Remove model
- `get_model_info(model)` - Get model information
- `create_model(name, modelfile)` - Create custom model

### OllamaModelManager

- `list_models(force_refresh)` - List models with caching
- `get_model_info(model_name)` - Get detailed model info
- `install_model(model_name, progress_callback)` - Install model
- `remove_model(model_name)` - Remove model
- `model_exists(model_name)` - Check if model exists
- `test_model(model_name, test_prompt)` - Test model
- `batch_test_models(models, test_prompt)` - Test multiple models
- `get_models_summary()` - Get models statistics
- `export_model_list(filename)` - Export model list
- `import_model_list(filename)` - Import model list

### ConversationManager

- `create_conversation(title, model, metadata)` - Create conversation
- `get_conversation(conversation_id)` - Get conversation
- `list_conversations()` - List all conversations
- `add_message(conversation_id, role, content, metadata)` - Add message
- `send_message(conversation_id, content, system_prompt, options, stream)` - Send message
- `get_conversation_messages(conversation_id)` - Get messages
- `get_conversation_context(conversation_id, max_length)` - Get context
- `delete_conversation(conversation_id)` - Delete conversation
- `clear_conversation(conversation_id)` - Clear messages
- `export_conversation(conversation_id, filename)` - Export conversation
- `import_conversation(filename)` - Import conversation
- `search_conversations(query)` - Search conversations
- `get_conversation_stats()` - Get statistics

### PromptEngineer

- `add_template(template)` - Add prompt template
- `get_template(name)` - Get template
- `list_templates(category)` - List templates
- `render_template(template_name, variables)` - Render template
- `test_prompt(prompt, model, expected_response)` - Test prompt
- `optimize_prompt(base_prompt, target_response, model, iterations)` - Optimize prompt
- `batch_test_templates(template_names, test_cases, model)` - Batch test
- `analyze_prompt_performance(template_name)` - Analyze performance
- `export_templates(filename)` - Export templates
- `import_templates(filename)` - Import templates
- `search_templates(query)` - Search templates
- `get_template_stats()` - Get statistics

### OllamaStreamingClient

- `add_callback(callback)` - Add streaming callback
- `remove_callback(callback)` - Remove callback
- `stream_generate(model, prompt, system, options)` - Stream generation
- `stream_chat(model, messages, options)` - Stream chat
- `stream_with_callback(model, prompt, callback, system, options)` - Stream with callback
- `start_background_stream(model, prompt, system, options)` - Background streaming
- `stop_background_stream()` - Stop background stream
- `get_event_queue()` - Get event queue
- `process_events(timeout)` - Process events
- `clear_event_queue()` - Clear event queue

## Troubleshooting

### Common Issues

1. **Server not available**: Ensure Ollama is running (`ollama serve`)
2. **Model not found**: Install the model first (`ollama pull model_name`)
3. **Connection errors**: Check Ollama server URL and network connectivity
4. **Memory issues**: Reduce model size or use smaller models
5. **Performance issues**: Adjust timeout settings and use streaming for long responses

### Dependencies

Make sure all required packages are installed:

```bash
pip install -r requirements.txt
```

### Ollama Setup

1. **Install Ollama**: Follow instructions at https://ollama.ai/
2. **Start server**: `ollama serve`
3. **Pull models**: `ollama pull llama2` (or other models)
4. **Verify installation**: `ollama list`

## Contributing

To add new Ollama capabilities:

1. Create a new class inheriting from appropriate base classes
2. Implement the required methods
3. Add the new class to the appropriate `__init__.py` file
4. Update this README with usage examples
5. Add tests and documentation

## License

This Ollama module is part of the TalkBridge project and follows the same license terms. 