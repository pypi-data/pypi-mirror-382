"""
Text generation formatting functionality for TextPrettify.
"""

import re


class GenerationFormatter:
    """
    Formatter for text generation and number formatting operations.

    Provides static methods for lorem ipsum generation and instance methods
    for number formatting (spelling out numbers, currency, percentages).
    """

    def __init__(self, text: str):
        """
        Initialize the GenerationFormatter with input text.

        Args:
            text: The text to format
        """
        self.text = text

    @staticmethod
    def lorem_ipsum(paragraphs: int = 1, sentences_per_paragraph: int = 5) -> str:
        """Generate lorem ipsum placeholder text."""
        lorem_words = [
            "lorem",
            "ipsum",
            "dolor",
            "sit",
            "amet",
            "consectetur",
            "adipiscing",
            "elit",
            "sed",
            "do",
            "eiusmod",
            "tempor",
            "incididunt",
            "ut",
            "labore",
            "et",
            "dolore",
            "magna",
            "aliqua",
            "enim",
            "ad",
            "minim",
            "veniam",
            "quis",
            "nostrud",
            "exercitation",
            "ullamco",
            "laboris",
            "nisi",
            "aliquip",
            "ex",
            "ea",
            "commodo",
            "consequat",
            "duis",
            "aute",
            "irure",
            "in",
            "reprehenderit",
            "voluptate",
            "velit",
            "esse",
            "cillum",
            "fugiat",
            "nulla",
            "pariatur",
            "excepteur",
            "sint",
            "occaecat",
            "cupidatat",
            "non",
            "proident",
            "sunt",
            "culpa",
            "qui",
            "officia",
            "deserunt",
            "mollit",
            "anim",
            "id",
            "est",
            "laborum",
        ]

        import random

        paragraphs_list = []

        for _ in range(paragraphs):
            sentences = []
            for _ in range(sentences_per_paragraph):
                sentence_length = random.randint(5, 15)
                sentence_words = random.sample(lorem_words, sentence_length)
                sentence_words[0] = sentence_words[0].capitalize()
                sentence = " ".join(sentence_words) + "."
                sentences.append(sentence)

            paragraphs_list.append(" ".join(sentences))

        return "\n\n".join(paragraphs_list)

    def spell_out_numbers(self, max_number: int = 100) -> str:
        """Convert numeric digits to written words (for numbers 0-100)."""
        number_words = {
            0: "zero",
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine",
            10: "ten",
            11: "eleven",
            12: "twelve",
            13: "thirteen",
            14: "fourteen",
            15: "fifteen",
            16: "sixteen",
            17: "seventeen",
            18: "eighteen",
            19: "nineteen",
            20: "twenty",
            30: "thirty",
            40: "forty",
            50: "fifty",
            60: "sixty",
            70: "seventy",
            80: "eighty",
            90: "ninety",
            100: "one hundred",
        }

        def number_to_words(n):
            if n in number_words:
                return number_words[n]
            elif 21 <= n <= 99:
                tens = (n // 10) * 10
                ones = n % 10
                return f"{number_words[tens]}-{number_words[ones]}"
            return str(n)

        def replace_number(match):
            num = int(match.group())
            if num <= max_number:
                return number_to_words(num)
            return str(num)

        return re.sub(r"\b\d+\b", replace_number, self.text)

    def format_currency(
        self, currency_symbol: str = "$", decimal_places: int = 2
    ) -> str:
        """Format numbers as currency."""

        def format_number(match):
            num = float(match.group())
            formatted = f"{num:,.{decimal_places}f}"
            return f"{currency_symbol}{formatted}"

        return re.sub(r"\b\d+\.?\d*\b", format_number, self.text)

    def format_percentage(self, decimal_places: int = 1) -> str:
        """Format decimal numbers as percentages."""

        def format_number(match):
            num = float(match.group())
            percentage = num * 100
            return f"{percentage:.{decimal_places}f}%"

        return re.sub(r"\b0\.\d+\b", format_number, self.text)
