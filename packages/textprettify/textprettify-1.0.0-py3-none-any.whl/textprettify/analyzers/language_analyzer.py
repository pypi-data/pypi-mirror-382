"""
Language detection and analysis functionality for TextPrettify.
"""

import re
from typing import Dict, List, Optional


class LanguageAnalyzer:
    """
    Analyzer for language detection and linguistic analysis.

    Provides methods for detecting text language using heuristics.
    """

    # Common word patterns for basic language detection
    LANGUAGE_PATTERNS = {
        "en": ["the", "is", "and", "or", "of", "to", "in", "a", "that", "it"],
        "es": ["el", "la", "de", "que", "y", "es", "en", "un", "por", "con"],
        "fr": ["le", "de", "un", "et", "être", "à", "il", "pour", "dans", "ce"],
        "de": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich"],
        "it": ["il", "di", "e", "la", "che", "per", "un", "in", "è", "non"],
        "pt": ["o", "de", "e", "a", "que", "do", "da", "em", "um", "para"],
    }

    def __init__(self, text: str):
        """
        Initialize the LanguageAnalyzer with input text.

        Args:
            text: The text to analyze
        """
        self.text = text
        self._words_cache: Optional[List[str]] = None

    @property
    def _words(self) -> List[str]:
        """Cached word list."""
        if self._words_cache is None:
            self._words_cache = re.findall(r"\b\w+\b", self.text)
        return self._words_cache

    def detect(self) -> Dict[str, any]:
        """
        Detect the language of the text using simple heuristics.

        Note: This is a basic implementation. For production use, consider
        using libraries like langdetect or langid.

        Returns:
            Dictionary with detected language, confidence, and method

        Examples:
            >>> analyzer = LanguageAnalyzer("Hello world")
            >>> result = analyzer.detect()
            >>> result['language']
            'en'
        """
        if not self._words:
            return {"language": "unknown", "confidence": 0.0, "method": "heuristic"}

        # Convert text to lowercase words
        text_words = [word.lower() for word in self._words]
        word_set = set(text_words)

        # Count matches for each language
        language_scores = {}
        for lang, common_words in self.LANGUAGE_PATTERNS.items():
            matches = sum(1 for word in common_words if word in word_set)
            language_scores[lang] = matches

        # Find language with most matches
        if max(language_scores.values()) == 0:
            return {"language": "unknown", "confidence": 0.0, "method": "heuristic"}

        detected_lang = max(language_scores, key=language_scores.get)
        confidence = language_scores[detected_lang] / len(
            self.LANGUAGE_PATTERNS[detected_lang]
        )

        return {
            "language": detected_lang,
            "confidence": round(confidence, 2),
            "method": "heuristic",
        }

    def get_language_code(self) -> str:
        """
        Get the ISO 639-1 language code.

        Returns:
            Two-letter language code or 'unknown'

        Examples:
            >>> analyzer = LanguageAnalyzer("The quick brown fox")
            >>> analyzer.get_language_code()
            'en'
        """
        result = self.detect()
        return result["language"]

    def get_language_name(self) -> str:
        """
        Get the full language name.

        Returns:
            Full language name

        Examples:
            >>> analyzer = LanguageAnalyzer("Bonjour le monde")
            >>> analyzer.get_language_name()
            'French'
        """
        language_names = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "unknown": "Unknown",
        }

        code = self.get_language_code()
        return language_names.get(code, "Unknown")

    def get_confidence(self) -> float:
        """
        Get the confidence score of language detection.

        Returns:
            Confidence score (0.0 to 1.0)

        Examples:
            >>> analyzer = LanguageAnalyzer("Hello world")
            >>> confidence = analyzer.get_confidence()
            >>> 0 <= confidence <= 1
            True
        """
        result = self.detect()
        return result["confidence"]

    def is_likely_language(self, language_code: str, threshold: float = 0.3) -> bool:
        """
        Check if text is likely in a specific language.

        Args:
            language_code: ISO 639-1 language code (e.g., 'en', 'es')
            threshold: Minimum confidence threshold (default: 0.3)

        Returns:
            True if detected language matches and confidence is above threshold

        Examples:
            >>> analyzer = LanguageAnalyzer("The quick brown fox jumps")
            >>> analyzer.is_likely_language('en')
            True
        """
        result = self.detect()
        return result["language"] == language_code and result["confidence"] >= threshold
