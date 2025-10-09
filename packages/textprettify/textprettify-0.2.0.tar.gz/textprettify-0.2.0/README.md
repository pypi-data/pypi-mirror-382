# TextPrettify

A comprehensive Python library for text formatting, transformation, and analysis. TextPrettify provides specialized, easy-to-use classes for manipulating and analyzing text strings for common use cases.

## Features

### Formatters
- **BasicFormatter**: Core text operations (whitespace, slugify, reading time, capitalization, truncation, punctuation, word counting)
- **CaseFormatter**: Case conversions (snake_case, camelCase, PascalCase, CONSTANT_CASE, kebab-case, Title Case)
- **TransformationFormatter**: Text transformations (reversal, line operations, find/replace, highlighting, acronyms, wrapping)
- **GenerationFormatter**: Text generation (Lorem Ipsum, number spelling, currency, percentages)
- **NormalizationFormatter**: Text normalization (Unicode, accents, smart quotes)

### Analyzers
- **CharacterAnalyzer**: Character-level analysis (counts, types)
- **SentenceAnalyzer**: Sentence extraction and analysis
- **ReadabilityAnalyzer**: Readability metrics (Flesch Reading Ease, Flesch-Kincaid Grade)
- **StatisticsAnalyzer**: Word statistics and frequency analysis
- **LanguageAnalyzer**: Basic language detection

## Installation

```bash
# From PyPI (when published)
pip install textprettify

# From source
git clone https://github.com/mmssajith/TextPrettify.git
cd TextPrettify
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Basic Formatting

```python
from textprettify import BasicFormatter

# Clean up messy whitespace
formatter = BasicFormatter("  Hello    World  ")
print(formatter.remove_extra_whitespace())  # "Hello World"

# Create URL-friendly slugs
formatter = BasicFormatter("My Awesome Post!")
print(formatter.slugify())  # "my-awesome-post"

# Estimate reading time
formatter = BasicFormatter("Lorem ipsum " * 200)
print(formatter.get_reading_time())  # "2 mins read"

# Capitalize with exceptions
formatter = BasicFormatter("a tale of two cities")
print(formatter.capitalize_words(exceptions=['a', 'of']))  # "A Tale of Two Cities"

# Truncate long text
formatter = BasicFormatter("The quick brown fox jumps over the lazy dog")
print(formatter.truncate(max_length=20))  # "The quick brown..."

# Count words
formatter = BasicFormatter("Hello world hello")
print(formatter.count_words())  # 3
print(formatter.count_words(unique=True))  # 2
```

### Case Conversions

```python
from textprettify import CaseFormatter

formatter = CaseFormatter("Hello World")
print(formatter.to_snake_case())      # "hello_world"
print(formatter.to_camel_case())      # "helloWorld"
print(formatter.to_pascal_case())     # "HelloWorld"
print(formatter.to_constant_case())   # "HELLO_WORLD"
print(formatter.to_kebab_case())      # "hello-world"
print(formatter.to_title_case(exceptions=['the', 'of']))  # "Hello World"
```

### Text Transformations

```python
from textprettify import TransformationFormatter

# Text reversal
formatter = TransformationFormatter("Hello World")
print(formatter.reverse_characters())  # "dlroW olleH"
print(formatter.reverse_words())       # "World Hello"

# Line operations
formatter = TransformationFormatter("apple\nbanana\napple\ncherry")
print(formatter.deduplicate_lines())   # "apple\nbanana\ncherry"
print(formatter.sort_lines())          # "apple\nbanana\ncherry"

# Find and replace
formatter = TransformationFormatter("Hello World, hello Python")
print(formatter.find_and_replace('hello', 'Hi', case_sensitive=False))
# "Hi World, Hi Python"

# Regex replace
formatter = TransformationFormatter("I have 5 apples and 10 oranges")
print(formatter.find_and_replace(r'\d+', 'X', regex=True))
# "I have X apples and X oranges"

