"""
Text transformation formatting functionality for TextPrettify.
"""

import re


class TransformationFormatter:
    """
    Formatter for text transformation operations.

    Provides methods for reversing text, adding spacing, highlighting,
    finding and replacing, and manipulating lines.
    """

    def __init__(self, text: str):
        """
        Initialize the TransformationFormatter with input text.

        Args:
            text: The text to transform
        """
        self.text = text

    # Text Reversal

    def reverse_characters(self) -> str:
        """
        Reverse the character order in the text.

        Returns:
            Text with characters in reverse order

        Examples:
            >>> formatter = TransformationFormatter("Hello World")
            >>> formatter.reverse_characters()
            'dlroW olleH'
        """
        return self.text[::-1]

    def reverse_words(self) -> str:
        """
        Reverse the word order in the text.

        Returns:
            Text with words in reverse order

        Examples:
            >>> formatter = TransformationFormatter("Hello World Python")
            >>> formatter.reverse_words()
            'Python World Hello'
        """
        words = self.text.split()
        return " ".join(reversed(words))

    # Letter Spacing

    def add_letter_spacing(self, spacing: str = " ") -> str:
        """
        Add spacing between each character.

        Args:
            spacing: String to insert between characters (default: single space)

        Returns:
            Text with spacing between characters

        Examples:
            >>> formatter = TransformationFormatter("Hello")
            >>> formatter.add_letter_spacing()
            'H e l l o'
        """
        return spacing.join(self.text)

    # Line Operations

    def remove_blank_lines(self) -> str:
        """
        Remove all blank lines from text.

        Returns:
            Text without blank lines

        Examples:
            >>> formatter = TransformationFormatter("Line 1\\n\\nLine 2\\n\\n\\nLine 3")
            >>> formatter.remove_blank_lines()
            'Line 1\\nLine 2\\nLine 3'
        """
        lines = self.text.split("\n")
        non_blank_lines = [line for line in lines if line.strip()]
        return "\n".join(non_blank_lines)

    def deduplicate_lines(self, preserve_order: bool = True) -> str:
        """
        Remove duplicate lines from text.

        Args:
            preserve_order: Keep original order of lines (default: True)

        Returns:
            Text with duplicate lines removed

        Examples:
            >>> formatter = TransformationFormatter("apple\\nbanana\\napple\\ncherry")
            >>> formatter.deduplicate_lines()
            'apple\\nbanana\\ncherry'
        """
        lines = self.text.split("\n")

        if preserve_order:
            seen = set()
            unique_lines = []
            for line in lines:
                if line not in seen:
                    seen.add(line)
                    unique_lines.append(line)
            return "\n".join(unique_lines)
        else:
            return "\n".join(list(set(lines)))

    def sort_lines(self, reverse: bool = False, case_sensitive: bool = False) -> str:
        """
        Sort lines alphabetically.

        Args:
            reverse: Sort in reverse order (default: False)
            case_sensitive: Use case-sensitive sorting (default: False)

        Returns:
            Text with sorted lines

        Examples:
            >>> formatter = TransformationFormatter("zebra\\napple\\nbanana")
            >>> formatter.sort_lines()
            'apple\\nbanana\\nzebra'
        """
        lines = self.text.split("\n")

        if case_sensitive:
            sorted_lines = sorted(lines, reverse=reverse)
        else:
            sorted_lines = sorted(lines, key=str.lower, reverse=reverse)

        return "\n".join(sorted_lines)

    # Find and Replace

    def find_and_replace(
        self,
        find: str,
        replace: str,
        regex: bool = False,
        case_sensitive: bool = True,
        count: int = 0,
    ) -> str:
        """
        Find and replace text with optional regex support.

        Args:
            find: Text or pattern to find
            replace: Replacement text
            regex: Use regex pattern matching (default: False)
            case_sensitive: Case-sensitive search (default: True)
            count: Maximum number of replacements (0 = all, default: 0)

        Returns:
            Text with replacements made

        Examples:
            >>> formatter = TransformationFormatter("Hello World, Hello Python")
            >>> formatter.find_and_replace("Hello", "Hi")
            'Hi World, Hi Python'
        """
        if regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.sub(find, replace, self.text, count=count, flags=flags)
        else:
            if not case_sensitive:
                pattern = re.compile(re.escape(find), re.IGNORECASE)
                return pattern.sub(replace, self.text, count=count)
            else:
                if count == 0:
                    return self.text.replace(find, replace)
                else:
                    return self.text.replace(find, replace, count)

    # Text Highlighting

    def highlight_markdown(self, words: list[str], style: str = "bold") -> str:
        """
        Highlight words using markdown formatting.

        Args:
            words: List of words to highlight
            style: Markdown style - 'bold', 'italic', 'code', or 'both'

        Returns:
            Text with markdown formatting applied

        Examples:
            >>> formatter = TransformationFormatter("Hello world")
            >>> formatter.highlight_markdown(['Hello'], 'bold')
            '**Hello** world'
        """
        text = self.text

        for word in words:
            pattern = re.compile(r"\b(" + re.escape(word) + r")\b", re.IGNORECASE)

            if style == "bold":
                text = pattern.sub(r"**\1**", text)
            elif style == "italic":
                text = pattern.sub(r"*\1*", text)
            elif style == "code":
                text = pattern.sub(r"`\1`", text)
            elif style == "both":
                text = pattern.sub(r"***\1***", text)

        return text

    def highlight_html(self, words: list[str], tag: str = "strong") -> str:
        """
        Highlight words using HTML tags.

        Args:
            words: List of words to highlight
            tag: HTML tag to use - 'strong', 'em', 'mark', 'code'

        Returns:
            Text with HTML tags applied

        Examples:
            >>> formatter = TransformationFormatter("Hello world")
            >>> formatter.highlight_html(['Hello'], 'strong')
            '<strong>Hello</strong> world'
        """
        text = self.text

        for word in words:
            pattern = re.compile(r"\b(" + re.escape(word) + r")\b", re.IGNORECASE)
            text = pattern.sub(rf"<{tag}>\1</{tag}>", text)

        return text

    # Acronym Extraction

    def extract_acronyms(self, min_length: int = 2, max_length: int = 10) -> list[str]:
        """
        Extract acronyms (uppercase words) from text.

        Args:
            min_length: Minimum acronym length (default: 2)
            max_length: Maximum acronym length (default: 10)

        Returns:
            List of unique acronyms found

        Examples:
            >>> formatter = TransformationFormatter("NASA and FBI are USA organizations")
            >>> acronyms = formatter.extract_acronyms()
            >>> 'NASA' in acronyms
            True
        """
        pattern = rf"\b[A-Z]{{{min_length},{max_length}}}\b"
        acronyms = re.findall(pattern, self.text)

        seen = set()
        unique_acronyms = []
        for acronym in acronyms:
            if acronym not in seen:
                seen.add(acronym)
                unique_acronyms.append(acronym)

        return unique_acronyms

    # Text Wrapping

    def wrap_text(self, width: int = 80, break_long_words: bool = True) -> str:
        """
        Wrap text to a specific line width.

        Args:
            width: Maximum line width (default: 80)
            break_long_words: Break words longer than width (default: True)

        Returns:
            Text wrapped to specified width

        Examples:
            >>> formatter = TransformationFormatter("This is a very long sentence")
            >>> wrapped = formatter.wrap_text(20)
            >>> all(len(line) <= 20 for line in wrapped.split('\\n'))
            True
        """
        import textwrap

        return textwrap.fill(self.text, width=width, break_long_words=break_long_words)
