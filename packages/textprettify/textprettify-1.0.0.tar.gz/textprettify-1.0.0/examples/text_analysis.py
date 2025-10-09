"""
Example usage of specialized analyzers for text analysis and statistics.
"""

from textprettify import (
    CharacterAnalyzer,
    SentenceAnalyzer,
    ReadabilityAnalyzer,
    StatisticsAnalyzer,
    LanguageAnalyzer,
)


def main():
    # Sample text for analysis
    sample_text = """
    Python is a high-level programming language. It was created by Guido van Rossum
    and first released in 1991. Python's design philosophy emphasizes code readability
    with its notable use of significant indentation. Its language constructs and
    object-oriented approach aim to help programmers write clear, logical code for
    small and large-scale projects.
    """

    print("=" * 60)
    print("TEXT ANALYSIS EXAMPLE")
    print("=" * 60)

    # Character count analysis
    print("\n1. CHARACTER COUNT ANALYSIS")
    print("-" * 60)
    char_analyzer = CharacterAnalyzer(sample_text)
    char_counts = char_analyzer.get_all_counts()
    print(f"Total characters: {char_counts['total']}")
    print(f"Characters (no spaces): {char_counts['no_spaces']}")
    print(f"Alphanumeric characters: {char_counts['alphanumeric']}")
    print(f"Letters: {char_counts['letters']}")
    print(f"Digits: {char_counts['digits']}")
    print(f"Punctuation: {char_counts['punctuation']}")

    # Sentence analysis
    print("\n2. SENTENCE ANALYSIS")
    print("-" * 60)
    sent_analyzer = SentenceAnalyzer(sample_text)
    sentence_stats = sent_analyzer.get_statistics()
    print(f"Total sentences: {sentence_stats['count']}")
    print(f"Average sentence length: {sentence_stats['average_length']} words")
    print(f"Longest sentence: {sentence_stats['longest'][:60]}...")
    print(f"Shortest sentence: {sentence_stats['shortest'][:60]}...")
    print("\nExtracted sentences:")
    for i, sentence in enumerate(sentence_stats["sentences"][:3], 1):
        print(f"  {i}. {sentence[:60]}...")

    # Readability metrics
    print("\n3. READABILITY METRICS")
    print("-" * 60)
    read_analyzer = ReadabilityAnalyzer(sample_text)
    readability = read_analyzer.get_scores()
    print(f"Flesch Reading Ease: {readability['reading_ease']}")
    print(f"  Interpretation: {read_analyzer.interpret_reading_ease()}")
    print("  (90-100: Very Easy, 60-69: Standard, 0-29: Very Confusing)")
    print(f"Flesch-Kincaid Grade Level: {readability['grade_level']}")
    print("  (Indicates US school grade level)")

    # Text statistics
    print("\n4. TEXT STATISTICS")
    print("-" * 60)
    stats_analyzer = StatisticsAnalyzer(sample_text)
    stats = stats_analyzer.get_statistics()
    print(f"Total words: {stats['word_count']}")
    print(f"Unique words: {stats['unique_word_count']}")
    print(f"Average word length: {stats['average_word_length']} characters")
    print(f"Longest word: {stats['longest_word']}")
    print(f"Shortest word: {stats['shortest_word']}")
    print(f"Lexical diversity: {stats['lexical_diversity']}")

    # Word frequency
    print("\nTop 10 most common words:")
    word_freq = stats_analyzer.word_frequency(top_n=10)
    for word, count in word_freq.items():
        print(f"  {word}: {count}")

    # Word length distribution
    print("\nWord length distribution:")
    length_dist = stats_analyzer.word_length_distribution()
    for length, count in list(length_dist.items())[:5]:
        print(f"  {length} characters: {count} words")

    # Language detection
    print("\n5. LANGUAGE DETECTION")
    print("-" * 60)
    lang_analyzer = LanguageAnalyzer(sample_text)
    language = lang_analyzer.detect()
    print(
        f"Detected language: {lang_analyzer.get_language_name()} ({language['language']})"
    )
    print(f"Confidence: {language['confidence']}")
    print(f"Method: {language['method']}")
    print(f"Is likely English: {lang_analyzer.is_likely_language('en')}")

    # Comprehensive analysis using all analyzers
    print("\n6. COMPREHENSIVE ANALYSIS")
    print("-" * 60)
    print("All analyzers used:")
    print("  ✓ CharacterAnalyzer - Character counting")
    print("  ✓ SentenceAnalyzer - Sentence extraction and analysis")
    print("  ✓ ReadabilityAnalyzer - Flesch scores")
    print("  ✓ StatisticsAnalyzer - Word statistics and frequency")
    print("  ✓ LanguageAnalyzer - Language detection")

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
