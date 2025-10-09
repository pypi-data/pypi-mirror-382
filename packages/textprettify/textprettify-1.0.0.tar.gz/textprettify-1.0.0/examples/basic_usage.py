"""
Basic usage examples for TextPrettify.
"""

from textprettify import BasicFormatter


def main():
    print("=" * 60)
    print("TextPrettify - Basic Usage Examples")
    print("=" * 60)

    # Example 1: Remove extra whitespace
    print("\n1. Remove Extra Whitespace:")
    messy_text = "  Hello    World   from   Python  "
    formatter = BasicFormatter(messy_text)
    clean_text = formatter.remove_extra_whitespace()
    print(f"   Input:  '{messy_text}'")
    print(f"   Output: '{clean_text}'")

    # Example 2: Slugify
    print("\n2. Slugify:")
    titles = [
        "My Awesome Blog Post!",
        "Python 3.11: New Features",
        "How to Learn AI & ML?",
    ]
    for title in titles:
        formatter = BasicFormatter(title)
        print(f"   '{title}'")
        print(f"   → {formatter.slugify()}")

    # Example 3: Reading time
    print("\n3. Reading Time Estimation:")
    short_article = "Lorem ipsum dolor sit amet. " * 50
    long_article = "Lorem ipsum dolor sit amet. " * 300
    short_formatter = BasicFormatter(short_article)
    long_formatter = BasicFormatter(long_article)
    print(
        f"   Short article ({short_formatter.count_words()} words): {short_formatter.get_reading_time()}"
    )
    print(
        f"   Long article ({long_formatter.count_words()} words): {long_formatter.get_reading_time()}"
    )

    # Example 4: Capitalize words
    print("\n4. Capitalize Words:")
    book_titles = [
        "the lord of the rings",
        "a tale of two cities",
        "the importance of being earnest",
    ]
    exceptions = ["the", "of", "a", "an", "and", "or", "but"]
    for book in book_titles:
        formatter = BasicFormatter(book)
        formatted = formatter.capitalize_words(exceptions=exceptions)
        print(f"   {book}")
        print(f"   → {formatted}")

    # Example 5: Truncate text
    print("\n5. Truncate Text:")
    long_text = "The quick brown fox jumps over the lazy dog in the meadow"
    formatter = BasicFormatter(long_text)
    for length in [20, 30, 40]:
        truncated = formatter.truncate(max_length=length)
        print(f"   Max {length} chars: {truncated}")

    # Example 6: Remove punctuation
    print("\n6. Remove Punctuation:")
    texts_with_punct = [
        "Hello, World!",
        "Python is awesome!!!",
        "user@example.com (email)",
    ]
    for text in texts_with_punct:
        formatter = BasicFormatter(text)
        clean = formatter.remove_punctuation()
        print(f"   '{text}' → '{clean}'")

    # Example 7: Keep specific punctuation
    print("\n7. Remove Punctuation (Keep Specific Chars):")
    email = "Contact: user@example.com!"
    formatter = BasicFormatter(email)
    clean_email = formatter.remove_punctuation(keep="@.:")
    print(f"   '{email}'")
    print(f"   → '{clean_email}'")

    # Example 8: Word count
    print("\n8. Word Count:")
    sample_text = "The quick brown fox jumps over the lazy brown dog"
    formatter = BasicFormatter(sample_text)
    total = formatter.count_words()
    unique = formatter.count_words(unique=True)
    print(f"   Text: '{sample_text}'")
    print(f"   Total words: {total}")
    print(f"   Unique words: {unique}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
