"""
Basic text formatting functionality for TextPrettify.
"""

import re
import string
from typing import Optional


class BasicFormatter:
    """
    Formatter for basic text cleaning and formatting operations.

    Provides methods for whitespace removal, slugification, capitalization,
    truncation, punctuation removal, and word counting.
    """

    def __init__(self, text: str):
        """
        Initialize the BasicFormatter with input text.

        Args:
            text: The text to format
        """
        self.text = text

    def remove_extra_whitespace(self) -> str:
        """
        Remove extra whitespace from text.

        Returns:
            Text with normalized whitespace

        Examples:
            >>> formatter = BasicFormatter("  Hello    World  ")
            >>> formatter.remove_extra_whitespace()
            'Hello World'
        """
        text = re.sub(r"\s+", " ", self.text)
        return text.strip()

    def slugify(self, separator: str = "-", lowercase: bool = True) -> str:
        """
        Convert text to a URL-friendly slug.

        Args:
            separator: Character to use as separator (default: '-')
            lowercase: Convert to lowercase (default: True)

        Returns:
            URL-friendly slug

        Examples:
            >>> formatter = BasicFormatter("My Awesome Post!")
            >>> formatter.slugify()
            'my-awesome-post'
        """
        text = self.text

        if lowercase:
            text = text.lower()

        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", separator, text)
        text = text.strip(separator)

        return text

    def get_reading_time(
        self, words_per_minute: int = 200, include_unit: bool = True
    ) -> str | int:
        """
        Calculate estimated reading time for text.

        Args:
            words_per_minute: Average reading speed (default: 200)
            include_unit: Return formatted string with unit (default: True)

        Returns:
            Reading time as formatted string or integer (minutes)

        Examples:
            >>> formatter = BasicFormatter("Hello world " * 100)
            >>> formatter.get_reading_time()
            '1 min read'
        """
        word_count = len(self.text.split())
        reading_time = max(1, round(word_count / words_per_minute))

        if include_unit:
            unit = "min" if reading_time == 1 else "mins"
            return f"{reading_time} {unit} read"

        return reading_time

    def capitalize_words(self, exceptions: Optional[list[str]] = None) -> str:
        """
        Capitalize the first letter of each word (title case).

        Args:
            exceptions: List of words to keep lowercase

        Returns:
            Text with capitalized words

        Examples:
            >>> formatter = BasicFormatter("the quick brown fox")
            >>> formatter.capitalize_words()
            'The Quick Brown Fox'
        """
        if exceptions is None:
            exceptions = []

        words = self.text.split()
        capitalized = []

        for i, word in enumerate(words):
            if i == 0 or word.lower() not in exceptions:
                capitalized.append(word.capitalize())
            else:
                capitalized.append(word.lower())

        return " ".join(capitalized)

    def truncate(
        self, max_length: int, suffix: str = "...", whole_words: bool = True
    ) -> str:
        """
        Truncate text to a maximum length.

        Args:
            max_length: Maximum length of output text
            suffix: String to append to truncated text (default: '...')
            whole_words: Only break at word boundaries (default: True)

        Returns:
            Truncated text

        Examples:
            >>> formatter = BasicFormatter("The quick brown fox jumps")
            >>> formatter.truncate(15)
            'The quick...'
        """
        if len(self.text) <= max_length:
            return self.text

        truncate_at = max_length - len(suffix)

        if whole_words:
            truncate_at = self.text.rfind(" ", 0, truncate_at)
            if truncate_at == -1:
                truncate_at = max_length - len(suffix)

        return self.text[:truncate_at].rstrip() + suffix

    def remove_punctuation(self, keep: Optional[str] = None) -> str:
        """
        Remove punctuation from text.

        Args:
            keep: Optional string of punctuation characters to keep

        Returns:
            Text without punctuation

        Examples:
            >>> formatter = BasicFormatter("Hello, World!")
            >>> formatter.remove_punctuation()
            'Hello World'
        """
        if keep:
            punctuation_to_remove = "".join(
                c for c in string.punctuation if c not in keep
            )
            translator = str.maketrans("", "", punctuation_to_remove)
        else:
            translator = str.maketrans("", "", string.punctuation)

        return self.text.translate(translator)

    def count_words(self, unique: bool = False) -> int:
        """
        Count words in text.

        Args:
            unique: Count only unique words (default: False)

        Returns:
            Word count

        Examples:
            >>> formatter = BasicFormatter("Hello world hello")
            >>> formatter.count_words()
            3
            >>> formatter.count_words(unique=True)
            2
        """
        words = self.text.lower().split()

        if unique:
            return len(set(words))

        return len(words)
