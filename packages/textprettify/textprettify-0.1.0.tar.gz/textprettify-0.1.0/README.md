# TextPrettify

A lightweight Python library for text cleaning and formatting. TextPrettify provides simple, intuitive functions to manipulate and format text strings for common use cases.

## Features

- **Remove Extra Whitespace**: Clean up text by removing leading/trailing spaces and normalizing multiple spaces
- **Slugify**: Convert text to URL-friendly slugs
- **Reading Time Estimation**: Calculate estimated reading time for text
- **Capitalize Words**: Apply title case with customizable exceptions
- **Truncate Text**: Shorten text to a maximum length with word-boundary awareness
- **Remove Punctuation**: Strip punctuation with optional character preservation
- **Word Count**: Count total or unique words in text

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/TextPrettify.git
cd TextPrettify

# Install in development mode
pip install -e .
```

## Quick Start

```python
from textprettify import (
    remove_extra_whitespace,
    slugify,
    get_reading_time,
    capitalize_words,
    truncate_text,
    remove_punctuation,
    count_words
)

# Clean up messy whitespace
text = "  Hello    World  "
clean_text = remove_extra_whitespace(text)
print(clean_text)  # "Hello World"

# Create URL-friendly slugs
title = "My Awesome Post!"
slug = slugify(title)
print(slug)  # "my-awesome-post"

# Estimate reading time
article = "Lorem ipsum " * 200
reading_time = get_reading_time(article)
print(reading_time)  # "2 mins read"

# Capitalize with exceptions
title = "a tale of two cities"
formatted = capitalize_words(title, exceptions=['a', 'of'])
print(formatted)  # "A Tale of Two Cities"

# Truncate long text
text = "The quick brown fox jumps over the lazy dog"
short = truncate_text(text, max_length=20)
print(short)  # "The quick brown..."

# Remove punctuation
text = "Hello, World!"
clean = remove_punctuation(text)
print(clean)  # "Hello World"

# Count words
text = "Hello world hello"
total = count_words(text)
unique = count_words(text, unique=True)
print(f"Total: {total}, Unique: {unique}")  # "Total: 3, Unique: 2"
```

## API Reference

### `remove_extra_whitespace(text: str) -> str`

Remove extra whitespace from text, including leading/trailing spaces and multiple consecutive spaces.

**Parameters:**
- `text` (str): The input text to clean

**Returns:**
- str: Text with normalized whitespace

**Example:**
```python
remove_extra_whitespace("  Hello    World  ")
# "Hello World"
```

### `slugify(text: str, separator: str = '-', lowercase: bool = True) -> str`

Convert text to a URL-friendly slug.

**Parameters:**
- `text` (str): The input text to slugify
- `separator` (str): Character to use as separator (default: '-')
- `lowercase` (bool): Convert to lowercase (default: True)

**Returns:**
- str: URL-friendly slug

**Example:**
```python
slugify("My Awesome Post!")
# "my-awesome-post"

slugify("Hello, World!", separator='_')
# "hello_world"
```

### `get_reading_time(text: str, words_per_minute: int = 200, include_unit: bool = True) -> str | int`

Calculate estimated reading time for text.

**Parameters:**
- `text` (str): The input text to analyze
- `words_per_minute` (int): Average reading speed (default: 200)
- `include_unit` (bool): Return formatted string with unit (default: True)

**Returns:**
- str | int: Reading time as formatted string or integer (minutes)

**Example:**
```python
get_reading_time("Hello world " * 100)
# "1 min read"

get_reading_time("Hello world " * 100, include_unit=False)
# 1
```

### `capitalize_words(text: str, exceptions: Optional[list[str]] = None) -> str`

Capitalize the first letter of each word (title case).

**Parameters:**
- `text` (str): The input text to capitalize
- `exceptions` (list[str], optional): List of words to keep lowercase

**Returns:**
- str: Text with capitalized words

**Example:**
```python
capitalize_words("the quick brown fox")
# "The Quick Brown Fox"

capitalize_words("a tale of two cities", exceptions=['a', 'of'])
# "A Tale of Two Cities"
```

### `truncate_text(text: str, max_length: int, suffix: str = '...', whole_words: bool = True) -> str`

Truncate text to a maximum length.

**Parameters:**
- `text` (str): The input text to truncate
- `max_length` (int): Maximum length of output text
- `suffix` (str): String to append to truncated text (default: '...')
- `whole_words` (bool): Only break at word boundaries (default: True)

**Returns:**
- str: Truncated text

**Example:**
```python
truncate_text("The quick brown fox jumps", 15)
# "The quick..."

truncate_text("The quick brown fox jumps", 15, whole_words=False)
# "The quick br..."
```

### `remove_punctuation(text: str, keep: Optional[str] = None) -> str`

Remove punctuation from text.

**Parameters:**
- `text` (str): The input text to clean
- `keep` (str, optional): String of punctuation characters to keep

**Returns:**
- str: Text without punctuation

**Example:**
```python
remove_punctuation("Hello, World!")
# "Hello World"

remove_punctuation("user@example.com", keep='@.')
# "user@example.com"
```

### `count_words(text: str, unique: bool = False) -> int`

Count words in text.

**Parameters:**
- `text` (str): The input text to analyze
- `unique` (bool): Count only unique words (default: False)

**Returns:**
- int: Word count

**Example:**
```python
count_words("Hello world hello")
# 3

count_words("Hello world hello", unique=True)
# 2
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=textprettify

# Run specific test file
python -m pytest tests/test_core.py
```

Or using unittest:

```bash
python -m unittest discover tests
```

## Examples

Check out the `examples/` directory for more detailed usage examples:

- `examples/basic_usage.py` - Basic usage examples for all functions
- `examples/blog_post_formatter.py` - Format blog post metadata
- `examples/url_generator.py` - Generate clean URLs from titles

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Sajith

## Version

0.1.0
