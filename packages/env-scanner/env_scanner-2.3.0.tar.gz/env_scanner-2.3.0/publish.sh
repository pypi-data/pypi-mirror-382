#!/bin/bash
# Simple publishing script for env-scanner

set -e  # Exit on error

echo "🚀 Publishing env-scanner to PyPI"
echo "=================================="

# Check if build and twine are installed
if ! command -v twine &> /dev/null; then
    echo "📦 Installing build tools..."
    pip install --upgrade build twine
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# Run tests
echo "🧪 Running tests..."
python3 -m pytest tests/ -v --tb=short
if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Fix them before publishing."
    exit 1
fi

# Build package
echo "🔨 Building package..."
python3 -m build

# Check package
echo "✅ Checking package..."
twine check dist/*
if [ $? -ne 0 ]; then
    echo "❌ Package check failed!"
    exit 1
fi

# Ask which repository to upload to
echo ""
echo "Where do you want to upload?"
echo "1) Test PyPI (recommended first)"
echo "2) Production PyPI"
echo "3) Cancel"
read -p "Choose (1/2/3): " choice

case $choice in
    1)
        echo "📤 Uploading to Test PyPI..."
        twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Uploaded to Test PyPI!"
        echo "Install with: pip install --index-url https://test.pypi.org/simple/ env-scanner"
        ;;
    2)
        read -p "⚠️  Upload to PRODUCTION PyPI? This cannot be undone! (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "📤 Uploading to Production PyPI..."
            twine upload dist/*
            echo ""
            echo "✅ Published to PyPI!"
            echo "Install with: pip install env-scanner"
            echo "View at: https://pypi.org/project/env-scanner/"
        else
            echo "❌ Cancelled."
            exit 1
        fi
        ;;
    3)
        echo "❌ Cancelled."
        exit 0
        ;;
    *)
        echo "❌ Invalid choice."
        exit 1
        ;;
esac

echo ""
echo "🎉 Done!"

