#!/usr/bin/env bash
# Test with Python 3.8 using Docker

set -e

echo "Testing with Python 3.8 in Docker..."

docker run --rm -v "$(pwd):/app" -w /app python:3.8-slim bash -c "
    pip install --upgrade pip && \
    pip install -e '.[dev,testing]' && \
    echo '================================' && \
    echo 'Running tests with Python 3.8...' && \
    echo '================================' && \
    pytest tests/ -v
"

echo ""
echo "✓ Python 3.8 tests completed!"
