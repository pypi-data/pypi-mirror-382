"""
Main module for pkl-mcp package.

This module contains the core functionality of the package.
Pre-commit hooks are now configured.
"""


def hello_world(name: str = "World") -> str:
    """
    Return a greeting message.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        A greeting message string.

    Example:
        >>> hello_world()
        'Hello, World!'
        >>> hello_world("Python")
        'Hello, Python!'
    """
    return f"Hello, {name}!"


def main() -> None:
    """
    Main entry point for the package when run as a script.
    """
    print(hello_world())


if __name__ == "__main__":
    main()
