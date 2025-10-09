"""
Text normalization formatting functionality for TextPrettify.
"""

import re
import unicodedata


class NormalizationFormatter:
    """
    Formatter for text normalization operations.

    Provides methods for Unicode normalization, accent removal,
    and smart quotes conversion.
    """

    def __init__(self, text: str):
        """
        Initialize the NormalizationFormatter with input text.

        Args:
            text: The text to normalize
        """
        self.text = text

    # Unicode Normalization

    def normalize_unicode(self, form: str = "NFC") -> str:
        """
        Normalize Unicode text.

        Args:
            form: Normalization form ('NFC', 'NFD', 'NFKC', 'NFKD')

        Returns:
            Normalized Unicode text

        Examples:
            >>> formatter = NormalizationFormatter("café")
            >>> formatter.normalize_unicode('NFD')
            'café'
        """
        return unicodedata.normalize(form, self.text)

    def remove_accents(self) -> str:
        """
        Remove accents and diacritical marks from text.

        Returns:
            Text without accents

        Examples:
            >>> formatter = NormalizationFormatter("café résumé")
            >>> formatter.remove_accents()
            'cafe resume'
        """
        nfd = unicodedata.normalize("NFD", self.text)
        return "".join(char for char in nfd if unicodedata.category(char) != "Mn")

    # Smart Quotes Conversion

    def to_smart_quotes(self) -> str:
        """
        Convert straight quotes to smart/curly quotes.

        Returns:
            Text with smart quotes

        Examples:
            >>> formatter = NormalizationFormatter('"Hello"')
            >>> formatter.to_smart_quotes()
            '"Hello"'
        """
        text = self.text

        # Opening double quote
        text = re.sub(r'(^|\s)"', r'\1"', text)
        # Closing double quote
        text = re.sub(r'"', r'"', text)

        # Opening single quote
        text = re.sub(r"(^|\s)'", r"\1'", text)
        # Apostrophe or closing single quote
        text = re.sub(r"'", r"'", text)

        return text

    def to_straight_quotes(self) -> str:
        """
        Convert smart/curly quotes to straight quotes.

        Returns:
            Text with straight quotes

        Examples:
            >>> formatter = NormalizationFormatter('"Hello"')
            >>> formatter.to_straight_quotes()
            '"Hello"'
        """
        text = self.text

        # Convert smart double quotes to straight
        text = text.replace('"', '"').replace('"', '"')

        # Convert smart single quotes to straight
        text = text.replace(""", "'").replace(""", "'")

        return text
