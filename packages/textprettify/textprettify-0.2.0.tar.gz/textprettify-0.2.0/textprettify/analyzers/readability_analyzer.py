"""
Readability analysis functionality for TextPrettify.
"""

import re
from typing import Dict, List, Optional


class ReadabilityAnalyzer:
    """
    Analyzer for text readability metrics.

    Provides methods for calculating readability scores like Flesch Reading Ease
    and Flesch-Kincaid Grade Level.
    """

    def __init__(self, text: str):
        """
        Initialize the ReadabilityAnalyzer with input text.

        Args:
            text: The text to analyze
        """
        self.text = text
        self._words_cache: Optional[List[str]] = None
        self._sentences_cache: Optional[List[str]] = None

    @property
    def _words(self) -> List[str]:
        """Cached word list."""
        if self._words_cache is None:
            self._words_cache = re.findall(r"\b\w+\b", self.text)
        return self._words_cache

    @property
    def _sentences(self) -> List[str]:
        """Cached sentence list."""
        if self._sentences_cache is None:
            sentences = re.split(r"[.!?]+\s+|[.!?]+$", self.text)
            self._sentences_cache = [s.strip() for s in sentences if s.strip()]
        return self._sentences_cache

    def _count_syllables(self, word: str) -> int:
        """
        Count syllables in a word using a simple heuristic.

        Args:
            word: The word to count syllables in

        Returns:
            Estimated syllable count
        """
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e'
        if word.endswith("e"):
            syllable_count -= 1

        # Every word has at least one syllable
        if syllable_count == 0:
            syllable_count = 1

        return syllable_count

    def flesch_reading_ease(self) -> float:
        """
        Calculate Flesch Reading Ease score.

        Score interpretation:
        - 90-100: Very Easy
        - 80-89: Easy
        - 70-79: Fairly Easy
        - 60-69: Standard
        - 50-59: Fairly Difficult
        - 30-49: Difficult
        - 0-29: Very Confusing

        Returns:
            Flesch Reading Ease score

        Examples:
            >>> analyzer = ReadabilityAnalyzer("The cat sat on the mat.")
            >>> score = analyzer.flesch_reading_ease()
            >>> 0 <= score <= 100
            True
        """
        if not self._words or not self._sentences:
            return 0.0

        total_words = len(self._words)
        total_sentences = len(self._sentences)
        total_syllables = sum(self._count_syllables(word) for word in self._words)

        if total_words == 0 or total_sentences == 0:
            return 0.0

        score = (
            206.835
            - 1.015 * (total_words / total_sentences)
            - 84.6 * (total_syllables / total_words)
        )
        return float(round(max(0, min(100, score)), 2))

    def flesch_kincaid_grade(self) -> float:
        """
        Calculate Flesch-Kincaid Grade Level.

        Returns the US school grade level needed to understand the text.

        Returns:
            Grade level (e.g., 8.0 means 8th grade)

        Examples:
            >>> analyzer = ReadabilityAnalyzer("The cat sat on the mat.")
            >>> grade = analyzer.flesch_kincaid_grade()
            >>> grade >= 0
            True
        """
        if not self._words or not self._sentences:
            return 0.0

        total_words = len(self._words)
        total_sentences = len(self._sentences)
        total_syllables = sum(self._count_syllables(word) for word in self._words)

        if total_words == 0 or total_sentences == 0:
            return 0.0

        grade = (
            0.39 * (total_words / total_sentences)
            + 11.8 * (total_syllables / total_words)
            - 15.59
        )
        return float(round(max(0, grade), 2))

    def get_scores(self) -> Dict[str, float]:
        """
        Get all readability metrics.

        Returns:
            Dictionary with reading_ease and grade_level scores

        Examples:
            >>> analyzer = ReadabilityAnalyzer("Simple text here.")
            >>> scores = analyzer.get_scores()
            >>> 'reading_ease' in scores
            True
        """
        return {
            "reading_ease": self.flesch_reading_ease(),
            "grade_level": self.flesch_kincaid_grade(),
        }

    def interpret_reading_ease(self) -> str:
        """
        Get a human-readable interpretation of the Flesch Reading Ease score.

        Returns:
            Interpretation string

        Examples:
            >>> analyzer = ReadabilityAnalyzer("Simple text.")
            >>> interpretation = analyzer.interpret_reading_ease()
            >>> isinstance(interpretation, str)
            True
        """
        score = self.flesch_reading_ease()

        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Confusing"
