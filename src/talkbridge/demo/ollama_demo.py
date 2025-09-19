#!/usr/bin/env python3
"""
TalkBridge Demo - Ollama Demo
=============================

Módulo ollama_demo para TalkBridge

Author: TalkBridge Team
Date: 2025-08-19
Version: 1.0

Requirements:
- PyQt6
======================================================================
Functions:
- demo_basic_client: Demo the basic Ollama client capabilities.
- demo_model_manager: Demo the model manager capabilities.
- demo_conversation_manager: Demo the conversation manager capabilities.
- demo_prompt_engineer: Demo the prompt engineer capabilities.
- demo_streaming_client: Demo the streaming client capabilities.
- demo_integration: Demo integration between different Ollama components.
- demo_advanced_features: Demo advanced Ollama features.
- main: Main demo function.
======================================================================
"""
from talkbridge.ollama import OllamaClient


import time
import os
import json

# Add the src directory to the path

from ..ollama import OllamaClient, OllamaModelManager, ConversationManager, PromptEngineer, OllamaStreamingClient
from ollama.streaming_client import ConsoleStreamingCallback, FileStreamingCallback, PerformanceStreamingCallback

def demo_basic_client():
    """Demo the basic Ollama client capabilities."""
    print("\n" + "="*50)
    print("BASIC OLLAMA CLIENT DEMO")
    print("="*50)
    
    client = OllamaClient()
    
    print("Testing basic Ollama client functionality...")
    
    # Health check
    health = client.health_check()
    print(f"Health check: {health}")
    
    if not health['server_available']:
        print("❌ Ollama server not available. Please start Ollama first.")
        return False
    
    # List models
    models = client.list_models()
    print(f"Available models: {[model['name'] for model in models]}")
    
    # Test generation if models are available
    if models:
        test_model = models[0]['name']
        print(f"\nTesting generation with model: {test_model}")
        
        response = client.generate(test_model, "Hello, how are you?")
        if response:
            print(f"Response: {response[:100]}...")
        else:
            print("No response generated")
    
    return True

def demo_model_manager():
    """Demo the model manager capabilities."""
    print("\n" + "="*50)
    print("MODEL MANAGER DEMO")
    print("="*50)
    
    manager = OllamaModelManager()
    
    print("Testing model management capabilities...")
    
    # List models
    models = manager.list_models()
    print(f"Available models: {[model.name for model in models]}")
    
    # Get models summary
    summary = manager.get_models_summary()
    print(f"Models summary: {summary}")
    
    # Test a model if available
    if models:
        test_model = models[0].name
        print(f"\nTesting model: {test_model}")
        
        test_result = manager.test_model(test_model, "What is 2+2?")
        print(f"Test result: {test_result}")
    
    # Export model list
    export_file = "models_export.json"
    if manager.export_model_list(export_file):
        print(f"Exported model list to: {export_file}")
    
    return True

def demo_conversation_manager():
    """Demo the conversation manager capabilities."""
    print("\n" + "="*50)
    print("CONVERSATION MANAGER DEMO")
    print("="*50)
    
    manager = ConversationManager()
    
    print("Testing conversation management...")
    
    # Create a conversation
    conv_id = manager.create_conversation("Test Conversation", "llama2")
    print(f"Created conversation: {conv_id}")
    
    # Send a message
    response_id = manager.send_message(conv_id, "Hello, how are you?")
    print(f"Got response ID: {response_id}")
    
    # Get conversation summary
    summary = manager.get_conversation_summary(conv_id)
    print(f"Conversation summary: {summary}")
    
    # Get conversation stats
    stats = manager.get_conversation_stats()
    print(f"Conversation stats: {stats}")
    
    # Export conversation
    export_file = "conversation_export.json"
    if manager.export_conversation(conv_id, export_file):
        print(f"Exported conversation to: {export_file}")
    
    return True

def demo_prompt_engineer():
    """Demo the prompt engineer capabilities."""
    print("\n" + "="*50)
    print("PROMPT ENGINEER DEMO")
    print("="*50)
    
    engineer = PromptEngineer()
    
    print("Testing prompt engineering capabilities...")
    
    # List templates
    templates = engineer.list_templates()
    print(f"Available templates: {[t.name for t in templates]}")
    
    # Test a template
    if templates:
        template = templates[0]  # Use first template
        variables = {"task": "Write a Python function to calculate fibonacci numbers"}
        
        prompt = engineer.render_template(template.name, variables)
        if prompt:
            print(f"\nRendered prompt: {prompt[:200]}...")
            
            # Test the prompt
            result = engineer.test_prompt(prompt)
            print(f"Test result: {result.response[:100]}...")
    
    # Get template stats
    stats = engineer.get_template_stats()
    print(f"Template stats: {stats}")
    
    # Export templates
    export_file = "templates_export.json"
    if engineer.export_templates(export_file):
        print(f"Exported templates to: {export_file}")
    
    return True

def demo_streaming_client():
    """Demo the streaming client capabilities."""
    print("\n" + "="*50)
    print("STREAMING CLIENT DEMO")
    print("="*50)
    
    client = OllamaStreamingClient()
    
    print("Testing streaming capabilities...")
    
    # Add console callback
    console_callback = ConsoleStreamingCallback(show_timestamps=True)
    client.add_callback(console_callback)
    
    # Add performance callback
    perf_callback = PerformanceStreamingCallback()
    client.add_callback(perf_callback)
    
    try:
        # Test streaming generation
        print("\nTesting streaming generation...")
        full_response = ""
        for chunk in client.stream_generate("llama2", "Tell me a short story about a robot."):
            full_response += chunk
        
        print(f"\nFull response length: {len(full_response)} characters")
        
        # Test streaming chat
        print("\nTesting streaming chat...")
        messages = [{"role": "user", "content": "What is the capital of France?"}]
        chat_response = ""
        for chunk in client.stream_chat("llama2", messages):
            chat_response += chunk
        
        print(f"Chat response length: {len(chat_response)} characters")
        
    except Exception as e:
        print(f"Streaming test error: {e}")
        return False
    
    return True

