"""
Example: Format blog post metadata using TextPrettify.
"""

from textprettify import (
    remove_extra_whitespace,
    slugify,
    get_reading_time,
    capitalize_words,
    truncate_text,
)


class BlogPost:
    """Simple blog post class demonstrating TextPrettify usage."""

    def __init__(self, title, content, author):
        self.raw_title = title
        self.title = remove_extra_whitespace(capitalize_words(title))
        self.slug = slugify(title)
        self.content = remove_extra_whitespace(content)
        self.author = author
        self.reading_time = get_reading_time(content)
        self.excerpt = truncate_text(content, max_length=150)

    def __str__(self):
        return f"""
{'=' * 70}
Title: {self.title}
Author: {self.author}
URL Slug: {self.slug}
Reading Time: {self.reading_time}
{'=' * 70}

Excerpt:
{self.excerpt}

Full Content:
{self.content}
{'=' * 70}
"""


def main():
    # Sample blog posts with messy formatting
    posts = [
        {
            "title": "  getting   started   with   python  ",
            "content": """
                Python is an amazing programming language.    It's used for web development,
                data science,   machine learning,   and much more.   In this tutorial,
                we'll explore the basics of Python and why it's become one of the most
                popular programming languages in the world.

                We'll cover variables, data types, functions, and control flow. By the end
                of this guide, you'll have a solid foundation to build upon.
            """ * 3,
            "author": "Jane Doe"
        },
        {
            "title": "10  TIPS  FOR  BETTER  CODE  REVIEWS",
            "content": """
                Code reviews are essential for maintaining code quality and sharing knowledge
                within a team. Here are ten practical tips to make your code reviews more
                effective and collaborative.

                First, focus on the code, not the person. Be constructive and specific in
                your feedback. Second, automate what you can - use linters and formatters
                to catch style issues automatically.
            """ * 2,
            "author": "John Smith"
        },
        {
            "title": "understanding   async/await   in   javascript",
            "content": """
                Asynchronous programming in JavaScript has evolved significantly over the years.
                From callbacks to Promises, and now async/await, developers have better tools
                to write clean asynchronous code.

                The async/await syntax makes asynchronous code look and behave more like
                synchronous code, making it easier to read and maintain.
            """ * 4,
            "author": "Sarah Johnson"
        }
    ]

    print("Blog Post Formatter using TextPrettify")
    print("=" * 70)

    for post_data in posts:
        post = BlogPost(
            title=post_data["title"],
            content=post_data["content"],
            author=post_data["author"]
        )
        print(post)
        print()


if __name__ == "__main__":
    main()
