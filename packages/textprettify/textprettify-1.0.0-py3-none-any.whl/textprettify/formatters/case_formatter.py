"""
Case conversion formatting functionality for TextPrettify.
"""

import re


class CaseFormatter:
    """
    Formatter for case conversion operations.

    Provides methods for converting text between different case formats
    like snake_case, camelCase, PascalCase, CONSTANT_CASE, and kebab-case.
    """

    def __init__(self, text: str):
        """
        Initialize the CaseFormatter with input text.

        Args:
            text: The text to format
        """
        self.text = text

    def to_snake_case(self) -> str:
        """
        Convert text to snake_case.

        Returns:
            Text in snake_case format

        Examples:
            >>> formatter = CaseFormatter("Hello World")
            >>> formatter.to_snake_case()
            'hello_world'
        """
        text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", self.text)
        text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
        text = re.sub(r"[-\s]+", "_", text)
        text = re.sub(r"[^\w]", "", text)
        text = re.sub(r"_+", "_", text)
        return text.lower()

    def to_camel_case(self) -> str:
        """
        Convert text to camelCase.

        Returns:
            Text in camelCase format

        Examples:
            >>> formatter = CaseFormatter("hello world")
            >>> formatter.to_camel_case()
            'helloWorld'
        """
        words = re.sub(r"[_\-\s]+", " ", self.text).split()
        if not words:
            return ""
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])

    def to_pascal_case(self) -> str:
        """
        Convert text to PascalCase.

        Returns:
            Text in PascalCase format

        Examples:
            >>> formatter = CaseFormatter("hello world")
            >>> formatter.to_pascal_case()
            'HelloWorld'
        """
        words = re.sub(r"[_\-\s]+", " ", self.text).split()
        return "".join(word.capitalize() for word in words)

    def to_constant_case(self) -> str:
        """
        Convert text to CONSTANT_CASE (screaming snake case).

        Returns:
            Text in CONSTANT_CASE format

        Examples:
            >>> formatter = CaseFormatter("hello world")
            >>> formatter.to_constant_case()
            'HELLO_WORLD'
        """
        return self.to_snake_case().upper()

    def to_kebab_case(self) -> str:
        """
        Convert text to kebab-case.

        Returns:
            Text in kebab-case format

        Examples:
            >>> formatter = CaseFormatter("Hello World")
            >>> formatter.to_kebab_case()
            'hello-world'
        """
        snake = self.to_snake_case()
        return snake.replace("_", "-")

    def to_title_case(self, exceptions: list[str] = None) -> str:
        """
        Convert text to Title Case.

        Args:
            exceptions: List of words to keep lowercase

        Returns:
            Text in Title Case

        Examples:
            >>> formatter = CaseFormatter("the lord of the rings")
            >>> formatter.to_title_case(exceptions=['the', 'of'])
            'The Lord of the Rings'
        """
        if exceptions is None:
            exceptions = []

        words = self.text.split()
        result = []

        for i, word in enumerate(words):
            if i == 0 or word.lower() not in exceptions:
                result.append(word.capitalize())
            else:
                result.append(word.lower())

        return " ".join(result)
