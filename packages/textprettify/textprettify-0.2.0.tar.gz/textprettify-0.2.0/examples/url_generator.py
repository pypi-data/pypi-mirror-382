"""
Example: Generate clean URLs from various text inputs.
"""

from textprettify import BasicFormatter


class URLGenerator:
    """Generate clean, SEO-friendly URLs from text."""

    def __init__(self, base_url="https://example.com"):
        self.base_url = base_url.rstrip("/")

    def generate_blog_url(self, title, category="blog"):
        """Generate a URL for a blog post."""
        formatter = BasicFormatter(title)
        clean_title = formatter.remove_extra_whitespace()
        slug = BasicFormatter(clean_title).slugify()
        return f"{self.base_url}/{category}/{slug}"

    def generate_product_url(self, product_name, product_id):
        """Generate a URL for a product page."""
        formatter = BasicFormatter(product_name)
        slug = formatter.slugify()
        return f"{self.base_url}/products/{slug}-{product_id}"

    def generate_user_profile_url(self, username):
        """Generate a URL for a user profile."""
        formatter = BasicFormatter(username)
        slug = formatter.slugify(separator="")
        return f"{self.base_url}/users/{slug}"

    def generate_search_url(self, query):
        """Generate a URL for search results."""
        formatter = BasicFormatter(query)
        slug = formatter.slugify(separator="+")
        return f"{self.base_url}/search?q={slug}"


def main():
    print("=" * 70)
    print("URL Generator Examples")
    print("=" * 70)

    generator = URLGenerator("https://myblog.com")

    # Blog post URLs
    print("\n1. Blog Post URLs:")
    blog_titles = [
        "How to Learn Python in 2024",
        "My Journey into Data Science!",
        "10 Tips for Better Code Reviews",
        "Understanding Async/Await in JavaScript",
    ]
    for title in blog_titles:
        url = generator.generate_blog_url(title)
        print(f"   {title}")
        print(f"   → {url}\n")

    # Product URLs
    print("\n2. Product URLs:")
    products = [
        ("Wireless Bluetooth Headphones - Premium Quality", "12345"),
        ("Mechanical Gaming Keyboard (RGB)", "67890"),
        ("USB-C Hub: 7-in-1 Adapter", "24680"),
    ]
    for product_name, product_id in products:
        url = generator.generate_product_url(product_name, product_id)
        print(f"   {product_name}")
        print(f"   → {url}\n")

    # User profile URLs
    print("\n3. User Profile URLs:")
    usernames = ["John Doe", "Sarah_Smith_123", "Developer@2024"]
    for username in usernames:
        url = generator.generate_user_profile_url(username)
        print(f"   {username}")
        print(f"   → {url}\n")

    # Search URLs
    print("\n4. Search URLs:")
    queries = [
        "Python tutorials for beginners",
        "Best practices: REST API design",
        "Machine learning with TensorFlow",
    ]
    for query in queries:
        url = generator.generate_search_url(query)
        print(f"   {query}")
        print(f"   → {url}\n")

    # Advanced example: Generate sitemap-friendly URLs
    print("\n5. Category + Subcategory URLs:")
    generator_advanced = URLGenerator("https://shop.example.com")

    categories = [
        ("Electronics", "Laptops & Computers", "Gaming Laptop - RTX 4090"),
        ("Clothing", "Men's Fashion", "Casual T-Shirt (100% Cotton)"),
        ("Books", "Programming", "Clean Code: A Handbook of Agile Craftsmanship"),
    ]

    for category, subcategory, item in categories:
        cat_slug = BasicFormatter(category).slugify()
        subcat_slug = BasicFormatter(subcategory).slugify()
        item_slug = BasicFormatter(item).slugify()
        url = f"{generator_advanced.base_url}/{cat_slug}/{subcat_slug}/{item_slug}"
        print(f"   {category} > {subcategory} > {item}")
        print(f"   → {url}\n")

    print("=" * 70)


if __name__ == "__main__":
    main()
