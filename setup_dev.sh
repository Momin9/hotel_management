#!/bin/bash
echo "Setting up development environment..."

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from template. Please update with your actual values."
else
    echo ".env already exists."
fi

# Create necessary directories
mkdir -p media/ tenant_logos/ staticfiles/

# Set proper permissions
chmod 755 media/ tenant_logos/ staticfiles/

echo "Setup complete!"
