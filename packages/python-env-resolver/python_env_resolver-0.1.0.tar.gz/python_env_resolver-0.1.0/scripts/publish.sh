#!/bin/bash
set -e

echo "🚀 Publishing python-env-resolver to PyPI"
echo ""

# Check if we're on main branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "❌ Error: You must be on the main branch to publish"
    echo "   Current branch: $BRANCH"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ Error: You have uncommitted changes"
    echo "   Commit or stash your changes before publishing"
    exit 1
fi

# Get version from pyproject.toml
VERSION=$(grep -m1 'version = ' pyproject.toml | cut -d'"' -f2)
echo "📦 Version: $VERSION"
echo ""

# Check if tag already exists
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "❌ Error: Git tag v$VERSION already exists"
    echo "   Update the version in pyproject.toml first"
    exit 1
fi

# Run tests
echo "🧪 Running tests..."
pytest
echo "✅ Tests passed"
echo ""

# Type check
echo "🔍 Type checking..."
mypy src
echo "✅ Type check passed"
echo ""

# Lint
echo "🎨 Linting..."
ruff check .
echo "✅ Linting passed"
echo ""

# Clean old builds
echo "🧹 Cleaning old builds..."
rm -rf dist/ build/ *.egg-info
echo ""

# Build
echo "📦 Building package..."
python -m build
echo "✅ Package built"
echo ""

# Check distribution
echo "🔍 Checking distribution..."
twine check dist/*
echo "✅ Distribution looks good"
echo ""

# Offer to publish to TestPyPI first
read -p "📤 Publish to TestPyPI first? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Publishing to TestPyPI..."
    twine upload --repository testpypi dist/*
    echo ""
    echo "✅ Published to TestPyPI"
    echo "🔗 View at: https://test.pypi.org/project/python-env-resolver/$VERSION/"
    echo ""
    echo "To test installation:"
    echo "  pip install --index-url https://test.pypi.org/simple/ python-env-resolver==$VERSION"
    echo ""
    read -p "Continue to PyPI? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Final confirmation
echo "⚠️  About to publish to PyPI (this cannot be undone)"
read -p "Are you sure? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

# Publish to PyPI
echo "📤 Publishing to PyPI..."
twine upload dist/*
echo ""
echo "✅ Published to PyPI!"
echo "🔗 View at: https://pypi.org/project/python-env-resolver/$VERSION/"
echo ""

# Create git tag
echo "🏷️  Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION"
echo ""

# Push tag
read -p "📤 Push tag to GitHub? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin "v$VERSION"
    echo "✅ Tag pushed to GitHub"
    echo ""
    echo "🎉 All done! Create a release on GitHub to announce it:"
    echo "   https://github.com/jagreehal/python-env-resolver/releases/new?tag=v$VERSION"
fi

echo ""
echo "🎉 Publishing complete!"
