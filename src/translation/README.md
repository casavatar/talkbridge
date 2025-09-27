# Offline Translation Module

This module provides **completely offline** translation capabilities using local translation models. It supports multiple translation engines and can work without an internet connection once models are downloaded.

## Features

- ✅ **100% Offline**: Works without internet connection after initial model download
- ✅ **Multiple Engines**: Supports both argos-translate and HuggingFace MarianMT models
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux
- ✅ **Fast & Lightweight**: Optimized for real-time interaction
- ✅ **Automatic Fallback**: Falls back to alternative engines if primary fails
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Modular Design**: Easy to extend for additional languages or engines

## Supported Languages

### Primary Engine (argos-translate)

- English → Spanish
- Spanish → English
- French → Spanish
- German → Spanish
- Italian → Spanish
- Portuguese → Spanish

### Fallback Engine (HuggingFace MarianMT)

- English → Spanish
- Spanish → English
- French → Spanish
- German → Spanish
- Italian → Spanish
- Portuguese → Spanish

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install argos-translate>=1.9.0
pip install transformers>=4.20.0
pip install torch>=1.12.0
pip install sentencepiece>=0.1.96
```

### 2. First Run Setup

On first run, the module will automatically download the necessary translation models. This requires an internet connection only for the initial download.

## Quick Start

### Basic Usage

```python
from src.translation import translate_to_spanish

# Simple translation
text = "Hello, how are you?"
translated = translate_to_spanish(text)
print(translated)  # "Hola, ¿cómo estás?"
```

### Advanced Usage

```python
from src.translation import OfflineTranslator

# Create translator instance
translator = OfflineTranslator(
    preferred_engine="argos",  # or "huggingface"
    auto_download=True
)

# Translate from different languages
texts = [
    ("en", "Hello world"),
    ("fr", "Bonjour le monde"),
    ("de", "Hallo Welt"),
    ("it", "Ciao mondo")
]

for source_lang, text in texts:
    translated = translator.translate_to_spanish(text, source_lang)
    print(f"{source_lang}: {text} → {translated}")
```

## API Reference

### Main Function

#### `translate_to_spanish(text: str, source_lang: str = "en") -> str`

Convenience function for translating text to Spanish.

**Parameters:**

- `text`: Text to translate
- `source_lang`: Source language code (default: "en")

**Returns:**

- Translated text in Spanish

**Raises:**

- `TranslationError`: If translation fails

### Class

#### `OfflineTranslator`

Main translation class with advanced features.

**Constructor:**

```python
OfflineTranslator(
    preferred_engine: str = "argos",
    model_cache_dir: Optional[str] = None,
    auto_download: bool = True
)
```

**Methods:**

- `translate_to_spanish(text: str, source_lang: str = "en") -> str`
- `get_supported_languages() -> Dict[str, Dict[str, str]]`
- `is_available() -> bool`

## Model Management

### Model Cache Location

Models are cached in:

- **macOS/Linux**: `~/.cache/talkbridge/translation_models/`
- **Windows**: `%USERPROFILE%\.cache\talkbridge\translation_models\`

### Model Download

Models are automatically downloaded on first use. You can also pre-download models:

```python
from src.translation import OfflineTranslator

translator = OfflineTranslator()
# Models will be downloaded automatically when first used
```

### Supported Model Sizes

- **argos-translate**: ~50-100MB per language pair
- **HuggingFace MarianMT**: ~200-500MB per language pair

## Performance

### Typical Performance (on modern hardware)

| Engine | First Load | Subsequent Loads | Translation Speed |
|--------|------------|------------------|-------------------|
| argos-translate | 2-5s | <1s | 0.1-0.5s |
| HuggingFace | 5-15s | 1-3s | 0.5-2s |

### Optimization Tips

1. **Use argos-translate for speed**: Set `preferred_engine="argos"`
2. **Reuse translator instance**: Don't create new instances for each translation
3. **Batch translations**: Process multiple texts together when possible

## Error Handling

The module provides comprehensive error handling:

```python
from src.translation import translate_to_spanish, TranslationError

try:
    result = translate_to_spanish("Hello world")
    print(result)
except TranslationError as e:
    print(f"Translation failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Common Error Scenarios

1. **No models available**: Install required packages
2. **Model download failed**: Check internet connection
3. **Unsupported language pair**: Check supported languages list
4. **Memory issues**: Use smaller models or increase system memory

## Examples

### Example 1: Basic Translation

```python
from src.translation import translate_to_spanish

texts = [
    "Hello, how are you?",
    "The weather is beautiful today.",
    "I love programming in Python."
]

for text in texts:
    translated = translate_to_spanish(text)
    print(f"{text} → {translated}")
```

### Example 2: Multi-language Translation

```python
from src.translation import OfflineTranslator

translator = OfflineTranslator()

languages = {
    "en": "Hello world",
    "fr": "Bonjour le monde", 
    "de": "Hallo Welt",
    "it": "Ciao mondo"
}

for lang, text in languages.items():
    translated = translator.translate_to_spanish(text, lang)
    print(f"{lang.upper()}: {text} → {translated}")
```

### Example 3: Error Handling

```python
from src.translation import translate_to_spanish, TranslationError

def safe_translate(text, source_lang="en"):
    try:
        return translate_to_spanish(text, source_lang)
    except TranslationError as e:
        return f"Translation failed: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

# Test with various inputs
test_cases = [
    ("Hello world", "en"),
    ("", "en"),  # Empty string
    ("Hello", "zh"),  # Unsupported language
]

for text, lang in test_cases:
    result = safe_translate(text, lang)
    print(f"'{text}' ({lang}) → {result}")
```

## Testing

Run the demo script to test the translation functionality:

```bash
python src/translation_demo.py
```

This will:

- Show system information
- Test basic translation
- Measure performance
- Test multi-language support
- Test error handling

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'argostranslate'**

   ```bash
   pip install argos-translate
   ```

2. **ImportError: No module named 'transformers'**

   ```bash
   pip install transformers torch sentencepiece
   ```

3. **Model download fails**
   - Check internet connection
   - Try using a different network
   - Check available disk space

4. **Slow performance**
   - Use argos-translate engine for speed
   - Ensure sufficient RAM
   - Close other applications

5. **Memory errors**
   - Use smaller models
   - Increase system memory
   - Process shorter texts

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from src.translation import translate_to_spanish
result = translate_to_spanish("Hello world")
```

## Contributing

To extend the translation module:

1. Add new language pairs to `supported_pairs` in `OfflineTranslator`
2. Implement new translation engines
3. Add tests for new functionality
4. Update documentation

## License

This module is part of the talkbridge project.

## Changelog

### Version 1.0.0

- Initial release
- Support for argos-translate and HuggingFace engines
- Offline translation capabilities
- Comprehensive error handling
- Performance optimization
