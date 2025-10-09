"""Tests for LanguageAnalyzer class."""

from textprettify import LanguageAnalyzer


class TestLanguageDetection:
    def test_detect_english(self):
        analyzer = LanguageAnalyzer("The quick brown fox jumps over the lazy dog")
        result = analyzer.detect()
        assert result["language"] == "en"
        assert result["confidence"] > 0

    def test_detect_unknown(self):
        analyzer = LanguageAnalyzer("xyz abc def")
        result = analyzer.detect()
        assert "language" in result
        assert "confidence" in result
        assert "method" in result

    def test_get_language_code(self):
        analyzer = LanguageAnalyzer("The quick brown fox")
        code = analyzer.get_language_code()
        assert code == "en"

    def test_get_language_name(self):
        analyzer = LanguageAnalyzer("The quick brown fox")
        name = analyzer.get_language_name()
        assert name == "English"

    def test_get_confidence(self):
        analyzer = LanguageAnalyzer("Hello world")
        confidence = analyzer.get_confidence()
        assert isinstance(confidence, float)
        assert confidence >= 0
        assert confidence <= 1

    def test_is_likely_language(self):
        analyzer = LanguageAnalyzer("The quick brown fox jumps over the lazy dog")
        assert analyzer.is_likely_language("en", threshold=0.1) is True
        assert analyzer.is_likely_language("es", threshold=0.1) is False

    def test_empty_text(self):
        analyzer = LanguageAnalyzer("")
        result = analyzer.detect()
        assert result["language"] == "unknown"
        assert result["confidence"] == 0.0
