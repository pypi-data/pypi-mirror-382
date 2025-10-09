"""
Sentence analysis functionality for TextPrettify.
"""

import re
from typing import Dict, List, Optional


class SentenceAnalyzer:
    """
    Analyzer for sentence-level text analysis.

    Provides methods for analyzing sentences, their structure, and properties.
    """

    def __init__(self, text: str):
        """
        Initialize the SentenceAnalyzer with input text.

        Args:
            text: The text to analyze
        """
        self.text = text
        self._sentences_cache: Optional[List[str]] = None

    @property
    def sentences(self) -> List[str]:
        """Cached sentence list."""
        if self._sentences_cache is None:
            # Split on sentence-ending punctuation followed by space or end of string
            sentences = re.split(r"[.!?]+\s+|[.!?]+$", self.text)
            self._sentences_cache = [s.strip() for s in sentences if s.strip()]
        return self._sentences_cache

    def count(self) -> int:
        """
        Get the number of sentences in the text.

        Returns:
            Number of sentences

        Examples:
            >>> analyzer = SentenceAnalyzer("Hello. How are you? I'm fine!")
            >>> analyzer.count()
            3
        """
        return len(self.sentences)

    def extract(self) -> List[str]:
        """
        Extract all sentences from the text.

        Returns:
            List of sentences

        Examples:
            >>> analyzer = SentenceAnalyzer("Hello. How are you?")
            >>> analyzer.extract()
            ['Hello', 'How are you']
        """
        return self.sentences.copy()

    def average_length(self) -> float:
        """
        Calculate average sentence length in words.

        Returns:
            Average number of words per sentence

        Examples:
            >>> analyzer = SentenceAnalyzer("Hello world. How are you doing?")
            >>> analyzer.average_length()
            2.5
        """
        if not self.sentences:
            return 0.0

        total_words = sum(
            len(re.findall(r"\b\w+\b", sentence)) for sentence in self.sentences
        )
        return total_words / len(self.sentences)

    def longest_sentence(self) -> str:
        """
        Find the longest sentence in the text.

        Returns:
            The longest sentence

        Examples:
            >>> analyzer = SentenceAnalyzer("Hi. This is a longer sentence. Bye.")
            >>> analyzer.longest_sentence()
            'This is a longer sentence'
        """
        if not self.sentences:
            return ""

        return max(self.sentences, key=len)

    def shortest_sentence(self) -> str:
        """
        Find the shortest sentence in the text.

        Returns:
            The shortest sentence

        Examples:
            >>> analyzer = SentenceAnalyzer("Hi. This is longer. Bye.")
            >>> analyzer.shortest_sentence()
            'Hi'
        """
        if not self.sentences:
            return ""

        return min(self.sentences, key=len)

    def get_statistics(self) -> Dict[str, any]:
        """
        Get comprehensive sentence statistics.

        Returns:
            Dictionary with sentence statistics

        Examples:
            >>> analyzer = SentenceAnalyzer("Hi. Hello there.")
            >>> stats = analyzer.get_statistics()
            >>> stats['count']
            2
        """
        return {
            "count": self.count(),
            "average_length": round(self.average_length(), 2),
            "longest": self.longest_sentence(),
            "shortest": self.shortest_sentence(),
            "sentences": self.extract(),
        }
