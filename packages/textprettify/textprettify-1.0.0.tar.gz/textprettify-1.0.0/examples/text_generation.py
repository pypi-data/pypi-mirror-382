"""
Text generation and manipulation examples using specialized formatters.
"""

from textprettify import GenerationFormatter, TransformationFormatter


def main():
    print("=" * 70)
    print("TEXT GENERATION & MANIPULATION EXAMPLES")
    print("=" * 70)

    # Lorem Ipsum Generator
    print("\n1. LOREM IPSUM GENERATOR")
    print("-" * 70)

    print("\nSingle paragraph (default):")
    lorem1 = GenerationFormatter.lorem_ipsum()
    print(lorem1[:200] + "...")

    print("\nMultiple paragraphs (3 paragraphs, 4 sentences each):")
    lorem2 = GenerationFormatter.lorem_ipsum(paragraphs=3, sentences_per_paragraph=4)
    paragraphs = lorem2.split("\n\n")
    for i, para in enumerate(paragraphs, 1):
        print(f"\nParagraph {i}:")
        print(para[:150] + "...")

    # Text Wrapping
    print("\n2. TEXT WRAPPING")
    print("-" * 70)

    long_text = (
        "Python is a high-level, interpreted programming language with dynamic "
        "semantics. Its high-level built-in data structures, combined with dynamic "
        "typing and dynamic binding, make it very attractive for Rapid Application "
        "Development."
    )

    formatter = TransformationFormatter(long_text)

    print("\nOriginal text:")
    print(long_text)

    print("\nWrapped to 40 characters:")
    print(formatter.wrap_text(width=40))

    print("\nWrapped to 60 characters:")
    print(formatter.wrap_text(width=60))

    # Line Operations
    print("\n3. LINE OPERATIONS")
    print("-" * 70)

    # Remove blank lines
    print("\n3a. Remove Blank Lines:")
    text_with_blanks = """Line 1

Line 2


Line 3

Line 4"""
    formatter = TransformationFormatter(text_with_blanks)
    print("Before:")
    print(repr(text_with_blanks))
    print("\nAfter:")
    print(repr(formatter.remove_blank_lines()))

    # Deduplicate lines
    print("\n3b. Deduplicate Lines:")
    duplicate_text = """apple
banana
apple
cherry
banana
date"""
    formatter = TransformationFormatter(duplicate_text)
    print("Before:")
    print(duplicate_text)
    print("\nAfter (preserving order):")
    print(formatter.deduplicate_lines())

    # Sort lines
    print("\n3c. Sort Lines:")
    unsorted_text = """zebra
apple
mango
banana
cherry"""
    formatter = TransformationFormatter(unsorted_text)
    print("Before:")
    print(unsorted_text)
    print("\nSorted (ascending):")
    print(formatter.sort_lines())
    print("\nSorted (descending):")
    print(formatter.sort_lines(reverse=True))

    # Find and Replace
    print("\n4. FIND AND REPLACE")
    print("-" * 70)

    # Basic replacement
    print("\n4a. Basic Replacement:")
    sample_text = "Hello World, Hello Python, Hello everyone!"
    formatter = TransformationFormatter(sample_text)
    print(f"Original: {sample_text}")
    print(f"Replace 'Hello' → 'Hi': {formatter.find_and_replace('Hello', 'Hi')}")

    # Case-insensitive replacement
    print("\n4b. Case-Insensitive Replacement:")
    mixed_case = "Hello World, hello Python, HELLO everyone!"
    formatter = TransformationFormatter(mixed_case)
    print(f"Original: {mixed_case}")
    print(
        f"Replace 'hello' (case-insensitive): {formatter.find_and_replace('hello', 'Hi', case_sensitive=False)}"
    )

    # Regex replacement
    print("\n4c. Regex Replacement:")
    text_with_numbers = "I bought 5 apples, 10 bananas, and 3 oranges"
    formatter = TransformationFormatter(text_with_numbers)
    print(f"Original: {text_with_numbers}")
    print(
        f"Replace all numbers with 'X': {formatter.find_and_replace(r'\\d+', 'X', regex=True)}"
    )

    # Text Highlighting
    print("\n5. TEXT HIGHLIGHTING / EMPHASIS")
    print("-" * 70)

    # Markdown highlighting
    print("\n5a. Markdown Highlighting:")
    article = "Python is a programming language. Python is easy to learn and Python is powerful."
    formatter = TransformationFormatter(article)

    print(f"Original: {article}")
    print(f"\nBold: {formatter.highlight_markdown(['Python'], 'bold')}")
    print(f"\nItalic: {formatter.highlight_markdown(['programming'], 'italic')}")
    print(f"\nCode: {formatter.highlight_markdown(['Python'], 'code')}")
    print(f"\nBold+Italic: {formatter.highlight_markdown(['Python', 'easy'], 'both')}")

    # HTML highlighting
    print("\n5b. HTML Highlighting:")
    content = "This is important text with emphasis"
    formatter = TransformationFormatter(content)

    print(f"Original: {content}")
    print(f"\n<strong>: {formatter.highlight_html(['important'], 'strong')}")
    print(f"\n<em>: {formatter.highlight_html(['emphasis'], 'em')}")
    print(f"\n<mark>: {formatter.highlight_html(['important'], 'mark')}")
    print(f"\n<code>: {formatter.highlight_html(['text'], 'code')}")

    # Acronym Extraction
    print("\n6. ACRONYM EXTRACTION")
    print("-" * 70)

    tech_text = """
    NASA develops space technology. The FBI investigates federal crimes.
    HTTP is used for web communication. USA is part of NATO.
    APIs are used in REST services and SOAP protocols.
    """
    formatter = TransformationFormatter(tech_text)

    acronyms = formatter.extract_acronyms()
    print(f"Text: {tech_text.strip()}")
    print(f"\nFound {len(acronyms)} acronyms:")
    for acronym in acronyms:
        print(f"  - {acronym}")

    # Number Formatting
    print("\n7. NUMBER FORMATTING")
    print("-" * 70)

    # Spell out numbers
    print("\n7a. Spell Out Numbers:")
    number_examples = [
        "I have 5 apples and 10 oranges",
        "There are 42 students in the class",
        "I bought 25 items",
    ]

    for text in number_examples:
        formatter = GenerationFormatter(text)
        print(f"  {text}")
        print(f"  → {formatter.spell_out_numbers()}")

    # Currency formatting
    print("\n7b. Currency Formatting:")
    currency_examples = ["The price is 1234.5", "Balance: 5000"]

    for text in currency_examples:
        formatter = GenerationFormatter(text)
        print(f"  {text}")
        print(f"  → {formatter.format_currency()}")

    # Percentage formatting
    print("\n7c. Percentage Formatting:")
    percentage_examples = ["Success rate is 0.95", "Growth of 0.123"]

    for text in percentage_examples:
        formatter = GenerationFormatter(text)
        print(f"  {text}")
        print(f"  → {formatter.format_percentage()}")

    # Complex Example: Document Processing
    print("\n8. COMPLEX EXAMPLE: DOCUMENT PROCESSING")
    print("-" * 70)

    document = """Introduction to AI


Artificial Intelligence (AI) is transforming industries.
AI enables machines to learn from experience.
Machine Learning (ML) is a subset of AI.
AI and ML are used in various applications.


Deep Learning is part of ML.
AI research continues to grow.
Companies invest heavily in AI.
"""

    formatter = TransformationFormatter(document)

    print("Original document:")
    print(document)

    # Process the document
    print("\nProcessing pipeline:")
    print("1. Remove blank lines")
    processed = formatter.remove_blank_lines()

    print("2. Extract acronyms")
    formatter2 = TransformationFormatter(processed)
    acronyms = formatter2.extract_acronyms()
    print(f"   Found: {', '.join(acronyms)}")

    print("3. Highlight acronyms in markdown")
    highlighted = formatter2.highlight_markdown(acronyms, "bold")

    print("4. Wrap to 60 characters")
    formatter3 = TransformationFormatter(highlighted)
    final = formatter3.wrap_text(width=60)

    print("\nProcessed document:")
    print(final)

    # Practical Use Case: Code Documentation
    print("\n9. PRACTICAL USE CASE: CODE DOCUMENTATION")
    print("-" * 70)

    code_comments = """TODO: Implement API endpoint
TODO: Add error handling
FIXME: Fix memory leak
TODO: Write unit tests
NOTE: This requires Python 3.8+
FIXME: Update deprecated code
"""

    formatter = TransformationFormatter(code_comments)

    print("Original comments:")
    print(code_comments)

    # Extract and organize by type
    print("Sorted and deduplicated:")
    sorted_comments = formatter.sort_lines()
    formatter_sorted = TransformationFormatter(sorted_comments)
    deduped = formatter_sorted.deduplicate_lines()
    print(deduped)

    print("\nHighlight keywords:")
    formatter_final = TransformationFormatter(deduped)
    highlighted = formatter_final.highlight_markdown(["TODO", "FIXME", "NOTE"], "bold")
    print(highlighted)

    print("\n" + "=" * 70)
    print("GENERATION & MANIPULATION EXAMPLES COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
