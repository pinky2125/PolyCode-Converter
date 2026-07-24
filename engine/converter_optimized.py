"""
Optimized Converter Module with Dictionary-based Routing and Better Error Handling
"""
import logging
from typing import Dict, Callable, Optional
from engine.python_to_java import convert as py_to_java
from engine.java_to_python import convert as java_to_py
from engine.python_to_c import convert as py_to_c
from engine.c_to_python import convert as c_to_py
from engine.c_to_java import convert as c_to_java
from engine.java_to_c import convert as java_to_c
from engine.python_to_cpp import convert as py_to_cpp
from engine.cpp_to_python import convert as cpp_to_py
from engine.cpp_to_java import convert as cpp_to_java
from engine.java_to_cpp import convert as java_to_cpp
from engine.c_to_cpp import convert as c_to_cpp
from engine.cpp_to_c import convert as cpp_to_c

logger = logging.getLogger(__name__)

# Define supported language pairs
CONVERTERS: Dict[tuple, Callable] = {
    ('python', 'java'): py_to_java,
    ('java', 'python'): java_to_py,
    ('python', 'c'): py_to_c,
    ('c', 'python'): c_to_py,
    ('c', 'java'): c_to_java,
    ('java', 'c'): java_to_c,
    ('python', 'cpp'): py_to_cpp,
    ('cpp', 'python'): cpp_to_py,
    ('cpp', 'java'): cpp_to_java,
    ('java', 'cpp'): java_to_cpp,
    ('c', 'cpp'): c_to_cpp,
    ('cpp', 'c'): cpp_to_c,
}

SUPPORTED_LANGUAGES = {'python', 'java', 'c', 'cpp'}


def validate_language(language: str) -> str:
    """Validate and normalize language name"""
    lang_lower = language.lower().strip()
    if lang_lower not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}. Supported: {SUPPORTED_LANGUAGES}")
    return lang_lower


def validate_code(code: str) -> str:
    """Validate code input"""
    if not isinstance(code, str):
        raise TypeError("Code must be a string")
    if not code.strip():
        raise ValueError("Code cannot be empty")
    if len(code) > 1000000:  # 1MB limit
        raise ValueError("Code exceeds maximum length (1MB)")
    return code


def convert_code(code: str, source_lang: str, target_lang: str) -> str:
    """
    Convert code from source language to target language
    
    Args:
        code: Source code string
        source_lang: Source programming language
        target_lang: Target programming language
        
    Returns:
        Converted code string
        
    Raises:
        ValueError: If language or conversion pair is not supported
        TypeError: If inputs are invalid types
    """
    try:
        # Validate inputs
        code = validate_code(code)
        source_lang = validate_language(source_lang)
        target_lang = validate_language(target_lang)
        
        # Check if same language
        if source_lang == target_lang:
            logger.warning(f"Source and target languages are the same: {source_lang}")
            return code
        
        # Get converter function
        conversion_key = (source_lang, target_lang)
        if conversion_key not in CONVERTERS:
            available = [f"{src} → {tgt}" for src, tgt in CONVERTERS.keys()]
            raise ValueError(
                f"Conversion not supported: {source_lang} → {target_lang}\n"
                f"Available conversions: {', '.join(sorted(available))}"
            )
        
        converter = CONVERTERS[conversion_key]
        logger.info(f"Converting from {source_lang} to {target_lang}")
        
        # Perform conversion
        result = converter(code)
        
        if not result:
            raise ValueError("Conversion returned empty result")
        
        logger.info(f"Conversion successful: {source_lang} → {target_lang}")
        return result
        
    except (ValueError, TypeError) as e:
        logger.error(f"Conversion error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {e}")
        raise


def get_supported_languages() -> list:
    """Get list of supported languages"""
    return sorted(list(SUPPORTED_LANGUAGES))


def get_available_conversions() -> Dict[str, list]:
    """Get dictionary of available conversions for each language"""
    conversions = {lang: [] for lang in SUPPORTED_LANGUAGES}
    for source, target in CONVERTERS.keys():
        conversions[source].append(target)
    return conversions