# Extract acronyms
formatter = TransformationFormatter("NASA and FBI are USA organizations")
print(formatter.extract_acronyms())  # ['NASA', 'FBI', 'USA']

# Text wrapping
formatter = TransformationFormatter("Very long text here...")
print(formatter.wrap_text(width=40))
```

### Text Generation

```python
from textprettify import GenerationFormatter

# Lorem Ipsum
lorem = GenerationFormatter.lorem_ipsum(paragraphs=2)
print(lorem)

# Spell out numbers
formatter = GenerationFormatter("I have 5 apples and 10 oranges")
print(formatter.spell_out_numbers())  # "I have five apples and ten oranges"

# Format currency
formatter = GenerationFormatter("The price is 1234.5")
print(formatter.format_currency())     # "The price is $1,234.50"
print(formatter.format_currency('€'))  # "The price is €1,234.50"

# Format percentages
formatter = GenerationFormatter("Success rate is 0.95")
print(formatter.format_percentage())  # "Success rate is 95.0%"
```

### Text Normalization

```python
from textprettify import NormalizationFormatter

# Remove accents
formatter = NormalizationFormatter("café résumé")
print(formatter.remove_accents())  # "cafe resume"

# Unicode normalization
formatter = NormalizationFormatter("café")
print(formatter.normalize_unicode('NFC'))

# Smart quotes
formatter = NormalizationFormatter('"Hello World"')
print(formatter.to_smart_quotes())      # ""Hello World""
print(formatter.to_straight_quotes())   # '"Hello World"'
```

### Text Analysis

```python
from textprettify import (
    CharacterAnalyzer,
    SentenceAnalyzer,
    ReadabilityAnalyzer,
    StatisticsAnalyzer,
    LanguageAnalyzer
)

text = "Python is a high-level programming language. It's easy to learn."

# Character analysis
char_analyzer = CharacterAnalyzer(text)
counts = char_analyzer.get_all_counts()
print(f"Total characters: {counts['total']}")
print(f"Letters: {counts['letters']}")
print(f"Digits: {counts['digits']}")

# Sentence analysis
sent_analyzer = SentenceAnalyzer(text)
print(f"Sentences: {sent_analyzer.count()}")
print(f"Average length: {sent_analyzer.average_length()} words")

# Readability metrics
read_analyzer = ReadabilityAnalyzer(text)
scores = read_analyzer.get_scores()
print(f"Reading ease: {scores['reading_ease']}")
print(f"Grade level: {scores['grade_level']}")
print(f"Interpretation: {read_analyzer.interpret_reading_ease()}")

# Text statistics
stats_analyzer = StatisticsAnalyzer(text)
stats = stats_analyzer.get_statistics()
print(f"Total words: {stats['word_count']}")
print(f"Unique words: {stats['unique_word_count']}")
print(f"Lexical diversity: {stats['lexical_diversity']}")

# Word frequency
word_freq = stats_analyzer.word_frequency(top_n=5)
print(f"Top 5 words: {word_freq}")

