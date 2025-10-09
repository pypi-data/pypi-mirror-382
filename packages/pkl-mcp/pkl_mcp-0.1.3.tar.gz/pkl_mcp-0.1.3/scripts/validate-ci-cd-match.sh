#!/bin/bash

# Validate that local build script matches CI/CD behavior
set -e

echo "🔍 Validating local build script matches CI/CD workflow..."

# Check if GitHub workflow file exists
if [[ ! -f ".github/workflows/publish.yml" ]]; then
    echo "❌ GitHub workflow file not found"
    exit 1
fi

echo "✅ GitHub workflow file found"

# Extract key steps from both files for comparison
echo "ℹ️ Comparing workflow steps..."

echo "📋 Local build script steps:"
grep -E "^==> |^ℹ️" scripts/local-build.sh | head -10

echo ""
echo "📋 CI/CD workflow steps:"
grep -E "name:|run:" .github/workflows/publish.yml | head -20

# Verify both use the same tools
echo ""
echo "🔧 Tool verification:"

# Check if both use ruff
if grep -q "ruff" scripts/local-build.sh && grep -q "ruff" .github/workflows/publish.yml; then
    echo "✅ Both use ruff for linting and formatting"
else
    echo "⚠️ Ruff usage mismatch between local and CI/CD"
fi

# Check if both use mypy
if grep -q "mypy" scripts/local-build.sh && grep -q "mypy" .github/workflows/publish.yml; then
    echo "✅ Both use mypy for type checking"
else
    echo "⚠️ MyPy usage mismatch between local and CI/CD"
fi

# Check if both use pytest
if grep -q "pytest" scripts/local-build.sh && grep -q "pytest" .github/workflows/publish.yml; then
    echo "✅ Both use pytest for testing"
else
    echo "⚠️ Pytest usage mismatch between local and CI/CD"
fi

# Check if both use build
if grep -q "build" scripts/local-build.sh && grep -q "build" .github/workflows/publish.yml; then
    echo "✅ Both use build for package creation"
else
    echo "⚠️ Build tool usage mismatch between local and CI/CD"
fi

# Check if both use twine
if grep -q "twine" scripts/local-build.sh && grep -q "twine" .github/workflows/publish.yml; then
    echo "✅ Both use twine for package validation"
else
    echo "⚠️ Twine usage mismatch between local and CI/CD"
fi

echo ""
echo "✅ CI/CD workflow validation completed!"