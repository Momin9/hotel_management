#!/bin/bash
echo "Cleaning up repository..."

# Remove Python cache files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete

# Remove IDE files
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".idea" -type d -exec rm -rf {} + 2>/dev/null

# Remove OS files
find . -name ".DS_Store" -delete
find . -name "Thumbs.db" -delete

# Remove coverage files
find . -name ".coverage" -delete
find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null

echo "Cleanup complete!"
