"""
Language utilities for TalkBridge

Provides centralized language support information for all adapters and components.
"""

from typing import Dict, List, Set

# Comprehensive list of supported languages based on Whisper, TTS, and Translation services
# This consolidates the language support from all adapters
WHISPER_LANGUAGES = [
    'en', 'zh', 'de', 'es', 'ru', 'ko', 'fr', 'ja', 'pt', 'tr', 'pl', 'ca', 'nl',
    'ar', 'sv', 'it', 'id', 'hi', 'fi', 'vi', 'he', 'uk', 'el', 'ms', 'cs', 'ro',
    'da', 'hu', 'ta', 'no', 'th', 'ur', 'hr', 'bg', 'lt', 'la', 'mi', 'ml', 'cy',
    'sk', 'te', 'fa', 'lv', 'bn', 'sr', 'az', 'sl', 'kn', 'et', 'mk', 'br', 'eu',
    'is', 'hy', 'ne', 'mn', 'bs', 'kk', 'sq', 'sw', 'gl', 'mr', 'pa', 'si', 'km',
    'sn', 'yo', 'so', 'af', 'oc', 'ka', 'be', 'tg', 'sd', 'gu', 'am', 'yi', 'lo',
    'uz', 'fo', 'ht', 'ps', 'tk', 'nn', 'mt', 'sa', 'lb', 'my', 'bo', 'tl', 'mg',
    'as', 'tt', 'haw', 'ln', 'ha', 'ba', 'jw', 'su'
]

TTS_LANGUAGES = [
    'ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi', 'fr', 'he',
    'hi', 'hr', 'hu', 'id', 'it', 'ja', 'ko', 'lv', 'ms', 'mt', 'nl', 'no', 'pl',
    'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'th', 'tr', 'uk', 'vi', 'zh'
]

TRANSLATION_LANGUAGES = [
    'af', 'ar', 'az', 'be', 'bg', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el',
    'en', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'ga', 'gl', 'gu', 'he', 'hi', 'hr',
    'hu', 'hy', 'id', 'is', 'it', 'ja', 'ka', 'kk', 'km', 'kn', 'ko', 'ky', 'la',
    'lb', 'lo', 'lt', 'lv', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl',
    'no', 'pa', 'pl', 'pt', 'ro', 'ru', 'si', 'sk', 'sl', 'sq', 'sr', 'sv', 'sw',
    'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'uz', 'vi', 'yi', 'zh', 'zu'
]

# Language names mapping
LANGUAGE_NAMES = {
    'af': 'Afrikaans',
    'am': 'Amharic',
    'ar': 'Arabic',
    'as': 'Assamese',
    'az': 'Azerbaijani',
    'ba': 'Bashkir',
    'be': 'Belarusian',
    'bg': 'Bulgarian',
    'bn': 'Bengali',
    'bo': 'Tibetan',
    'br': 'Breton',
    'bs': 'Bosnian',
    'ca': 'Catalan',
    'cs': 'Czech',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'el': 'Greek',
    'en': 'English',
    'es': 'Spanish',
    'et': 'Estonian',
    'eu': 'Basque',
    'fa': 'Persian',
    'fi': 'Finnish',
    'fo': 'Faroese',
    'fr': 'French',
    'ga': 'Irish',
    'gl': 'Galician',
    'gu': 'Gujarati',
    'ha': 'Hausa',
    'haw': 'Hawaiian',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hr': 'Croatian',
    'ht': 'Haitian Creole',
    'hu': 'Hungarian',
    'hy': 'Armenian',
    'id': 'Indonesian',
    'is': 'Icelandic',
    'it': 'Italian',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'ka': 'Georgian',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'kn': 'Kannada',
    'ko': 'Korean',
    'ky': 'Kyrgyz',
    'la': 'Latin',
    'lb': 'Luxembourgish',
    'ln': 'Lingala',
    'lo': 'Lao',
    'lt': 'Lithuanian',
    'lv': 'Latvian',
    'mg': 'Malagasy',
    'mi': 'Maori',
    'mk': 'Macedonian',
    'ml': 'Malayalam',
    'mn': 'Mongolian',
    'mr': 'Marathi',
    'ms': 'Malay',
    'mt': 'Maltese',
    'my': 'Myanmar',
    'ne': 'Nepali',
    'nl': 'Dutch',
    'nn': 'Norwegian Nynorsk',
    'no': 'Norwegian',
    'oc': 'Occitan',
    'pa': 'Punjabi',
    'pl': 'Polish',
    'ps': 'Pashto',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sa': 'Sanskrit',
    'sd': 'Sindhi',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'sn': 'Shona',
    'so': 'Somali',
    'sq': 'Albanian',
    'sr': 'Serbian',
    'su': 'Sundanese',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'tg': 'Tajik',
    'th': 'Thai',
    'tk': 'Turkmen',
    'tl': 'Tagalog',
    'tr': 'Turkish',
    'tt': 'Tatar',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zh': 'Chinese',
    'zu': 'Zulu'
}


def get_supported_languages(service: str = 'all') -> List[str]:
    """
    Get list of supported languages for a specific service or all services.
    
    Args:
        service: Service type ('whisper', 'tts', 'translation', 'all')
        
    Returns:
        List of supported language codes
    """
    if service.lower() == 'whisper':
        return WHISPER_LANGUAGES.copy()
    elif service.lower() == 'tts':
        return TTS_LANGUAGES.copy()
    elif service.lower() == 'translation':
        return TRANSLATION_LANGUAGES.copy()
    else:
        # Return intersection of all services for maximum compatibility
        all_languages = set(WHISPER_LANGUAGES) & set(TTS_LANGUAGES) & set(TRANSLATION_LANGUAGES)
        return sorted(list(all_languages))


def get_supported_languages_dict(service: str = 'all') -> Dict[str, str]:
    """
    Get dictionary of supported languages with language codes as keys and names as values.
    
    Args:
        service: Service type ('whisper', 'tts', 'translation', 'all')
        
    Returns:
        Dictionary mapping language codes to language names
    """
    supported_codes = get_supported_languages(service)
    return {code: LANGUAGE_NAMES.get(code, code.upper()) for code in supported_codes}


def is_language_supported(language_code: str, service: str = 'all') -> bool:
    """
    Check if a language is supported by a specific service.
    
    Args:
        language_code: Language code to check
        service: Service type ('whisper', 'tts', 'translation', 'all')
        
    Returns:
        True if language is supported, False otherwise
    """
    supported_languages = get_supported_languages(service)
    return language_code.lower() in [lang.lower() for lang in supported_languages]


def get_language_name(language_code: str) -> str:
    """
    Get the human-readable name for a language code.
    
    Args:
        language_code: Language code
        
    Returns:
        Human-readable language name
    """
    return LANGUAGE_NAMES.get(language_code.lower(), language_code.upper())


def get_common_languages() -> List[str]:
    """
    Get list of most commonly used languages that are supported by all services.
    
    Returns:
        List of common language codes
    """
    common_languages = [
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh',
        'ar', 'hi', 'nl', 'sv', 'no', 'da', 'fi', 'pl', 'cs', 'hu'
    ]
    # Filter to only include languages supported by all services
    all_supported = get_supported_languages('all')
    return [lang for lang in common_languages if lang in all_supported]