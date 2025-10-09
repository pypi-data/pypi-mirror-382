"""
Statistical analysis functionality for TextPrettify.
"""

import re
from typing import Dict, List, Optional
from collections import Counter


class StatisticsAnalyzer:
    """
    Analyzer for text statistics and word analysis.

    Provides methods for analyzing word counts, lengths, frequencies, and more.
    """

    def __init__(self, text: str):
        """
        Initialize the StatisticsAnalyzer with input text.

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

    def word_count(self) -> int:
        """
        Get total word count.

        Returns:
            Number of words

        Examples:
            >>> analyzer = StatisticsAnalyzer("Hello world from Python")
            >>> analyzer.word_count()
            4
        """
        return len(self._words)

    def unique_word_count(self) -> int:
        """
        Get count of unique words (case-insensitive).

        Returns:
            Number of unique words

        Examples:
            >>> analyzer = StatisticsAnalyzer("Hello world hello")
            >>> analyzer.unique_word_count()
            2
        """
        return len(set(word.lower() for word in self._words))

    def average_word_length(self) -> float:
        """
        Calculate average word length.

        Returns:
            Average number of characters per word

        Examples:
            >>> analyzer = StatisticsAnalyzer("Hi hello")
            >>> analyzer.average_word_length()
            3.5
        """
        if not self._words:
            return 0.0

        total_chars = sum(len(word) for word in self._words)
        return round(total_chars / len(self._words), 2)

    def longest_word(self) -> str:
        """
        Find the longest word in the text.

        Returns:
            The longest word (first occurrence if multiple)

        Examples:
            >>> analyzer = StatisticsAnalyzer("Short lengthy word")
            >>> analyzer.longest_word()
            'lengthy'
        """
        if not self._words:
            return ""

        return max(self._words, key=len)

    def shortest_word(self) -> str:
        """
        Find the shortest word in the text.

        Returns:
            The shortest word (first occurrence if multiple)

        Examples:
            >>> analyzer = StatisticsAnalyzer("I am happy")
            >>> analyzer.shortest_word()
            'I'
        """
        if not self._words:
            return ""

        return min(self._words, key=len)

    def word_frequency(
        self, top_n: Optional[int] = None, case_sensitive: bool = False
    ) -> Dict[str, int]:
        """
        Get word frequency distribution.

        Args:
            top_n: Return only the top N most common words (None for all)
            case_sensitive: Use case-sensitive counting (default: False)

        Returns:
            Dictionary of words and their frequencies

        Examples:
            >>> analyzer = StatisticsAnalyzer("hello world hello")
            >>> analyzer.word_frequency()
            {'hello': 2, 'world': 1}
        """
        if case_sensitive:
            words = self._words
        else:
            words = [word.lower() for word in self._words]

        word_counts = Counter(words)

        if top_n is not None:
            return dict(word_counts.most_common(top_n))

        return dict(word_counts)

    def word_length_distribution(self) -> Dict[int, int]:
        """
        Get distribution of word lengths.

        Returns:
            Dictionary mapping word length to count of words with that length

        Examples:
            >>> analyzer = StatisticsAnalyzer("I am happy")
            >>> dist = analyzer.word_length_distribution()
            >>> dist[1]
            1
        """
        length_counts = Counter(len(word) for word in self._words)
        return dict(sorted(length_counts.items()))

    def lexical_diversity(self) -> float:
        """
        Calculate lexical diversity (unique words / total words).

        Returns:
            Lexical diversity ratio (0.0 to 1.0)

        Examples:
            >>> analyzer = StatisticsAnalyzer("hello world hello")
            >>> diversity = analyzer.lexical_diversity()
            >>> 0 <= diversity <= 1
            True
        """
        if not self._words:
            return 0.0

        unique_count = self.unique_word_count()
        total_count = self.word_count()

        return round(unique_count / total_count, 3)

    def get_statistics(self) -> Dict[str, any]:
        """
        Get comprehensive text statistics.

        Returns:
            Dictionary with various text statistics

        Examples:
            >>> analyzer = StatisticsAnalyzer("Hello world")
            >>> stats = analyzer.get_statistics()
            >>> stats['word_count']
            2
        """
        return {
            "word_count": self.word_count(),
            "unique_word_count": self.unique_word_count(),
            "average_word_length": self.average_word_length(),
            "longest_word": self.longest_word(),
            "shortest_word": self.shortest_word(),
            "lexical_diversity": self.lexical_diversity(),
        }
