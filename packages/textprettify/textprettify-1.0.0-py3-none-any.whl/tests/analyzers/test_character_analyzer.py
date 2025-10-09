"""Tests for CharacterAnalyzer class."""

from textprettify import CharacterAnalyzer


class TestCharacterCounts:
    def test_count_total(self):
        analyzer = CharacterAnalyzer("Hello, World!")
        assert analyzer.count_total() == 13

    def test_count_no_spaces(self):
        analyzer = CharacterAnalyzer("Hello, World!")
        assert analyzer.count_no_spaces() == 12

    def test_count_alphanumeric(self):
        analyzer = CharacterAnalyzer("Hello, World! 123")
        assert analyzer.count_alphanumeric() == 13

    def test_count_letters(self):
        analyzer = CharacterAnalyzer("Hello123")
        assert analyzer.count_letters() == 5

    def test_count_digits(self):
        analyzer = CharacterAnalyzer("Hello123")
        assert analyzer.count_digits() == 3

    def test_count_spaces(self):
        analyzer = CharacterAnalyzer("Hello World")
        assert analyzer.count_spaces() == 1

    def test_count_punctuation(self):
        analyzer = CharacterAnalyzer("Hello, World!")
        assert analyzer.count_punctuation() == 2

    def test_get_all_counts(self):
        analyzer = CharacterAnalyzer("Hello!")
        counts = analyzer.get_all_counts()
        assert counts["total"] == 6
        assert counts["alphanumeric"] == 5
        assert "letters" in counts
        assert "digits" in counts
        assert "punctuation" in counts
