"""Tests for ReadabilityAnalyzer class."""

from textprettify import ReadabilityAnalyzer


class TestReadabilityMetrics:
    def test_flesch_reading_ease(self):
        analyzer = ReadabilityAnalyzer("The cat sat on the mat.")
        score = analyzer.flesch_reading_ease()
        assert isinstance(score, float)
        assert score >= 0
        assert score <= 100

    def test_flesch_kincaid_grade(self):
        analyzer = ReadabilityAnalyzer("The cat sat on the mat.")
        grade = analyzer.flesch_kincaid_grade()
        assert isinstance(grade, float)
        assert grade >= 0

    def test_get_scores(self):
        analyzer = ReadabilityAnalyzer("Simple text here.")
        scores = analyzer.get_scores()
        assert "reading_ease" in scores
        assert "grade_level" in scores

    def test_interpret_reading_ease(self):
        analyzer = ReadabilityAnalyzer("Simple text.")
        interpretation = analyzer.interpret_reading_ease()
        assert isinstance(interpretation, str)
        assert len(interpretation) > 0

    def test_empty_text(self):
        analyzer = ReadabilityAnalyzer("")
        assert analyzer.flesch_reading_ease() == 0.0
        assert analyzer.flesch_kincaid_grade() == 0.0
