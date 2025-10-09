"""Tests for GenerationFormatter class."""

from textprettify import GenerationFormatter


class TestLoremIpsum:
    def test_default_lorem_ipsum(self):
        text = GenerationFormatter.lorem_ipsum()
        assert isinstance(text, str)
        assert len(text) > 0

    def test_multiple_paragraphs(self):
        text = GenerationFormatter.lorem_ipsum(paragraphs=3)
        paragraphs = text.split("\n\n")
        assert len(paragraphs) == 3

    def test_custom_sentences(self):
        text = GenerationFormatter.lorem_ipsum(paragraphs=1, sentences_per_paragraph=3)
        sentence_count = text.count(".")
        assert sentence_count == 3


class TestNumberSpelling:
    def test_spell_out_numbers(self):
        formatter = GenerationFormatter("I have 5 apples and 10 oranges")
        result = formatter.spell_out_numbers()
        assert "five" in result
        assert "ten" in result

    def test_spell_out_numbers_max(self):
        formatter = GenerationFormatter("I have 5 apples and 200 oranges")
        result = formatter.spell_out_numbers(max_number=10)
        assert "five" in result
        assert "200" in result

    def test_spell_out_teens(self):
        formatter = GenerationFormatter("I am 13 years old")
        result = formatter.spell_out_numbers()
        assert "thirteen" in result

    def test_spell_out_compound(self):
        formatter = GenerationFormatter("I have 25 items")
        result = formatter.spell_out_numbers()
        assert "twenty-five" in result


class TestCurrencyFormatting:
    def test_format_currency_default(self):
        formatter = GenerationFormatter("The price is 1234.5")
        result = formatter.format_currency()
        assert "$1,234.50" in result

    def test_format_currency_euro(self):
        formatter = GenerationFormatter("The price is 1000")
        result = formatter.format_currency("€")
        assert "€1,000.00" in result


class TestPercentageFormatting:
    def test_format_percentage(self):
        formatter = GenerationFormatter("Success rate is 0.95")
        result = formatter.format_percentage()
        assert "95.0%" in result

    def test_format_percentage_precision(self):
        formatter = GenerationFormatter("Growth of 0.123")
        result = formatter.format_percentage(2)
        assert "12.30%" in result