# Language detection
lang_analyzer = LanguageAnalyzer(text)
result = lang_analyzer.detect()
print(f"Language: {lang_analyzer.get_language_name()} ({result['language']})")
print(f"Confidence: {result['confidence']}")
```

## API Reference

### BasicFormatter

```python
BasicFormatter(text: str)
```

**Methods:**
- `remove_extra_whitespace() -> str`: Remove extra whitespace
- `slugify(separator: str = '-', lowercase: bool = True) -> str`: Convert to URL slug
- `get_reading_time(words_per_minute: int = 200, include_unit: bool = True) -> str | int`: Estimate reading time
- `capitalize_words(exceptions: list[str] = None) -> str`: Capitalize words with exceptions
- `truncate(max_length: int, suffix: str = '...', whole_words: bool = True) -> str`: Truncate text
- `remove_punctuation(keep: str = None) -> str`: Remove punctuation
- `count_words(unique: bool = False) -> int`: Count words

### CaseFormatter

```python
CaseFormatter(text: str)
```

**Methods:**
- `to_snake_case() -> str`: Convert to snake_case
- `to_camel_case() -> str`: Convert to camelCase
- `to_pascal_case() -> str`: Convert to PascalCase
- `to_constant_case() -> str`: Convert to CONSTANT_CASE
- `to_kebab_case() -> str`: Convert to kebab-case
- `to_title_case(exceptions: list[str] = None) -> str`: Convert to Title Case

### TransformationFormatter

```python
TransformationFormatter(text: str)
```

**Methods:**
- `reverse_characters() -> str`: Reverse character order
- `reverse_words() -> str`: Reverse word order
- `add_letter_spacing(separator: str = ' ') -> str`: Add spacing between letters
- `remove_blank_lines() -> str`: Remove blank lines
- `deduplicate_lines() -> str`: Remove duplicate lines
- `sort_lines(reverse: bool = False) -> str`: Sort lines
- `find_and_replace(pattern: str, replacement: str, case_sensitive: bool = True, regex: bool = False) -> str`: Find and replace text
- `highlight_markdown(words: list[str], style: str) -> str`: Highlight words in markdown
- `highlight_html(words: list[str], tag: str) -> str`: Highlight words in HTML
- `extract_acronyms() -> list[str]`: Extract acronyms
- `wrap_text(width: int) -> str`: Wrap text to width

### GenerationFormatter

```python
GenerationFormatter(text: str)
```

**Static Methods:**
- `lorem_ipsum(paragraphs: int = 1, sentences_per_paragraph: int = 5) -> str`: Generate Lorem Ipsum

**Instance Methods:**
- `spell_out_numbers(max_number: int = 100) -> str`: Spell out numbers
- `format_currency(symbol: str = '$') -> str`: Format currency
- `format_percentage(decimals: int = 1) -> str`: Format percentages

### NormalizationFormatter

```python
NormalizationFormatter(text: str)
```

**Methods:**
- `normalize_unicode(form: str = 'NFC') -> str`: Normalize Unicode (NFC, NFD, NFKC, NFKD)
- `remove_accents() -> str`: Remove accents from text
- `to_smart_quotes() -> str`: Convert to smart quotes
- `to_straight_quotes() -> str`: Convert to straight quotes

### Analyzers

See the Quick Start section above for analyzer usage examples.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=textprettify

# Run specific test file
pytest tests/formatters/test_basic_formatter.py

# Run specific test class
pytest tests/formatters/test_basic_formatter.py::TestSlugify
```

## Examples

Check out the `examples/` directory for comprehensive usage examples:

- `basic_usage.py` - Basic formatting operations
- `text_transformation_example.py` - Case conversions and transformations
- `text_generation_example.py` - Text generation and manipulation
- `text_analysis_example.py` - Text analysis and statistics
- `blog_post_formatter.py` - Format blog post metadata
- `url_generator.py` - Generate clean URLs from titles

## Project Structure

```
textprettify/
├── formatters/
│   ├── basic_formatter.py
│   ├── case_formatter.py
│   ├── transformation_formatter.py
│   ├── generation_formatter.py
│   └── normalization_formatter.py
├── analyzers/
│   ├── character_analyzer.py
│   ├── sentence_analyzer.py
│   ├── readability_analyzer.py
│   ├── statistics_analyzer.py
│   └── language_analyzer.py
tests/
├── formatters/
└── analyzers/
examples/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/mmssajith/TextPrettify.git
cd TextPrettify

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=textprettify --cov-report=html
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Sajith

## Development

### Code Quality Tools

This project uses pre-commit hooks to maintain code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

**Configured hooks:**
- **Ruff**: Fast Python linter and formatter
- **Mypy**: Static type checking

### Running Pre-commit Checks

The pre-commit hooks will run automatically on every commit. You can also run them manually:

```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
pre-commit run mypy --all-files
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Latest Release: v0.2.0** - Added comprehensive text analysis tools, pre-commit hooks, and enhanced formatters.
