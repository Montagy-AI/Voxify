#!/bin/bash
set -e

echo "Installing linting tools..."
npm install --save-dev eslint prettier @eslint/js

echo "Running ESLint..."
eslint_exit=0
npx eslint src/ || eslint_exit=$?

echo "Running Prettier check..."
prettier_exit=0
npx prettier --check src/ || prettier_exit=$?

echo "Results:"
if [ $eslint_exit -eq 0 ]; then
    echo "✅ ESLint: No linting issues"
else
    echo "❌ ESLint: Found linting issues"
fi

if [ $prettier_exit -eq 0 ]; then
    echo "✅ Prettier: No formatting issues"
else
    echo "❌ Prettier: Found formatting issues"
fi

# Exit with error if either tool found issues
if [ $eslint_exit -ne 0 ] || [ $prettier_exit -ne 0 ]; then
    exit 1
fi

echo "✅ All frontend checks passed!"