#!/bin/bash

# Publish script for Point Topic MCP to PyPI using UV
set -e

# Auto-increment version in pyproject.toml
echo "🔢 Auto-incrementing version..."
CURRENT_VERSION=$(grep "version = " pyproject.toml | sed 's/version = "//' | sed 's/"//')
echo "Current version: $CURRENT_VERSION"

# Parse version (assuming X.Y.Z format)
IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
NEW_PATCH=$((patch + 1))
NEW_VERSION="$major.$minor.$NEW_PATCH"

echo "New version: $NEW_VERSION"

# Update pyproject.toml
sed -i '' "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Get token from .pypirc if it exists
if [ -f "$HOME/.pypirc" ]; then
    echo "📄 Reading token from ~/.pypirc..."
    PYPI_TOKEN=$(grep "password = " ~/.pypirc | sed 's/.*password = //' | tr -d ' ')
    if [ -z "$PYPI_TOKEN" ]; then
        echo "❌ Could not find token in ~/.pypirc"
        exit 1
    fi
else
    echo "❌ No ~/.pypirc file found!"
    echo "Set up your PyPI credentials first"
    exit 1
fi

echo "🧹 Cleaning old dist files..."
rm -rf dist/

echo "🔨 Building package with UV..."
uv build

echo "📦 Built package files:"
ls -la dist/

echo "🚀 Uploading to PyPI with UV..."
uv publish --token "$PYPI_TOKEN"

echo "✅ Successfully published to PyPI!"
echo ""
echo "Users can now install with:"
echo "  pip install point-topic-mcp"
echo ""
echo "Or specify the new version to ensure you get the latest:"
echo "  pip install point-topic-mcp==$NEW_VERSION"
echo ""
echo "And use with:"
echo "  point-topic-mcp"
