"""Tests for StatisticsAnalyzer class."""

from textprettify import StatisticsAnalyzer


class TestWordStatistics:
    def test_word_count(self):
        analyzer = StatisticsAnalyzer("Hello world from Python")
        assert analyzer.word_count() == 4

    def test_unique_word_count(self):
        analyzer = StatisticsAnalyzer("Hello world hello")
        assert analyzer.unique_word_count() == 2

    def test_average_word_length(self):
        analyzer = StatisticsAnalyzer("Hi hello")
        assert analyzer.average_word_length() == 3.5

    def test_longest_word(self):
        analyzer = StatisticsAnalyzer("Short lengthy word")
        assert analyzer.longest_word() == "lengthy"

    def test_shortest_word(self):
        analyzer = StatisticsAnalyzer("I am happy")
        assert analyzer.shortest_word() == "I"

    def test_word_frequency(self):
        analyzer = StatisticsAnalyzer("hello world hello")
        freq = analyzer.word_frequency()
        assert freq["hello"] == 2
        assert freq["world"] == 1

    def test_word_frequency_top_n(self):
        analyzer = StatisticsAnalyzer("hello world hello python world")
        freq = analyzer.word_frequency(top_n=2)
        assert len(freq) == 2

    def test_word_frequency_case_sensitive(self):
        analyzer = StatisticsAnalyzer("Hello hello HELLO")
        freq = analyzer.word_frequency(case_sensitive=True)
        assert len(freq) == 3

    def test_word_length_distribution(self):
        analyzer = StatisticsAnalyzer("I am happy today")
        dist = analyzer.word_length_distribution()
        assert isinstance(dist, dict)
        assert 1 in dist

    def test_lexical_diversity(self):
        analyzer = StatisticsAnalyzer("hello world hello")
        diversity = analyzer.lexical_diversity()
        assert diversity > 0
        assert diversity <= 1

    def test_get_statistics(self):
        analyzer = StatisticsAnalyzer("Hello world")
        stats = analyzer.get_statistics()
        assert stats["word_count"] == 2
        assert "average_word_length" in stats
        assert "lexical_diversity" in stats
