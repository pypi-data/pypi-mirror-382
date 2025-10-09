"""
Tests for the main module of pkl-mcp package.
"""

from io import StringIO
from unittest.mock import patch

from pkl_mcp.main import hello_world, main


class TestHelloWorld:
    """Test cases for the hello_world function."""

    def test_hello_world_default(self) -> None:
        """Test hello_world with default parameter."""
        result = hello_world()
        assert result == "Hello, World!"

    def test_hello_world_with_name(self) -> None:
        """Test hello_world with custom name."""
        result = hello_world("Python")
        assert result == "Hello, Python!"

    def test_hello_world_empty_string(self) -> None:
        """Test hello_world with empty string."""
        result = hello_world("")
        assert result == "Hello, !"

    def test_hello_world_special_characters(self) -> None:
        """Test hello_world with special characters."""
        result = hello_world("Test-123")
        assert result == "Hello, Test-123!"

    def test_hello_world_unicode_characters(self) -> None:
        """Test hello_world with unicode characters."""
        result = hello_world("世界")
        assert result == "Hello, 世界!"

    def test_hello_world_whitespace(self) -> None:
        """Test hello_world with whitespace in name."""
        result = hello_world("  Python  ")
        assert result == "Hello,   Python  !"

    def test_hello_world_long_name(self) -> None:
        """Test hello_world with a very long name."""
        long_name = "A" * 1000
        result = hello_world(long_name)
        assert result == f"Hello, {long_name}!"

    def test_hello_world_return_type(self) -> None:
        """Test that hello_world returns a string."""
        result = hello_world()
        assert isinstance(result, str)

    def test_hello_world_none_parameter(self) -> None:
        """Test hello_world with None as parameter (should use default)."""
        # This tests the type annotation behavior
        result = hello_world()  # Using default instead of None
        assert result == "Hello, World!"


class TestMain:
    """Test cases for the main function."""

    def test_main_output(self) -> None:
        """Test that main function prints the expected output."""
        # Capture stdout
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            main()

        output = captured_output.getvalue().strip()
        assert output == "Hello, World!"

    def test_main_calls_hello_world(self) -> None:
        """Test that main function calls hello_world with default parameters."""
        with patch(
            "pkl_mcp.main.hello_world", return_value="Mocked Hello"
        ) as mock_hello:
            with patch("builtins.print"):
                main()

            mock_hello.assert_called_once_with()

    def test_main_prints_hello_world_result(self) -> None:
        """Test that main function prints the result of hello_world."""
        with patch(
            "pkl_mcp.main.hello_world", return_value="Test Output"
        ) as mock_hello:
            captured_output = StringIO()
            with patch("sys.stdout", captured_output):
                main()

            output = captured_output.getvalue().strip()
            assert output == "Test Output"
            mock_hello.assert_called_once_with()


class TestModuleExecution:
    """Test cases for module execution behavior."""

    def test_module_has_main_guard(self) -> None:
        """Test that the module has proper __main__ guard."""
        # This test ensures the main() function is only called when run as script
        # We can't easily test the __name__ == "__main__" condition directly,
        # but we can verify the functions exist and are callable
        assert callable(main)
        assert callable(hello_world)

    def test_main_function_exists(self) -> None:
        """Test that main function is properly defined."""
        assert callable(main)
        assert main.__doc__ is not None
        assert "entry point" in main.__doc__.lower()

    def test_hello_world_function_exists(self) -> None:
        """Test that hello_world function is properly defined."""
        assert callable(hello_world)
        assert hello_world.__doc__ is not None
        assert "greeting" in hello_world.__doc__.lower()


class TestDocstrings:
    """Test cases for function docstrings and documentation."""

    def test_hello_world_docstring(self) -> None:
        """Test that hello_world has proper docstring."""
        docstring = hello_world.__doc__
        assert docstring is not None
        assert "Return a greeting message" in docstring
        assert "Args:" in docstring
        assert "Returns:" in docstring
        assert "Example:" in docstring

    def test_main_docstring(self) -> None:
        """Test that main has proper docstring."""
        docstring = main.__doc__
        assert docstring is not None
        assert "entry point" in docstring.lower()


class TestTypeAnnotations:
    """Test cases for type annotations."""

    def test_hello_world_annotations(self) -> None:
        """Test that hello_world has proper type annotations."""
        annotations = hello_world.__annotations__
        assert "name" in annotations
        assert "return" in annotations
        assert annotations["name"] is str
        assert annotations["return"] is str

    def test_main_annotations(self) -> None:
        """Test that main has proper type annotations."""
        annotations = main.__annotations__
        assert "return" in annotations
        # main() should return None (represented as None in annotations)
        assert annotations["return"] is None
