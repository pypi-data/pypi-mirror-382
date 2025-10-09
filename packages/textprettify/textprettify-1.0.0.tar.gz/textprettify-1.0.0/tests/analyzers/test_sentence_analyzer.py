"""Tests for SentenceAnalyzer class."""

from textprettify import SentenceAnalyzer


class TestSentenceAnalysis:
    def test_count(self):
        analyzer = SentenceAnalyzer("Hello. How are you? I'm fine!")
        assert analyzer.count() == 3

    def test_extract(self):
        analyzer = SentenceAnalyzer("Hello. How are you?")
        sentences = analyzer.extract()
        assert len(sentences) == 2
        assert "Hello" in sentences

    def test_average_length(self):
        analyzer = SentenceAnalyzer("Hello world. How are you doing?")
        avg = analyzer.average_length()
        assert round(avg, 1) == 3.0

    def test_longest_sentence(self):
        analyzer = SentenceAnalyzer("Hi. This is a longer sentence. Bye.")
        longest = analyzer.longest_sentence()
        assert "longer" in longest

    def test_shortest_sentence(self):
        analyzer = SentenceAnalyzer("Hi. This is longer. Bye.")
        shortest = analyzer.shortest_sentence()
        assert shortest in ["Hi", "Bye"]

    def test_get_statistics(self):
        analyzer = SentenceAnalyzer("Hi. Hello there.")
        stats = analyzer.get_statistics()
        assert stats["count"] == 2
        assert "average_length" in stats
        assert "sentences" in stats
        assert "longest" in stats
        assert "shortest" in stats
