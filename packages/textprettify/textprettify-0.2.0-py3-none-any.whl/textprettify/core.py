"""
Core text manipulation functions for TextPrettify.
"""

import re
import string
from typing import Optional


def remove_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace from text, including leading/trailing spaces
    and multiple consecutive spaces.

    Args:
        text: The input text to clean

    Returns:
        Text with normalized whitespace

    Examples:
        >>> remove_extra_whitespace("  Hello    World  ")
        'Hello World'
        >>> remove_extra_whitespace("Multiple\\n\\n\\nlines")
        'Multiple lines'
    """
    # Replace multiple whitespace characters with a single space
    text = re.sub(r"\s+", " ", text)
    # Remove leading and trailing whitespace
    return text.strip()


def slugify(text: str, separator: str = "-", lowercase: bool = True) -> str:
    """
    Convert text to a URL-friendly slug.

    Args:
        text: The input text to slugify
        separator: Character to use as separator (default: '-')
        lowercase: Convert to lowercase (default: True)

    Returns:
        URL-friendly slug

    Examples:
        >>> slugify("My Awesome Post!")
        'my-awesome-post'
        >>> slugify("Hello, World!", separator='_')
        'hello_world'
        >>> slugify("Python 3.9 Release", lowercase=False)
        'Python-3-9-Release'
    """
    # Convert to lowercase if requested
    if lowercase:
        text = text.lower()

    # Replace spaces and non-alphanumeric characters with separator
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", separator, text)

    # Remove leading/trailing separators
    text = text.strip(separator)

    return text


def get_reading_time(
    text: str, words_per_minute: int = 200, include_unit: bool = True
) -> str | int:
    """
    Calculate estimated reading time for text.

    Args:
        text: The input text to analyze
        words_per_minute: Average reading speed (default: 200)
        include_unit: Return formatted string with unit (default: True)

    Returns:
        Reading time as formatted string or integer (minutes)

    Examples:
        >>> get_reading_time("Hello world " * 100)
        '1 min read'
        >>> get_reading_time("Hello world " * 100, include_unit=False)
        1
    """
    # Count words
    word_count = len(text.split())

    # Calculate reading time in minutes
    reading_time = max(1, round(word_count / words_per_minute))

    if include_unit:
        unit = "min" if reading_time == 1 else "mins"
        return f"{reading_time} {unit} read"

    return reading_time


def capitalize_words(text: str, exceptions: Optional[list[str]] = None) -> str:
    """
    Capitalize the first letter of each word (title case).

    Args:
        text: The input text to capitalize
        exceptions: List of words to keep lowercase (e.g., ['a', 'the', 'of'])

    Returns:
        Text with capitalized words

    Examples:
        >>> capitalize_words("the quick brown fox")
        'The Quick Brown Fox'
        >>> capitalize_words("a tale of two cities", exceptions=['a', 'of'])
        'A Tale of Two Cities'
    """
    if exceptions is None:
        exceptions = []

    words = text.split()
    capitalized = []

    for i, word in enumerate(words):
        # Always capitalize first word
        if i == 0 or word.lower() not in exceptions:
            capitalized.append(word.capitalize())
        else:
            capitalized.append(word.lower())

    return " ".join(capitalized)


def truncate_text(
    text: str, max_length: int, suffix: str = "...", whole_words: bool = True
) -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: The input text to truncate
        max_length: Maximum length of output text
        suffix: String to append to truncated text (default: '...')
        whole_words: Only break at word boundaries (default: True)

    Returns:
        Truncated text

    Examples:
        >>> truncate_text("The quick brown fox jumps", 15)
        'The quick...'
        >>> truncate_text("The quick brown fox jumps", 15, whole_words=False)
        'The quick br...'
    """
    if len(text) <= max_length:
        return text

    # Account for suffix length
    truncate_at = max_length - len(suffix)

    if whole_words:
        # Find the last space before truncate point
        truncate_at = text.rfind(" ", 0, truncate_at)
        if truncate_at == -1:
            truncate_at = max_length - len(suffix)

    return text[:truncate_at].rstrip() + suffix


def remove_punctuation(text: str, keep: Optional[str] = None) -> str:
    """
    Remove punctuation from text.

    Args:
        text: The input text to clean
        keep: Optional string of punctuation characters to keep

    Returns:
        Text without punctuation

    Examples:
        >>> remove_punctuation("Hello, World!")
        'Hello World'
        >>> remove_punctuation("user@example.com", keep='@.')
        'user@example.com'
    """
    if keep:
        # Create translation table excluding characters to keep
        punctuation_to_remove = "".join(c for c in string.punctuation if c not in keep)
        translator = str.maketrans("", "", punctuation_to_remove)
    else:
        translator = str.maketrans("", "", string.punctuation)

    return text.translate(translator)


def count_words(text: str, unique: bool = False) -> int:
    """
    Count words in text.

    Args:
        text: The input text to analyze
        unique: Count only unique words (default: False)

    Returns:
        Word count

    Examples:
        >>> count_words("Hello world hello")
        3
        >>> count_words("Hello world hello", unique=True)
        2
    """
    words = text.lower().split()

    if unique:
        return len(set(words))

    return len(words)
