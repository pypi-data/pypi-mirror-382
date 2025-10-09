#!/bin/bash

# Test package installation and import functionality
set -e

echo "🧪 Testing package installation and import functionality..."

# Create a temporary directory for testing
TEST_DIR=$(mktemp -d)
echo "ℹ️ Using temporary directory: $TEST_DIR"

# Copy the built package to test directory
cp dist/pkl_mcp-0.1.0-py3-none-any.whl "$TEST_DIR/"

# Create a fresh virtual environment for testing
echo "ℹ️ Creating fresh test environment..."
cd "$TEST_DIR"
python -m venv test_env
source test_env/bin/activate

# Install the package
echo "ℹ️ Installing package from wheel..."
pip install pkl_mcp-0.1.0-py3-none-any.whl

# Test import functionality
echo "ℹ️ Testing package import..."
python -c "
import pkl_mcp
print('✅ Successfully imported pkl_mcp')
print(f'Package version: {getattr(pkl_mcp, \"__version__\", \"unknown\")}')

# Test main functionality
from pkl_mcp.main import hello_world
result = hello_world()
print(f'✅ Function call successful: {result}')

# Test CLI entry point if it exists
import subprocess
try:
    result = subprocess.run(['pkl-mcp', '--help'], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print('✅ CLI entry point working')
    else:
        print('ℹ️ CLI entry point not configured or not working')
except Exception as e:
    print(f'ℹ️ CLI test skipped: {e}')
"

# Deactivate and cleanup
deactivate
cd - > /dev/null
rm -rf "$TEST_DIR"

echo "✅ Package installation and import test completed successfully!"