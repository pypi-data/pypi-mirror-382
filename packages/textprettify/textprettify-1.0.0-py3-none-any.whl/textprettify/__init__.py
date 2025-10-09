"""
TextPrettify - A mini-library for text cleaning and formatting.

Provides class-based utilities to manipulate, format, and analyze text strings.
"""

from .formatters import (
    BasicFormatter,
    CaseFormatter,
    TransformationFormatter,
    GenerationFormatter,
    NormalizationFormatter,
)
from .analyzers import (
    CharacterAnalyzer,
    SentenceAnalyzer,
    ReadabilityAnalyzer,
    StatisticsAnalyzer,
    LanguageAnalyzer,
)

__version__ = "0.1.0"
__all__ = [
    # Formatters
    "BasicFormatter",
    "CaseFormatter",
    "TransformationFormatter",
    "GenerationFormatter",
    "NormalizationFormatter",
    # Analyzers
    "CharacterAnalyzer",
    "SentenceAnalyzer",
    "ReadabilityAnalyzer",
    "StatisticsAnalyzer",
    "LanguageAnalyzer",
]
