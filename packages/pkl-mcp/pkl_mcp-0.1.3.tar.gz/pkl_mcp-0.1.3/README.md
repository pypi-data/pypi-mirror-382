# pkl-mcp

[![CI](https://github.com/username/pkl-mcp/workflows/CI/badge.svg)](https://github.com/username/pkl-mcp/actions)
[![PyPI version](https://badge.fury.io/py/pkl-mcp.svg)](https://badge.fury.io/py/pkl-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/pkl-mcp.svg)](https://pypi.org/project/pkl-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A Python package for MCP (Model Context Protocol) integration with Pkl configuration language.

## Features

- 🚀 **Modern Python**: Built with Python 3.9+ support
- 🔧 **Type Safe**: Full type hints and mypy compatibility
- 🧪 **Well Tested**: Comprehensive test suite with coverage reporting
- 📦 **Easy Installation**: Available on PyPI
- 🛠️ **Developer Friendly**: Pre-commit hooks and automated formatting
- 🔄 **CI/CD Ready**: GitHub Actions workflows included

## Installation

### From PyPI (Recommended)

```bash
pip install pkl-mcp
```

### From Source

```bash
git clone https://github.com/username/pkl-mcp.git
cd pkl-mcp
pip install -e .
```

## Quick Start

### Basic Usage

```python
from pkl_mcp import hello_world

# Simple greeting
message = hello_world()
print(message)  # Output: Hello, World!

# Custom greeting
message = hello_world("Python Developer")
print(message)  # Output: Hello, Python Developer!
```

### Command Line Interface

The package also provides a command-line interface:

```bash
# Run the main function
pkl-mcp

# Or use python -m
python -m pkl_mcp.main
```

## API Documentation

### `hello_world(name: str = "World") -> str`

Returns a greeting message.

**Parameters:**
- `name` (str, optional): The name to greet. Defaults to "World".

**Returns:**
- `str`: A greeting message string.

**Example:**
```python
>>> from pkl_mcp import hello_world
>>> hello_world()
'Hello, World!'
>>> hello_world("Python")
'Hello, Python!'
```

## Development

This project uses modern Python development tools and practices.

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Git](https://git-scm.com/) for version control
- [GitHub CLI](https://cli.github.com/) for repository operations (optional)

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/username/pkl-mcp.git
   cd pkl-mcp
   ```

2. **Set up the development environment:**
   ```bash
   # Create virtual environment and install dependencies
   uv sync --dev

   # Activate the virtual environment (if needed)
   source .venv/bin/activate  # On macOS/Linux
   # .venv\Scripts\activate   # On Windows
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

### Development Workflow

#### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=pkl_mcp

# Run tests in watch mode (for development)
uv run pytest --watch
```

#### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues automatically
uv run ruff check . --fix

# Type checking
uv run mypy .
```

#### Local Build Validation

Before pushing changes, run the complete validation pipeline:

```bash
# Run the local build script (must pass before pushing)
uv run ./scripts/local-build.sh
```

This script runs:
- Dependency synchronization
- Code formatting and linting
- Type checking
- Complete test suite with coverage
- Package building
- Final validation

#### Building the Package

```bash
# Build distribution packages
uv run python -m build

# Check the built packages
uv run twine check dist/*
```

### Project Structure

```
pkl-mcp/
├── src/
│   └── pkl_mcp/           # Main package
│       ├── __init__.py    # Package initialization
│       └── main.py        # Core functionality
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_main.py
├── scripts/               # Build and utility scripts
│   └── local-build.sh     # Local validation script
├── .github/
│   └── workflows/         # GitHub Actions
│       ├── ci.yml         # Continuous Integration
│       └── publish.yml    # PyPI Publishing
├── docs/                  # Documentation
├── pyproject.toml         # Project configuration
├── README.md              # This file
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules
└── .pre-commit-config.yaml # Pre-commit hooks
```

### Configuration

The project uses `pyproject.toml` for all configuration:

- **Build system**: Hatchling
- **Dependencies**: Managed by uv
- **Code formatting**: Ruff
- **Linting**: Ruff
- **Type checking**: MyPy
- **Testing**: Pytest with coverage
- **Pre-commit hooks**: Automated quality checks

### Contributing

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** and add tests
4. **Run the local build**: `uv run ./scripts/local-build.sh`
5. **Commit your changes**: `git commit -am 'Add some feature'`
6. **Push to the branch**: `git push origin feature-name`
7. **Create a Pull Request** on GitHub

### Code Style

This project follows these conventions:

- **PEP 8** compliance via Ruff
- **Type hints** for all public APIs
- **Docstrings** for all public functions and classes
- **Test coverage** of 90% or higher
- **Pre-commit hooks** for automated quality checks

### Release Process

Releases are automated through GitHub Actions:

1. **Create a new tag**: `git tag v1.0.0`
2. **Push the tag**: `git push origin v1.0.0`
3. **GitHub Actions** will automatically:
   - Run the full test suite
   - Build the package
   - Publish to PyPI
   - Create a GitHub release

## Requirements

- Python 3.9+
- No runtime dependencies (currently)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### [0.1.0] - 2024-01-01

- Initial release
- Basic hello_world functionality
- Complete development workflow setup
- CI/CD automation
- PyPI publishing

## Support

- **Issues**: [GitHub Issues](https://github.com/username/pkl-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/pkl-mcp/discussions)
- **Documentation**: [README](https://github.com/username/pkl-mcp#readme)

## Acknowledgments

- Built with [uv](https://docs.astral.sh/uv/) for dependency management
- Code quality powered by [Ruff](https://docs.astral.sh/ruff/)
- Type checking with [MyPy](https://mypy.readthedocs.io/)
- Testing with [Pytest](https://docs.pytest.org/)
- CI/CD with [GitHub Actions](https://github.com/features/actions)
