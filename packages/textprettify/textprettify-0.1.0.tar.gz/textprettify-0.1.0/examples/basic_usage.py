"""
Basic usage examples for TextPrettify.
"""

from textprettify import (
    remove_extra_whitespace,
    slugify,
    get_reading_time,
    capitalize_words,
    truncate_text,
    remove_punctuation,
    count_words
)


def main():
    print("=" * 60)
    print("TextPrettify - Basic Usage Examples")
    print("=" * 60)

    # Example 1: Remove extra whitespace
    print("\n1. Remove Extra Whitespace:")
    messy_text = "  Hello    World   from   Python  "
    clean_text = remove_extra_whitespace(messy_text)
    print(f"   Input:  '{messy_text}'")
    print(f"   Output: '{clean_text}'")

    # Example 2: Slugify
    print("\n2. Slugify:")
    titles = [
        "My Awesome Blog Post!",
        "Python 3.11: New Features",
        "How to Learn AI & ML?"
    ]
    for title in titles:
        print(f"   '{title}'")
        print(f"   → {slugify(title)}")

    # Example 3: Reading time
    print("\n3. Reading Time Estimation:")
    short_article = "Lorem ipsum dolor sit amet. " * 50
    long_article = "Lorem ipsum dolor sit amet. " * 300
    print(f"   Short article ({count_words(short_article)} words): {get_reading_time(short_article)}")
    print(f"   Long article ({count_words(long_article)} words): {get_reading_time(long_article)}")

    # Example 4: Capitalize words
    print("\n4. Capitalize Words:")
    book_titles = [
        "the lord of the rings",
        "a tale of two cities",
        "the importance of being earnest"
    ]
    exceptions = ['the', 'of', 'a', 'an', 'and', 'or', 'but']
    for book in book_titles:
        formatted = capitalize_words(book, exceptions=exceptions)
        print(f"   {book}")
        print(f"   → {formatted}")

    # Example 5: Truncate text
    print("\n5. Truncate Text:")
    long_text = "The quick brown fox jumps over the lazy dog in the meadow"
    for length in [20, 30, 40]:
        truncated = truncate_text(long_text, max_length=length)
        print(f"   Max {length} chars: {truncated}")

    # Example 6: Remove punctuation
    print("\n6. Remove Punctuation:")
    texts_with_punct = [
        "Hello, World!",
        "Python is awesome!!!",
        "user@example.com (email)",
    ]
    for text in texts_with_punct:
        clean = remove_punctuation(text)
        print(f"   '{text}' → '{clean}'")

    # Example 7: Keep specific punctuation
    print("\n7. Remove Punctuation (Keep Specific Chars):")
    email = "Contact: user@example.com!"
    clean_email = remove_punctuation(email, keep='@.:')
    print(f"   '{email}'")
    print(f"   → '{clean_email}'")

    # Example 8: Word count
    print("\n8. Word Count:")
    sample_text = "The quick brown fox jumps over the lazy brown dog"
    total = count_words(sample_text)
    unique = count_words(sample_text, unique=True)
    print(f"   Text: '{sample_text}'")
    print(f"   Total words: {total}")
    print(f"   Unique words: {unique}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
