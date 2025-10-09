"""Tests for TransformationFormatter class."""

from textprettify import TransformationFormatter


class TestTextReversal:
    def test_reverse_characters(self):
        formatter = TransformationFormatter("Hello World")
        assert formatter.reverse_characters() == "dlroW olleH"

    def test_reverse_words(self):
        formatter = TransformationFormatter("Hello World Python")
        assert formatter.reverse_words() == "Python World Hello"


class TestLetterSpacing:
    def test_default_spacing(self):
        formatter = TransformationFormatter("Hello")
        assert formatter.add_letter_spacing() == "H e l l o"

    def test_custom_spacing(self):
        formatter = TransformationFormatter("Hello")
        assert formatter.add_letter_spacing("-") == "H-e-l-l-o"


class TestLineOperations:
    def test_remove_blank_lines(self):
        formatter = TransformationFormatter("Line 1\n\nLine 2\n\n\nLine 3")
        result = formatter.remove_blank_lines()
        assert result == "Line 1\nLine 2\nLine 3"

    def test_deduplicate_lines(self):
        formatter = TransformationFormatter("apple\nbanana\napple\ncherry")
        result = formatter.deduplicate_lines()
        assert result == "apple\nbanana\ncherry"

    def test_sort_lines(self):
        formatter = TransformationFormatter("zebra\napple\nbanana")
        result = formatter.sort_lines()
        assert result == "apple\nbanana\nzebra"

    def test_sort_lines_reverse(self):
        formatter = TransformationFormatter("apple\nbanana\nzebra")
        result = formatter.sort_lines(reverse=True)
        assert result == "zebra\nbanana\napple"


class TestFindAndReplace:
    def test_basic_replace(self):
        formatter = TransformationFormatter("Hello World, Hello Python")
        result = formatter.find_and_replace("Hello", "Hi")
        assert result == "Hi World, Hi Python"

    def test_case_insensitive_replace(self):
        formatter = TransformationFormatter("Hello World, hello Python")
        result = formatter.find_and_replace("hello", "Hi", case_sensitive=False)
        assert result == "Hi World, Hi Python"

    def test_regex_replace(self):
        formatter = TransformationFormatter("I have 5 apples and 10 oranges")
        result = formatter.find_and_replace(r"\d+", "X", regex=True)
        assert result == "I have X apples and X oranges"


class TestHighlighting:
    def test_highlight_markdown_bold(self):
        formatter = TransformationFormatter("Hello world")
        result = formatter.highlight_markdown(["Hello"], "bold")
        assert "**Hello**" in result

    def test_highlight_html_strong(self):
        formatter = TransformationFormatter("Hello world")
        result = formatter.highlight_html(["Hello"], "strong")
        assert result == "<strong>Hello</strong> world"


class TestAcronymExtraction:
    def test_extract_acronyms(self):
        formatter = TransformationFormatter("NASA and FBI are USA organizations")
        acronyms = formatter.extract_acronyms()
        assert "NASA" in acronyms
        assert "FBI" in acronyms
        assert "USA" in acronyms


class TestTextWrapping:
    def test_wrap_text(self):
        long_text = "This is a very long sentence that should be wrapped"
        formatter = TransformationFormatter(long_text)
        wrapped = formatter.wrap_text(width=30)
        lines = wrapped.split("\n")
        for line in lines:
            assert len(line) <= 30
