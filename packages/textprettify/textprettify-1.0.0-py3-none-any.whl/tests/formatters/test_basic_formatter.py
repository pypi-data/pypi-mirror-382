"""Tests for BasicFormatter class."""

from textprettify import BasicFormatter


class TestBasicFormatterInit:
    def test_initialization(self):
        formatter = BasicFormatter("Hello World")
        assert formatter.text == "Hello World"


class TestRemoveExtraWhitespace:
    def test_multiple_spaces(self):
        formatter = BasicFormatter("Hello    World")
        assert formatter.remove_extra_whitespace() == "Hello World"

    def test_leading_trailing_spaces(self):
        formatter = BasicFormatter("  Hello World  ")
        assert formatter.remove_extra_whitespace() == "Hello World"

    def test_newlines_and_tabs(self):
        formatter = BasicFormatter("Hello\n\n\tWorld")
        assert formatter.remove_extra_whitespace() == "Hello World"

    def test_empty_string(self):
        formatter = BasicFormatter("")
        assert formatter.remove_extra_whitespace() == ""


class TestSlugify:
    def test_basic_slugify(self):
        formatter = BasicFormatter("My Awesome Post!")
        assert formatter.slugify() == "my-awesome-post"

    def test_special_characters(self):
        formatter = BasicFormatter("Hello, World!")
        assert formatter.slugify() == "hello-world"

    def test_custom_separator(self):
        formatter = BasicFormatter("Hello World")
        assert formatter.slugify(separator="_") == "hello_world"

    def test_no_lowercase(self):
        formatter = BasicFormatter("Hello World")
        assert formatter.slugify(lowercase=False) == "Hello-World"


class TestGetReadingTime:
    def test_short_text(self):
        text = "Hello world " * 50
        formatter = BasicFormatter(text)
        assert formatter.get_reading_time() == "1 min read"

    def test_longer_text(self):
        text = "Hello world " * 200
        formatter = BasicFormatter(text)
        assert formatter.get_reading_time() == "2 mins read"

    def test_without_unit(self):
        text = "Hello world " * 100
        formatter = BasicFormatter(text)
        assert formatter.get_reading_time(include_unit=False) == 1


class TestCapitalizeWords:
    def test_basic_capitalization(self):
        formatter = BasicFormatter("hello world")
        assert formatter.capitalize_words() == "Hello World"

    def test_with_exceptions(self):
        formatter = BasicFormatter("a tale of two cities")
        result = formatter.capitalize_words(exceptions=["a", "of"])
        assert result == "A Tale of Two Cities"


class TestTruncate:
    def test_no_truncation_needed(self):
        formatter = BasicFormatter("Short text")
        assert formatter.truncate(20) == "Short text"

    def test_truncate_whole_words(self):
        formatter = BasicFormatter("The quick brown fox jumps")
        result = formatter.truncate(15)
        assert len(result) <= 15
        assert result.endswith("...")


class TestRemovePunctuation:
    def test_basic_removal(self):
        formatter = BasicFormatter("Hello, World!")
        assert formatter.remove_punctuation() == "Hello World"

    def test_keep_specific_chars(self):
        formatter = BasicFormatter("user@example.com")
        assert formatter.remove_punctuation(keep="@.") == "user@example.com"


class TestCountWords:
    def test_basic_count(self):
        formatter = BasicFormatter("Hello world")
        assert formatter.count_words() == 2

    def test_unique_count(self):
        formatter = BasicFormatter("Hello world hello")
        assert formatter.count_words(unique=True) == 2
