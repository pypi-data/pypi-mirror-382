# Design Document

## Overview

This design establishes a complete Python PyPI package development workflow using modern tooling and best practices. The solution uses `uv` for dependency management, `ruff` for linting/formatting, `mypy` for type checking, `pytest` for testing, and GitHub Actions for CI/CD. The design emphasizes local-first development where all checks must pass locally before pushing to GitHub.

## Architecture

### Project Structure
```
project-root/
├── src/
│   └── pkl_mcp/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── scripts/
│   └── local-build.sh
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── publish.yml
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
└── .ruff.toml
```

### Tool Chain Integration
- **uv**: Primary dependency manager and virtual environment handler
- **ruff**: Combined linter and formatter (replaces black, flake8, isort)
- **mypy**: Static type checking
- **pytest**: Testing framework with coverage reporting
- **pre-commit**: Git hooks for automated quality checks
- **GitHub Actions**: CI/CD automation
- **GitHub CLI**: Repository management

## Components and Interfaces

### 1. Package Configuration (pyproject.toml)
**Purpose**: Central configuration for package metadata, dependencies, and tool settings

**Key Sections**:
- `[build-system]`: Uses modern build backend (hatchling or setuptools)
- `[project]`: Package metadata, dependencies, entry points
- `[project.optional-dependencies]`: Development dependencies
- `[tool.ruff]`: Linting and formatting configuration
- `[tool.mypy]`: Type checking configuration
- `[tool.pytest]`: Test configuration
- `[tool.coverage]`: Coverage reporting settings

### 2. Source Package Structure
**Purpose**: Clean, importable Python package with proper __init__.py

**Components**:
- `src/pkl_mcp/__init__.py`: Package initialization and public API
- `src/pkl_mcp/main.py`: Core functionality with example "hello world" implementation
- Type hints throughout for mypy compatibility

### 3. Testing Framework
**Purpose**: Comprehensive test coverage with pytest

**Components**:
- `tests/test_main.py`: Unit tests for core functionality
- `tests/__init__.py`: Test package initialization
- Coverage reporting integrated with pytest
- Test discovery and execution via `uv run pytest`

### 4. Code Quality Pipeline
**Purpose**: Automated code quality enforcement

**Local Tools**:
- `ruff check .`: Linting with auto-fix capabilities
- `ruff format .`: Code formatting
- `mypy .`: Static type checking
- `pre-commit`: Git hooks running all quality checks

**Integration Points**:
- Pre-commit hooks prevent commits with quality issues
- Local build script runs complete quality pipeline
- CI/CD mirrors local quality checks exactly

### 5. Local Build System
**Purpose**: Complete validation before pushing to GitHub

**Script**: `scripts/local-build.sh`
**Steps**:
1. Environment setup and dependency sync
2. Code formatting and linting
3. Type checking
4. Test execution with coverage
5. Package building
6. Final validation report

### 6. GitHub Integration
**Purpose**: Automated CI/CD with GitHub Actions

**Workflows**:
- `ci.yml`: Runs on push/PR, tests multiple Python versions
- `publish.yml`: Triggered by release tags, publishes to PyPI

**GitHub CLI Integration**:
- Repository creation and management
- Pull request workflows
- Authentication verification

### 7. PyPI Publishing
**Purpose**: Automated package distribution

**Components**:
- Build system creates wheel and source distributions
- GitHub Actions handles secure PyPI publishing
- Version management through git tags
- Automated release notes generation

## Data Models

### Package Metadata
```python
# pyproject.toml structure
[project]
name: str
version: str
description: str
authors: List[Dict[str, str]]
dependencies: List[str]
requires-python: str
classifiers: List[str]
```

### Development Dependencies
```python
[project.optional-dependencies]
dev: List[str]  # ruff, mypy, pytest, pre-commit, build, twine
```

### Tool Configurations
```python
[tool.ruff]
line-length: int
target-version: str
select: List[str]  # Rule categories
ignore: List[str]  # Ignored rules

[tool.mypy]
python_version: str
strict: bool
warn_return_any: bool
```

## Error Handling

### Local Development Errors
- **Dependency conflicts**: uv provides clear resolution messages
- **Quality check failures**: Pre-commit hooks show specific issues and fixes
- **Type errors**: mypy provides detailed error locations and suggestions
- **Test failures**: pytest shows detailed failure information with coverage gaps

### CI/CD Error Handling
- **Build failures**: GitHub Actions provide detailed logs and artifact uploads
- **Publishing errors**: Secure token validation and clear PyPI error messages
- **Version conflicts**: Automated version checking prevents duplicate releases

### Recovery Strategies
- **Failed local build**: Step-by-step error resolution with tool-specific fixes
- **CI/CD failures**: Local reproduction of CI environment for debugging
- **Publishing issues**: Manual override capabilities with proper authentication

## Testing Strategy

### Unit Testing
- **Framework**: pytest with coverage reporting
- **Scope**: All public functions and methods
- **Coverage Target**: >90% for core functionality
- **Test Organization**: Mirror source structure in tests/

### Integration Testing
- **Local Build**: Complete workflow testing via local-build.sh
- **CI/CD Testing**: Multi-version Python testing in GitHub Actions
- **Package Testing**: Installation and import testing of built packages

### Quality Assurance
- **Static Analysis**: mypy for type safety
- **Code Style**: ruff for consistent formatting and linting
- **Security**: Basic security linting via ruff security rules
- **Documentation**: Docstring validation and README accuracy

### Test Automation
- **Pre-commit**: Automated quality checks on every commit
- **CI Pipeline**: Automated testing on push and pull requests
- **Release Testing**: Automated package building and publishing validation

## Implementation Phases

### Phase 1: Project Foundation
- Create basic project structure
- Configure pyproject.toml with metadata and dependencies
- Set up src/ package with hello world functionality

### Phase 2: Development Environment
- Configure uv for dependency management
- Set up ruff, mypy, and pytest configurations
- Create basic test suite

### Phase 3: Quality Pipeline
- Implement pre-commit hooks
- Create local build validation script
- Configure all quality tools integration

### Phase 4: CI/CD Automation
- Create GitHub Actions workflows
- Configure PyPI publishing automation
- Set up GitHub CLI integration

### Phase 5: Documentation and Polish
- Complete README with usage examples
- Add comprehensive docstrings
- Final testing and validation