def demo_integration():
    """Demo integration between different Ollama components."""
    print("\n" + "="*50)
    print("OLLAMA INTEGRATION DEMO")
    print("="*50)
    
    try:
        # Initialize components
        client = OllamaClient()
        model_manager = OllamaModelManager(client)
        conversation_manager = ConversationManager(client)
        prompt_engineer = PromptEngineer(client)
        streaming_client = OllamaStreamingClient(client)
        
        print("Testing integrated Ollama workflow...")
        
        # Check if server is available
        if not client.ping():
            print("❌ Ollama server not available")
            return False
        
        # Get available models
        models = model_manager.list_models()
        if not models:
            print("❌ No models available")
            return False
        
        test_model = models[0].name
        print(f"Using model: {test_model}")
        
        # Create a conversation
        conv_id = conversation_manager.create_conversation("Integration Test", test_model)
        
        # Use prompt engineer to create a prompt
        templates = prompt_engineer.list_templates()
        if templates:
            template = templates[0]
            variables = {"task": "Explain quantum computing in simple terms"}
            prompt = prompt_engineer.render_template(template.name, variables)
            
            if prompt:
                # Send message through conversation manager
                response_id = conversation_manager.send_message(conv_id, prompt)
                print(f"Generated response ID: {response_id}")
                
                # Get conversation summary
                summary = conversation_manager.get_conversation_summary(conv_id)
                print(f"Conversation summary: {summary}")
        
        print("✅ Integration demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration demo error: {e}")
        return False

def demo_advanced_features():
    """Demo advanced Ollama features."""
    print("\n" + "="*50)
    print("ADVANCED FEATURES DEMO")
    print("="*50)
    
    try:
        client = OllamaClient()
        
        print("Testing advanced features...")
        
        # Test streaming with file callback
        file_callback = FileStreamingCallback("ollama_stream.log", append=True)
        streaming_client = OllamaStreamingClient(client)
        streaming_client.add_callback(file_callback)
        
        print("Testing file streaming...")
        for chunk in streaming_client.stream_generate("llama2", "Write a poem about technology."):
            pass  # Chunks are handled by file callback
        
        print("✅ File streaming completed. Check ollama_stream.log")
        
        # Test model management features
        model_manager = OllamaModelManager(client)
        
        # Get detailed model info
        models = model_manager.list_models()
        if models:
            model_info = model_manager.get_model_info(models[0].name)
            if model_info:
                print(f"Model info: {model_info}")
        
        # Test prompt optimization
        prompt_engineer = PromptEngineer(client)
        base_prompt = "Explain machine learning"
        target_response = "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."
        
        optimized_prompt = prompt_engineer.optimize_prompt(base_prompt, target_response, iterations=3)
        print(f"Optimized prompt: {optimized_prompt}")
        
        print("✅ Advanced features demo completed!")
        return True
        
    except Exception as e:
        print(f"❌ Advanced features demo error: {e}")
        return False

def main():
    """Main demo function."""
    print("🤖 TALKBRIDGE OLLAMA INTEGRATION DEMO 🤖")
    print("This demo showcases all Ollama integration capabilities")
    print("Make sure Ollama is running before starting the demo")
    
    try:
        # Run all demos
        demos = [
            ("Basic Client", demo_basic_client),
            ("Model Manager", demo_model_manager),
            ("Conversation Manager", demo_conversation_manager),
            ("Prompt Engineer", demo_prompt_engineer),
            ("Streaming Client", demo_streaming_client),
            ("Integration", demo_integration),
            ("Advanced Features", demo_advanced_features)
        ]
        
        successful_demos = 0
        total_demos = len(demos)
        
        for name, demo_func in demos:
            print(f"\n{'='*20} {name} {'='*20}")
            try:
                if demo_func():
                    successful_demos += 1
                    print(f"✅ {name} demo completed successfully")
                else:
                    print(f"❌ {name} demo failed")
            except Exception as e:
                print(f"❌ {name} demo error: {e}")
        
        print("\n" + "="*50)
        print("🎉 OLLAMA DEMO SUMMARY 🎉")
        print("="*50)
        print(f"Successful demos: {successful_demos}/{total_demos}")
        
        if successful_demos == total_demos:
            print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY! 🎉")
        else:
            print(f"⚠️  {total_demos - successful_demos} demos failed")
        
        print("\nOllama integration capabilities include:")
        print("✅ Advanced Ollama client with streaming and error handling")
        print("✅ Model management (install, remove, test, export/import)")
        print("✅ Conversation management with message history")
        print("✅ Prompt engineering with templates and optimization")
        print("✅ Real-time streaming with callbacks and event handling")
        print("✅ Comprehensive integration between all components")
        print("✅ Performance monitoring and logging")
        print("\nYou can now integrate these Ollama capabilities into your TalkBridge application!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Exiting...")
    except Exception as e:
        print(f"\nDemo error: {e}")
        print("Make sure Ollama is running and accessible:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Start Ollama: ollama serve")
        print("3. Pull a model: ollama pull llama2")

if __name__ == "__main__":
    main() 