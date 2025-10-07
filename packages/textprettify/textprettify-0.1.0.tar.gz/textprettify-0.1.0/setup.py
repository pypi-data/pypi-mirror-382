"""
Setup configuration for TextPrettify.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="textprettify",
    version="0.1.0",
    author="Sajith",
    description="A lightweight Python library for text cleaning and formatting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/TextPrettify",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    keywords="text, string, formatting, slug, whitespace, utility",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/TextPrettify/issues",
        "Source": "https://github.com/yourusername/TextPrettify",
    },
)
