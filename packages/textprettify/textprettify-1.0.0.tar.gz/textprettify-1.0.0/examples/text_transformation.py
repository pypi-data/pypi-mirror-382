"""
Text transformation examples using specialized formatters.
"""

from textprettify import (
    CaseFormatter,
    TransformationFormatter,
    NormalizationFormatter,
    GenerationFormatter,
)


def main():
    print("=" * 70)
    print("TEXT TRANSFORMATION EXAMPLES")
    print("=" * 70)

    # Case Conversions
    print("\n1. CASE CONVERSIONS")
    print("-" * 70)

    examples = ["Hello World", "helloWorld", "HelloWorld", "hello_world_example"]

    for text in examples:
        formatter = CaseFormatter(text)
        print(f"\nOriginal: '{text}'")
        print(f"  snake_case:     {formatter.to_snake_case()}")
        print(f"  camelCase:      {formatter.to_camel_case()}")
        print(f"  PascalCase:     {formatter.to_pascal_case()}")
        print(f"  CONSTANT_CASE:  {formatter.to_constant_case()}")
        print(f"  kebab-case:     {formatter.to_kebab_case()}")

    # Text Reversal
    print("\n2. TEXT REVERSAL")
    print("-" * 70)

    reversal_examples = [
        "Hello World",
        "Python Programming Language",
        "The quick brown fox",
    ]

    for text in reversal_examples:
        formatter = TransformationFormatter(text)
        print(f"\nOriginal: '{text}'")
        print(f"  Reverse characters: {formatter.reverse_characters()}")
        print(f"  Reverse words:      {formatter.reverse_words()}")

    # Letter Spacing
    print("\n3. LETTER SPACING")
    print("-" * 70)

    spacing_text = "HELLO"
    formatter = TransformationFormatter(spacing_text)
    print(f"\nOriginal: '{spacing_text}'")
    print(f"  Default spacing:  {formatter.add_letter_spacing()}")
    print(f"  Dash spacing:     {formatter.add_letter_spacing('-')}")
    print(f"  Underscore:       {formatter.add_letter_spacing('_')}")
    print(f"  Dot spacing:      {formatter.add_letter_spacing('.')}")
    print(f"  Double space:     {formatter.add_letter_spacing('  ')}")

    # Text Normalization
    print("\n4. TEXT NORMALIZATION")
    print("-" * 70)

    accent_examples = [
        "café résumé",
        "naïve Zürich",
        "São Paulo façade",
        "piñata jalapeño",
    ]

    print("\nAccent Removal:")
    for text in accent_examples:
        formatter = NormalizationFormatter(text)
        print(f"  '{text}' → '{formatter.remove_accents()}'")

    print("\nUnicode Normalization:")
    unicode_text = "café"
    formatter = NormalizationFormatter(unicode_text)
    print(f"  Original: '{unicode_text}'")
    print(f"  NFC:  '{formatter.normalize_unicode('NFC')}'")
    print(f"  NFD:  '{formatter.normalize_unicode('NFD')}'")
    print(f"  NFKC: '{formatter.normalize_unicode('NFKC')}'")
    print(f"  NFKD: '{formatter.normalize_unicode('NFKD')}'")

    # Smart Quotes Conversion
    print("\n5. SMART QUOTES CONVERSION")
    print("-" * 70)

    quote_examples = [
        '"Hello World"',
        "'It's a beautiful day'",
        "\"She said, 'Hello!'\"",
        "The \"quick\" brown 'fox'",
    ]

    print("\nStraight → Smart Quotes:")
    for text in quote_examples:
        formatter = NormalizationFormatter(text)
        smart = formatter.to_smart_quotes()
        print(f"  {text}")
        print(f"  → {smart}")

    print("\nSmart → Straight Quotes:")
    smart_quote_text = '"Hello" and "world"'
    formatter = NormalizationFormatter(smart_quote_text)
    print(f"  {smart_quote_text}")
    print(f"  → {formatter.to_straight_quotes()}")

    # Number Formatting
    print("\n6. NUMBER FORMATTING")
    print("-" * 70)

    # Spell out numbers
    print("\nSpell Out Numbers:")
    number_examples = [
        "I have 5 apples and 10 oranges",
        "There are 42 students in the class",
        "I bought 99 balloons",
        "The year 2024 is here",
    ]

    for text in number_examples:
        formatter = GenerationFormatter(text)
        print(f"  {text}")
        print(f"  → {formatter.spell_out_numbers()}")

    # Currency formatting
    print("\nCurrency Formatting:")
    currency_examples = ["The price is 1234.5", "Total cost: 999.99", "Balance: 5000"]

    for text in currency_examples:
        formatter = GenerationFormatter(text)
        print(f"  {text}")
        print(f"  → USD: {formatter.format_currency('$')}")
        print(f"  → EUR: {formatter.format_currency('€')}")
        print(f"  → GBP: {formatter.format_currency('£')}")

    # Percentage formatting
    print("\nPercentage Formatting:")
    percentage_examples = [
        "Success rate is 0.95",
        "Growth of 0.123",
        "Completion: 0.5",
        "Error rate: 0.02",
    ]

    for text in percentage_examples:
        formatter = GenerationFormatter(text)
        print(f"  {text}")
        print(f"  → {formatter.format_percentage(1)}")

    # Line Operations
    print("\n7. LINE OPERATIONS")
    print("-" * 70)

    # Remove blank lines
    print("\n7a. Remove Blank Lines:")
    text_with_blanks = "Line 1\n\nLine 2\n\n\nLine 3"
    formatter = TransformationFormatter(text_with_blanks)
    print(f"Before: {repr(text_with_blanks)}")
    print(f"After:  {repr(formatter.remove_blank_lines())}")

    # Deduplicate lines
    print("\n7b. Deduplicate Lines:")
    duplicate_text = "apple\nbanana\napple\ncherry"
    formatter = TransformationFormatter(duplicate_text)
    print(f"Before:\n{duplicate_text}")
    print(f"\nAfter:\n{formatter.deduplicate_lines()}")

    # Sort lines
    print("\n7c. Sort Lines:")
    unsorted_text = "zebra\napple\nmango\nbanana"
    formatter = TransformationFormatter(unsorted_text)
    print(f"Before:\n{unsorted_text}")
    print(f"\nSorted (ascending):\n{formatter.sort_lines()}")
    print(f"\nSorted (descending):\n{formatter.sort_lines(reverse=True)}")

    # Variable naming conventions
    print("\n8. VARIABLE NAMING CONVENTIONS")
    print("-" * 70)

    variable_name = "user profile settings"
    formatter = CaseFormatter(variable_name)

    print(f"\nConverting '{variable_name}' for different contexts:")
    print(f"  Python variable:    {formatter.to_snake_case()}")
    print(f"  JavaScript var:     {formatter.to_camel_case()}")
    print(f"  Class name:         {formatter.to_pascal_case()}")
    print(f"  Constant:           {formatter.to_constant_case()}")
    print(f"  CSS class:          {formatter.to_kebab_case()}")

    # Find and Replace
    print("\n9. FIND AND REPLACE")
    print("-" * 70)

    sample_text = "Hello World, Hello Python"
    formatter = TransformationFormatter(sample_text)
    print(f"Original: {sample_text}")
    print(f"Replace 'Hello' → 'Hi': {formatter.find_and_replace('Hello', 'Hi')}")

    mixed_case = "Hello World, hello Python"
    formatter = TransformationFormatter(mixed_case)
    print(f"\nOriginal: {mixed_case}")
    print(
        f"Case-insensitive replace: {formatter.find_and_replace('hello', 'Hi', case_sensitive=False)}"
    )

    text_with_numbers = "I have 5 apples and 10 oranges"
    formatter = TransformationFormatter(text_with_numbers)
    print(f"\nOriginal: {text_with_numbers}")
    print(
        f"Regex replace digits: {formatter.find_and_replace(r'\\d+', 'X', regex=True)}"
    )

    # Text Highlighting
    print("\n10. TEXT HIGHLIGHTING")
    print("-" * 70)

    article = "Python is a programming language"
    formatter = TransformationFormatter(article)

    print(f"Original: {article}")
    print(f"\nMarkdown bold: {formatter.highlight_markdown(['Python'], 'bold')}")
    print(f"Markdown italic: {formatter.highlight_markdown(['programming'], 'italic')}")
    print(f"Markdown code: {formatter.highlight_markdown(['Python'], 'code')}")

    content = "This is important text"
    formatter = TransformationFormatter(content)
    print(f"\nOriginal: {content}")
    print(f"HTML strong: {formatter.highlight_html(['important'], 'strong')}")
    print(f"HTML em: {formatter.highlight_html(['important'], 'em')}")

    # Acronym Extraction
    print("\n11. ACRONYM EXTRACTION")
    print("-" * 70)

    tech_text = "NASA develops technology. FBI investigates crimes. USA is part of NATO."
    formatter = TransformationFormatter(tech_text)

    acronyms = formatter.extract_acronyms()
    print(f"Text: {tech_text}")
    print(f"\nFound {len(acronyms)} acronyms: {', '.join(acronyms)}")

    print("\n" + "=" * 70)
    print("TRANSFORMATION EXAMPLES COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
