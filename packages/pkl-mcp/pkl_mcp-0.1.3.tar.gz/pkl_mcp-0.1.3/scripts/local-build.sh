#!/bin/bash

# Local build validation script for pkl-mcp package
# This script runs the complete quality pipeline that mirrors CI/CD exactly
# Requirements: 5.1, 5.2, 5.3, 5.4, 5.5

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}==>${NC} ${1}"
}

print_success() {
    echo -e "${GREEN}✅${NC} ${1}"
}

print_error() {
    echo -e "${RED}❌${NC} ${1}"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} ${1}"
}

print_info() {
    echo -e "${CYAN}ℹ️${NC} ${1}"
}

# Start build validation
echo -e "${PURPLE}🚀 Starting local build validation for pkl-mcp...${NC}"
echo ""

# Validate environment
print_step "Validating build environment"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Ensure we're in the project root
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Run this script from the project root."
    exit 1
fi

# Check for required tools
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install uv first."
    exit 1
fi

# Check GitHub CLI authentication (optional but recommended)
print_info "Checking GitHub CLI authentication..."
if command -v gh &> /dev/null; then
    if gh auth status 2>&1 | grep -q "Active account: true"; then
        print_success "GitHub CLI is authenticated"
    else
        print_warning "GitHub CLI is not authenticated. Run 'gh auth login' to enable GitHub operations."
        print_info "GitHub operations will be unavailable until authentication is complete."
    fi
else
    print_warning "GitHub CLI (gh) is not installed. Install it to enable GitHub operations."
    print_info "Visit: https://cli.github.com/ for installation instructions."
fi

print_success "Environment validation passed"
echo ""

# Step 1: Dependency sync and environment setup
print_step "Setting up environment and syncing dependencies"
print_info "Creating virtual environment and installing dependencies..."

# Sync dependencies (creates venv if needed)
if ! uv sync --dev; then
    print_error "Failed to sync dependencies"
    exit 1
fi

print_success "Dependencies synced successfully"
echo ""

# Step 2: Code formatting
print_step "Running code formatting with ruff"
print_info "Formatting Python code..."

if ! uv run ruff format .; then
    print_error "Code formatting failed"
    exit 1
fi

print_success "Code formatting completed"
echo ""

# Step 3: Linting checks
print_step "Running linting checks with ruff"
print_info "Checking code quality and style..."

if ! uv run ruff check . --fix; then
    print_error "Linting checks failed"
    exit 1
fi

print_success "Linting checks passed"
echo ""

# Step 4: Type checking
print_step "Running static type checking with mypy"
print_info "Analyzing type annotations..."

if ! uv run mypy .; then
    print_error "Type checking failed"
    exit 1
fi

print_success "Type checking passed"
echo ""

# Step 5: Test execution with coverage
print_step "Running test suite with coverage"
print_info "Executing tests and measuring coverage..."

if ! uv run pytest; then
    print_error "Test suite failed"
    exit 1
fi

print_success "All tests passed with required coverage"
echo ""

# Step 6: Package building
print_step "Building package distributions"
print_info "Creating wheel and source distributions..."

# Clean previous builds
if [ -d "dist" ]; then
    rm -rf dist/
    print_info "Cleaned previous build artifacts"
fi

if ! uv run python -m build; then
    print_error "Package building failed"
    exit 1
fi

print_success "Package built successfully"
echo ""

# Step 7: Package validation
print_step "Validating built packages"
print_info "Checking package integrity..."

# Check if build artifacts exist
if [ ! -d "dist" ] || [ -z "$(ls -A dist/)" ]; then
    print_error "No build artifacts found in dist/"
    exit 1
fi

# Count and validate artifacts
wheel_count=$(find dist/ -name "*.whl" | wc -l)
sdist_count=$(find dist/ -name "*.tar.gz" | wc -l)

if [ "$wheel_count" -eq 0 ]; then
    print_error "No wheel distribution found"
    exit 1
fi

if [ "$sdist_count" -eq 0 ]; then
    print_error "No source distribution found"
    exit 1
fi

print_info "Found $wheel_count wheel(s) and $sdist_count source distribution(s)"

# Validate package metadata using twine
print_info "Validating package metadata..."
if ! uv run twine check dist/*; then
    print_error "Package validation failed"
    exit 1
fi

print_success "Package validation passed"
echo ""

# Step 8: Final validation report
print_step "Generating final validation report"

echo ""
echo -e "${GREEN}🎉 LOCAL BUILD VALIDATION SUCCESSFUL! 🎉${NC}"
echo ""
echo "Build Summary:"
echo "=============="
echo "✅ Environment setup and dependency sync"
echo "✅ Code formatting (ruff format)"
echo "✅ Linting checks (ruff check)"
echo "✅ Type checking (mypy)"
echo "✅ Test suite execution with coverage"
echo "✅ Package building (wheel + source)"
echo "✅ Package validation (twine check)"
echo ""
echo -e "${CYAN}📦 Build Artifacts:${NC}"
ls -la dist/
echo ""
echo -e "${GREEN}🚀 Code is ready for push to GitHub!${NC}"
echo -e "${CYAN}💡 Next steps:${NC}"
echo "   - git add ."
echo "   - git commit -m \"Your commit message\""
echo "   - git push"
echo ""

# Optional: Show git status
if git status --porcelain | grep -q .; then
    print_warning "You have uncommitted changes:"
    git status --short
    echo ""
fi

exit 0