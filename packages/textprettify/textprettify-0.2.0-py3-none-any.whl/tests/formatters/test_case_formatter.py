"""Tests for CaseFormatter class."""

from textprettify import CaseFormatter


class TestCaseConversions:
    def test_to_snake_case(self):
        formatter = CaseFormatter("Hello World")
        assert formatter.to_snake_case() == "hello_world"

    def test_to_snake_case_from_camel(self):
        formatter = CaseFormatter("helloWorld")
        assert formatter.to_snake_case() == "hello_world"

    def test_to_snake_case_from_pascal(self):
        formatter = CaseFormatter("HelloWorld")
        assert formatter.to_snake_case() == "hello_world"

    def test_to_camel_case(self):
        formatter = CaseFormatter("hello world")
        assert formatter.to_camel_case() == "helloWorld"

    def test_to_camel_case_from_snake(self):
        formatter = CaseFormatter("hello_world_example")
        assert formatter.to_camel_case() == "helloWorldExample"

    def test_to_pascal_case(self):
        formatter = CaseFormatter("hello world")
        assert formatter.to_pascal_case() == "HelloWorld"

    def test_to_pascal_case_from_snake(self):
        formatter = CaseFormatter("hello_world_example")
        assert formatter.to_pascal_case() == "HelloWorldExample"

    def test_to_constant_case(self):
        formatter = CaseFormatter("hello world")
        assert formatter.to_constant_case() == "HELLO_WORLD"

    def test_to_constant_case_from_camel(self):
        formatter = CaseFormatter("helloWorld")
        assert formatter.to_constant_case() == "HELLO_WORLD"

    def test_to_kebab_case(self):
        formatter = CaseFormatter("Hello World")
        assert formatter.to_kebab_case() == "hello-world"

    def test_to_kebab_case_from_camel(self):
        formatter = CaseFormatter("helloWorld")
        assert formatter.to_kebab_case() == "hello-world"

    def test_to_title_case(self):
        formatter = CaseFormatter("the lord of the rings")
        result = formatter.to_title_case(exceptions=["the", "of"])
        assert result == "The Lord of the Rings"
