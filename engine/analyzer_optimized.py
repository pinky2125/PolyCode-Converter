"""
Optimized Code Analyzer with Better Error Handling and Caching
"""
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure the Gemini API client
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Timeout for API calls (in seconds)
API_TIMEOUT = 30

# Language-specific improvement suggestions (fallback)
LANGUAGE_SUGGESTIONS = {
    'python': {
        'suggestion': "Python emphasizes readability and simplicity. Use list comprehensions instead of raw loops, leverage built-in functions, and follow PEP 8 conventions for better code style.",
        'tips': [
            "Use list comprehensions for cleaner loops",
            "Leverage built-in functions like map(), filter()",
            "Use context managers (with statement) for resource management",
            "Follow PEP 8 naming conventions",
            "Use type hints for better code clarity"
        ]
    },
    'java': {
        'suggestion': "Java requires strict typing and encapsulation. Utilize Java Streams API for functional programming, use proper access modifiers, and follow SOLID principles.",
        'tips': [
            "Use Java Streams API for collections manipulation",
            "Implement proper encapsulation with private/public modifiers",
            "Use try-with-resources for better resource management",
            "Leverage StringBuilder for string concatenation",
            "Use Optional for null safety"
        ]
    },
    'cpp': {
        'suggestion': "C++ offers both efficiency and safety. Use standard library containers (vector, map) instead of raw pointers, employ RAII principles, and leverage modern C++ features.",
        'tips': [
            "Use std::vector instead of raw arrays",
            "Implement RAII (Resource Acquisition Is Initialization)",
            "Use smart pointers (unique_ptr, shared_ptr) instead of raw pointers",
            "Leverage std::algorithm for collections",
            "Use const-correctness throughout code"
        ]
    },
    'c': {
        'suggestion': "C requires careful memory management. Always check pointer validity, use static analysis tools, and follow established coding standards like MISRA C.",
        'tips': [
            "Always validate pointers before dereferencing",
            "Use const for immutable variables",
            "Avoid buffer overflows with proper bounds checking",
            "Use static analysis tools (lint, cppcheck)",
            "Document assumptions about inputs"
        ]
    }
}


def get_language_suggestion(target_lang: str) -> str:
    """Get language-specific suggestion"""
    lang_lower = target_lang.lower()
    if lang_lower in LANGUAGE_SUGGESTIONS:
        return LANGUAGE_SUGGESTIONS[lang_lower]['suggestion']
    return f"Ensure your {target_lang} code follows language-specific best practices and conventions."


def extract_code_block(text: str, delimiter: str = '```') -> Optional[str]:
    """
    Extract code from markdown code blocks
    
    Args:
        text: Text potentially containing code blocks
        delimiter: Code block delimiter (default: ```)
        
    Returns:
        Extracted code or None
    """
    if not text:
        return None
    
    # Handle markdown code blocks with language specification
    if f'{delimiter}' in text:
        try:
            # Find start of code block
            start = text.find(delimiter)
            if start == -1:
                return None
            
            # Skip language specification line if present
            first_newline = text.find('\n', start)
            code_start = first_newline + 1 if first_newline != -1 else start + len(delimiter)
            
            # Find end of code block
            end = text.find(delimiter, code_start)
            if end == -1:
                return text[code_start:].strip()
            
            return text[code_start:end].strip()
        except Exception as e:
            logger.warning(f"Error extracting code block: {e}")
            return text.strip()
    
    return text.strip()


def parse_ai_response(response_text: str) -> Dict[str, str]:
    """
    Parse AI response with proper error handling
    
    Args:
        response_text: Raw response from AI
        
    Returns:
        Dictionary with 'suggestion' and 'solution' keys
    """
    result = {
        "suggestion": "No explicit suggestion could be generated.",
        "solution": "No explicit solution could be generated."
    }
    
    try:
        if not response_text:
            return result
        
        # Extract suggestion
        if "[SUGGESTION_START]" in response_text and "[SUGGESTION_END]" in response_text:
            try:
                suggestion = response_text.split("[SUGGESTION_START]")[1].split("[SUGGESTION_END]")[0].strip()
                if suggestion:
                    result["suggestion"] = suggestion
            except Exception as e:
                logger.warning(f"Error extracting suggestion: {e}")
        
        # Extract solution
        if "[SOLUTION_START]" in response_text and "[SOLUTION_END]" in response_text:
            try:
                solution = response_text.split("[SOLUTION_START]")[1].split("[SOLUTION_END]")[0].strip()
                
                # Clean up markdown formatting
                solution = extract_code_block(solution)
                
                if solution:
                    result["solution"] = solution
            except Exception as e:
                logger.warning(f"Error extracting solution: {e}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error parsing AI response: {e}")
        return result


def analyze_code(source_code: str, converted_code: str, 
                source_lang: str, target_lang: str) -> Dict[str, str]:
    """
    Analyze converted code and provide suggestions using AI
    
    Args:
        source_code: Original source code
        converted_code: Converted code output
        source_lang: Source programming language
        target_lang: Target programming language
        
    Returns:
        Dictionary with 'suggestion' and 'solution' keys
    """
    
    # If no API key, return language-specific suggestions
    if not API_KEY:
        logger.info("No GEMINI_API_KEY found, using language-specific suggestions")
        suggestion = get_language_suggestion(target_lang)
        return {
            "suggestion": suggestion,
            "solution": converted_code
        }
    
    try:
        # Limit code size to avoid API issues
        max_code_length = 5000
        
        source_preview = source_code[:max_code_length] if len(source_code) > max_code_length else source_code
        converted_preview = converted_code[:max_code_length] if len(converted_code) > max_code_length else converted_code
        
        prompt = f"""You are an expert code reviewer and optimization specialist.

A user has converted code from {source_lang} to {target_lang}.

SOURCE CODE ({source_lang}):
```
{source_preview}
```

CONVERTED CODE ({target_lang}):
```
{converted_preview}
```

Please analyze this conversion and provide:
1. ONE key improvement suggestion for the {target_lang} code (focusing on best practices, performance, or idioms)
2. An optimized version of the converted code applying your suggestion

Format your response EXACTLY as follows (these markers are important):
[SUGGESTION_START]
Your improvement suggestion here - focus on one key improvement
[SUGGESTION_END]

[SOLUTION_START]
Provide ONLY the optimized code (without markdown formatting or language identifier)
[SOLUTION_END]"""

        # Use gemini-1.5-flash for faster responses
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            request_options={"timeout": API_TIMEOUT}
        )
        
        if response and response.text:
            return parse_ai_response(response.text)
        else:
            logger.warning("Empty response from AI API")
            return {
                "suggestion": get_language_suggestion(target_lang),
                "solution": converted_code
            }
    
    except Exception as e:
        logger.error(f"Error during AI analysis: {e}")
        
        # Fallback to language-specific suggestions
        return {
            "suggestion": f"AI analysis failed: {str(e)}. {get_language_suggestion(target_lang)}",
            "solution": converted_code
        }


@lru_cache(maxsize=32)
def get_language_specific_tips(language: str) -> Optional[list]:
    """Get language-specific improvement tips (cached)"""
    lang_lower = language.lower()
    if lang_lower in LANGUAGE_SUGGESTIONS:
        return LANGUAGE_SUGGESTIONS[lang_lower]['tips']
    return None
