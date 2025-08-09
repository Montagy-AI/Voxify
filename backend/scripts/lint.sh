#!/bin/bash
set -e
echo "Installing linting tools..."
pip install flake8 black
echo "Running black..."
black_exit=0
black --check . || black_exit=$?
echo "Running flake8..."
flake8_exit=0
flake8 . || flake8_exit=$?  # Changed to . for consistency
echo "Results:"
if [ $black_exit -eq 0 ]; then
    echo "✅ Black: No formatting issues"
else
    echo "❌ Black: Found formatting issues"
fi
if [ $flake8_exit -eq 0 ]; then
    echo "✅ Flake8: No style issues"
else
    echo "❌ Flake8: Found style issues"
fi
# Exit with error if either tool found issues
if [ $black_exit -ne 0 ] || [ $flake8_exit -ne 0 ]; then
    exit 1
fi
echo "✅ All checks passed!"