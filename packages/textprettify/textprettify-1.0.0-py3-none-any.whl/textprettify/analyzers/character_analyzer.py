"""
Character analysis functionality for TextPrettify.
"""

from typing import Dict


class CharacterAnalyzer:
    """
    Analyzer for character-level text analysis.

    Provides methods for counting characters in various ways.
    """

    def __init__(self, text: str):
        """
        Initialize the CharacterAnalyzer with input text.

        Args:
            text: The text to analyze
        """
        self.text = text

    def count_total(self) -> int:
        """
        Get total character count including spaces and punctuation.

        Returns:
            Total number of characters

        Examples:
            >>> analyzer = CharacterAnalyzer("Hello, World!")
            >>> analyzer.count_total()
            13
        """
        return len(self.text)

    def count_no_spaces(self) -> int:
        """
        Get character count excluding spaces.

        Returns:
            Number of characters without spaces

        Examples:
            >>> analyzer = CharacterAnalyzer("Hello, World!")
            >>> analyzer.count_no_spaces()
            12
        """
        return len([c for c in self.text if not c.isspace()])

    def count_alphanumeric(self) -> int:
        """
        Get count of alphanumeric characters only.

        Returns:
            Number of alphanumeric characters

        Examples:
            >>> analyzer = CharacterAnalyzer("Hello, World! 123")
            >>> analyzer.count_alphanumeric()
            13
        """
        return sum(1 for c in self.text if c.isalnum())

    def count_letters(self) -> int:
        """
        Get count of letter characters only.

        Returns:
            Number of letter characters

        Examples:
            >>> analyzer = CharacterAnalyzer("Hello123")
            >>> analyzer.count_letters()
            5
        """
        return sum(1 for c in self.text if c.isalpha())

    def count_digits(self) -> int:
        """
        Get count of digit characters.

        Returns:
            Number of digit characters

        Examples:
            >>> analyzer = CharacterAnalyzer("Hello123")
            >>> analyzer.count_digits()
            3
        """
        return sum(1 for c in self.text if c.isdigit())

    def count_spaces(self) -> int:
        """
        Get count of space characters.

        Returns:
            Number of space characters

        Examples:
            >>> analyzer = CharacterAnalyzer("Hello World")
            >>> analyzer.count_spaces()
            1
        """
        return self.text.count(" ")

    def count_punctuation(self) -> int:
        """
        Get count of punctuation characters.

        Returns:
            Number of punctuation characters

        Examples:
            >>> analyzer = CharacterAnalyzer("Hello, World!")
            >>> analyzer.count_punctuation()
            2
        """
        import string

        return sum(1 for c in self.text if c in string.punctuation)

    def get_all_counts(self) -> Dict[str, int]:
        """
        Get all character count metrics.

        Returns:
            Dictionary with all character counts

        Examples:
            >>> analyzer = CharacterAnalyzer("Hello!")
            >>> counts = analyzer.get_all_counts()
            >>> counts['total']
            6
        """
        return {
            "total": self.count_total(),
            "no_spaces": self.count_no_spaces(),
            "alphanumeric": self.count_alphanumeric(),
            "letters": self.count_letters(),
            "digits": self.count_digits(),
            "spaces": self.count_spaces(),
            "punctuation": self.count_punctuation(),
        }
