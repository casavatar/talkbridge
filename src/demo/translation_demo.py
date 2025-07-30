#!/usr/bin/env python3
#----------------------------------------------------------------------------------------------------------------------------
# description: Offline Translation Demo
#----------------------------------------------------------------------------------------------------------------------------
# 
# author: ingekastel
# date: 2025-06-02
# version: 1.0
# 
# requirements:
# - argos-translate Python package
# - transformers Python package
# - sentencepiece Python package
# - torch Python package
#----------------------------------------------------------------------------------------------------------------------------
# functions:
# - test_basic_translation: Test basic translation functionality
# - test_performance: Test translation performance
# - test_different_languages: Test translation from different source languages
# - test_error_handling: Test error handling with invalid inputs
# - show_system_info: Show system information and available engines
#----------------------------------------------------------------------------------------------------------------------------

import time
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.translation import translate_to_spanish, OfflineTranslator, TranslationError


def test_basic_translation():
    """Test basic translation functionality."""
    print("=" * 60)
    print("BASIC TRANSLATION TEST")
    print("=" * 60)
    
    test_texts = [
        "Hello, how are you?",
        "The weather is beautiful today.",
        "I love programming in Python.",
        "This is a test of the translation system.",
        "Machine learning is fascinating.",
        "The quick brown fox jumps over the lazy dog."
    ]
    
    for i, text in enumerate(test_texts, 1):
        try:
            print(f"\n{i}. Original: {text}")
            translated = translate_to_spanish(text)
            print(f"   Translated: {translated}")
        except TranslationError as e:
            print(f"   ERROR: {e}")
        except Exception as e:
            print(f"   UNEXPECTED ERROR: {e}")


def test_performance():
    """Test translation performance."""
    print("\n" + "=" * 60)
    print("PERFORMANCE TEST")
    print("=" * 60)
    
    # Initialize translator once
    translator = OfflineTranslator()
    
    if not translator.is_available():
        print("ERROR: No translation engines available!")
        return
    
    test_text = "This is a performance test of the offline translation system."
    
    print(f"Testing with text: '{test_text}'")
    print(f"Available engines: argos={translator.argos_available}, huggingface={translator.hf_available}")
    print(f"Preferred engine: {translator.preferred_engine}")
    
    # Test multiple runs to get average performance
    times = []
    for i in range(5):
        try:
            start_time = time.time()
            result = translator.translate_to_spanish(test_text)
            end_time = time.time()
            latency = end_time - start_time
            times.append(latency)
            print(f"Run {i+1}: {latency:.3f}s - '{result}'")
        except Exception as e:
            print(f"Run {i+1}: ERROR - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"\nPerformance Summary:")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Min time: {min_time:.3f}s")
        print(f"  Max time: {max_time:.3f}s")


def test_different_languages():
    """Test translation from different source languages."""
    print("\n" + "=" * 60)
    print("MULTI-LANGUAGE TEST")
    print("=" * 60)
    
    test_cases = [
        ("en", "Hello world"),
        ("fr", "Bonjour le monde"),
        ("de", "Hallo Welt"),
        ("it", "Ciao mondo"),
        ("pt", "Olá mundo")
    ]
    
    translator = OfflineTranslator()
    
    for source_lang, text in test_cases:
        try:
            print(f"\n{source_lang.upper()}: {text}")
            translated = translator.translate_to_spanish(text, source_lang)
            print(f"ES: {translated}")
        except TranslationError as e:
            print(f"ERROR: {e}")
        except Exception as e:
            print(f"UNEXPECTED ERROR: {e}")


def test_error_handling():
    """Test error handling with invalid inputs."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING TEST")
    print("=" * 60)
    
    test_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("a" * 1000, "Very long text"),
        ("Hello", "zh"),  # Unsupported language
    ]
    
    for text, description in test_cases:
        try:
            print(f"\nTesting: {description}")
            if description == "Unsupported language":
                translated = translate_to_spanish(text, "zh")
            else:
                translated = translate_to_spanish(text)
            print(f"Result: '{translated}'")
        except TranslationError as e:
            print(f"Expected error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


def show_system_info():
    """Show system information and available engines."""
    print("=" * 60)
    print("SYSTEM INFORMATION")
    print("=" * 60)
    
    translator = OfflineTranslator()
    
    print(f"Python version: {sys.version}")
    print(f"Available engines:")
    print(f"  - argos-translate: {translator.argos_available}")
    print(f"  - HuggingFace: {translator.hf_available}")
    print(f"  - Any engine available: {translator.is_available()}")
    
    if translator.is_available():
        print(f"\nSupported language pairs:")
        supported = translator.get_supported_languages()
        for engine, pairs in supported.items():
            print(f"  {engine.upper()}:")
            for pair, description in pairs.items():
                print(f"    - {pair}: {description}")
    else:
        print("\nNo translation engines available!")
        print("Please install required packages:")
        print("  pip install argos-translate")
        print("  pip install transformers torch sentencepiece")


def main():
    """Main demo function."""
    print("OFFLINE TRANSLATION DEMO")
    print("=" * 60)
    print("This demo showcases the offline translation capabilities")
    print("of the talkbridge translation module.")
    print()
    
    # Show system information first
    show_system_info()
    
    # Run tests
    test_basic_translation()
    test_performance()
    test_different_languages()
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
    print("The offline translation module is ready for use!")
    print("You can now use translate_to_spanish() function in your applications.")


if __name__ == "__main__":
    main() 