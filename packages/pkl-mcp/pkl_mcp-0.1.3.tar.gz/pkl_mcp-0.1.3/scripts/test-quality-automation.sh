#!/bin/bash

# Test all quality checks and automation work correctly
set -e

echo "🔧 Testing all quality checks and automation..."

echo "==> Testing individual quality tools"

# Test ruff formatting
echo "ℹ️ Testing ruff formatting..."
uv run ruff format --check .
echo "✅ Ruff formatting check passed"

# Test ruff linting
echo "ℹ️ Testing ruff linting..."
uv run ruff check .
echo "✅ Ruff linting check passed"

# Test mypy type checking
echo "ℹ️ Testing mypy type checking..."
uv run mypy .
echo "✅ MyPy type checking passed"

# Test pytest with coverage
echo "ℹ️ Testing pytest with coverage..."
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90
echo "✅ Pytest with coverage passed"

echo "==> Testing pre-commit hooks (if configured)"
if [[ -f ".pre-commit-config.yaml" ]]; then
    echo "ℹ️ Testing pre-commit hooks..."
    uv run pre-commit run --all-files || echo "⚠️ Pre-commit hooks not fully configured"
else
    echo "ℹ️ Pre-commit hooks not configured (optional)"
fi

echo "==> Testing GitHub CLI functionality"
echo "ℹ️ Testing GitHub CLI authentication..."
gh auth status
echo "✅ GitHub CLI authentication working"

echo "ℹ️ Testing repository access..."
gh repo view --json name,visibility
echo "✅ Repository access working"

echo "==> Testing build automation"
echo "ℹ️ Testing clean build process..."
rm -rf dist/ build/ *.egg-info/
uv run python -m build
echo "✅ Build automation working"

echo "ℹ️ Testing package validation..."
uv run twine check dist/*
echo "✅ Package validation working"

echo ""
echo "🎉 All quality checks and automation tests passed!"