"""
Setup configuration for TextPrettify.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="textprettify",
    version="1.0.0",
    author="Sajith",
    description="A comprehensive Python library for text formatting, transformation, and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmssajith/TextPrettify",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    keywords="text, string, formatting, slug, whitespace, utility, analysis, readability, statistics, case-conversion, unicode, normalization, text-analysis",
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/mmssajith/TextPrettify/issues",
        "Source": "https://github.com/mmssajith/TextPrettify",
        "Documentation": "https://github.com/mmssajith/TextPrettify#readme",
    },
)
