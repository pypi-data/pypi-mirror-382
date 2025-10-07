"""
TextPrettify - A mini-library for text cleaning and formatting.

Provides simple utilities to manipulate and format text strings.
"""

from .core import (
    remove_extra_whitespace,
    slugify,
    get_reading_time,
    capitalize_words,
    truncate_text,
    remove_punctuation,
    count_words,
)

__version__ = "0.1.0"
__all__ = [
    "remove_extra_whitespace",
    "slugify",
    "get_reading_time",
    "capitalize_words",
    "truncate_text",
    "remove_punctuation",
    "count_words",
]
