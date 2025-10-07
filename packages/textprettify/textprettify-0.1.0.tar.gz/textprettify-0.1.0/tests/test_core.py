"""
Unit tests for core text manipulation functions.
"""

import unittest
from textprettify import (
    remove_extra_whitespace,
    slugify,
    get_reading_time,
    capitalize_words,
    truncate_text,
    remove_punctuation,
    count_words,
)


class TestRemoveExtraWhitespace(unittest.TestCase):
    def test_multiple_spaces(self):
        self.assertEqual(remove_extra_whitespace("Hello    World"), "Hello World")

    def test_leading_trailing_spaces(self):
        self.assertEqual(remove_extra_whitespace("  Hello World  "), "Hello World")

    def test_newlines_and_tabs(self):
        self.assertEqual(remove_extra_whitespace("Hello\n\n\tWorld"), "Hello World")

    def test_empty_string(self):
        self.assertEqual(remove_extra_whitespace(""), "")

    def test_single_word(self):
        self.assertEqual(remove_extra_whitespace("  Hello  "), "Hello")


class TestSlugify(unittest.TestCase):
    def test_basic_slugify(self):
        self.assertEqual(slugify("My Awesome Post!"), "my-awesome-post")

    def test_special_characters(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")

    def test_custom_separator(self):
        self.assertEqual(slugify("Hello World", separator='_'), "hello_world")

    def test_no_lowercase(self):
        self.assertEqual(slugify("Hello World", lowercase=False), "Hello-World")

    def test_numbers(self):
        self.assertEqual(slugify("Python 3.9 Release"), "python-3-9-release")

    def test_unicode_removal(self):
        self.assertEqual(slugify("Café ☕ Time"), "caf-time")


class TestGetReadingTime(unittest.TestCase):
    def test_short_text(self):
        text = "Hello world " * 50  # 100 words
        self.assertEqual(get_reading_time(text), "1 min read")

    def test_longer_text(self):
        text = "Hello world " * 200  # 400 words
        self.assertEqual(get_reading_time(text), "2 mins read")

    def test_without_unit(self):
        text = "Hello world " * 100
        self.assertEqual(get_reading_time(text, include_unit=False), 1)

    def test_custom_wpm(self):
        text = "Hello world " * 50  # 100 words
        self.assertEqual(get_reading_time(text, words_per_minute=100), "1 min read")

    def test_minimum_reading_time(self):
        text = "Hello"
        self.assertEqual(get_reading_time(text, include_unit=False), 1)


class TestCapitalizeWords(unittest.TestCase):
    def test_basic_capitalization(self):
        self.assertEqual(capitalize_words("hello world"), "Hello World")

    def test_with_exceptions(self):
        result = capitalize_words("a tale of two cities", exceptions=['a', 'of'])
        self.assertEqual(result, "A Tale of Two Cities")

    def test_first_word_always_capitalized(self):
        result = capitalize_words("the quick brown fox", exceptions=['the'])
        self.assertEqual(result, "The Quick Brown Fox")

    def test_empty_string(self):
        self.assertEqual(capitalize_words(""), "")


class TestTruncateText(unittest.TestCase):
    def test_no_truncation_needed(self):
        text = "Short text"
        self.assertEqual(truncate_text(text, 20), "Short text")

    def test_truncate_whole_words(self):
        text = "The quick brown fox jumps over the lazy dog"
        result = truncate_text(text, 20)
        self.assertTrue(len(result) <= 20)
        self.assertTrue(result.endswith("..."))

    def test_truncate_no_whole_words(self):
        text = "The quick brown fox"
        result = truncate_text(text, 15, whole_words=False)
        self.assertEqual(result, "The quick b...")

    def test_custom_suffix(self):
        text = "The quick brown fox jumps"
        result = truncate_text(text, 15, suffix='...')
        self.assertTrue(result.endswith("..."))


class TestRemovePunctuation(unittest.TestCase):
    def test_basic_removal(self):
        self.assertEqual(remove_punctuation("Hello, World!"), "Hello World")

    def test_keep_specific_chars(self):
        self.assertEqual(
            remove_punctuation("user@example.com", keep='@.'),
            "user@example.com"
        )

    def test_multiple_punctuation(self):
        self.assertEqual(
            remove_punctuation("Wow!!! Amazing..."),
            "Wow Amazing"
        )

    def test_no_punctuation(self):
        self.assertEqual(remove_punctuation("Hello World"), "Hello World")


class TestCountWords(unittest.TestCase):
    def test_basic_count(self):
        self.assertEqual(count_words("Hello world"), 2)

    def test_unique_count(self):
        self.assertEqual(count_words("Hello world hello", unique=True), 2)

    def test_non_unique_count(self):
        self.assertEqual(count_words("Hello world hello", unique=False), 3)

    def test_empty_string(self):
        self.assertEqual(count_words(""), 0)


if __name__ == '__main__':
    unittest.main()
