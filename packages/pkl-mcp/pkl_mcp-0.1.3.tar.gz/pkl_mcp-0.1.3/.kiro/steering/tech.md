# Technology Stack

This is a Python project designed for PyPI package distribution with best practices for development, testing, and deployment.

## Core Technologies
- **Python**: Primary language
- **uv**: Dependency and virtual environment management
- **GitHub**: Private repository with `gh` CLI for repository operations
- **GitHub Actions**: CI/CD workflows for automated testing and deployment

## Build System
- **uv** for dependency management and virtual environment creation
- **build** package for creating distribution packages
- **twine** for uploading to PyPI
- Local builds must mirror GitHub Actions workflows exactly

## Environment Management
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies
uv pip install -e ".[dev]"

# Sync dependencies from lock file
uv pip sync requirements.txt
```

## GitHub CLI Authentication
Before using any `gh` commands, ensure proper authentication:

```bash
# Check current authentication status
gh auth status

# Login with web browser (recommended for private repos)
gh auth login --web

# Login with token (alternative method)
gh auth login --with-token < token.txt

# Verify access to private repositories
gh repo list --limit 5
```

## Common Commands
```bash
# Install project in development mode (creates venv if needed)
uv sync --dev

# Run tests (automatically uses project venv)
uv run pytest

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy .

# Build package
uv run python -m build

# Local build validation (must pass before pushing)
uv run ./scripts/local-build.sh

# Run any Python script/command in project environment
uv run python your_script.py

# GitHub operations (don't require venv)
gh repo create --private
gh pr create
gh workflow run
```

## Code Quality Tools
- **ruff**: Fast Python linter and formatter (replaces flake8, black, isort)
- **mypy**: Static type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks for code quality enforcement

## Dependencies
- Keep runtime dependencies minimal
- Use optional dependencies for development tools: `pip install -e ".[dev]"`
- Pin exact versions in CI/CD, use ranges in package requirements
- Regular dependency updates via Dependabot or manual review

## Development Workflow
1. **Never push without local validation**: All code must pass local build before pushing
2. **Pre-commit hooks**: Automatically run linting and formatting
3. **Type hints**: Required for all public APIs
4. **Test coverage**: Maintain high test coverage for core functionality
5. **Documentation**: Docstrings for all public functions and classes

## CI/CD Requirements
- GitHub Actions workflows for testing across Python versions
- Automated PyPI publishing on tagged releases
- Local build script that mirrors GitHub Actions exactly
- Branch protection requiring status checks to pass