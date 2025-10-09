"""Tests for NormalizationFormatter class."""

from textprettify import NormalizationFormatter


class TestUnicodeNormalization:
    def test_normalize_unicode(self):
        formatter = NormalizationFormatter("café")
        result = formatter.normalize_unicode("NFC")
        assert isinstance(result, str)

    def test_remove_accents(self):
        formatter = NormalizationFormatter("café résumé")
        assert formatter.remove_accents() == "cafe resume"

    def test_remove_accents_naive(self):
        formatter = NormalizationFormatter("naïve")
        assert formatter.remove_accents() == "naive"

    def test_remove_accents_no_accents(self):
        formatter = NormalizationFormatter("hello world")
        assert formatter.remove_accents() == "hello world"


class TestSmartQuotes:
    def test_to_smart_quotes_double(self):
        formatter = NormalizationFormatter('"Hello World"')
        result = formatter.to_smart_quotes()
        assert '"' in result
        assert '"' in result

    def test_to_straight_quotes_double(self):
        formatter = NormalizationFormatter('"Hello World"')
        result = formatter.to_straight_quotes()
        assert result.count('"') == 2

    def test_to_straight_quotes_single(self):
        formatter = NormalizationFormatter("'Hello World'")
        result = formatter.to_straight_quotes()
        assert result.count("'") == 2
