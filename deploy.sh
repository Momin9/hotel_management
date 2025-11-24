#!/bin/bash

# Deployment script for Hotel Management Django application

echo "Starting hotel management system deployment..."

# Navigate to project directory
cd /home/momin-ali/Projects/Django/hotel_software_deliverable

# Activate virtual environment
source .venv/bin/activate

# Pull latest changes from GitHub
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run database migrations
python3 manage.py migrate

# Collect static files
python3 manage.py collectstatic --noinput

# Create media directories if they don't exist
mkdir -p media/hotel_images
mkdir -p media/hotel_icons
mkdir -p media/profile_images

# Set proper permissions
chmod 755 media/
chmod 755 media/hotel_images/
chmod 755 media/hotel_icons/
chmod 755 media/profile_images/

# Restart Gunicorn (if using)
 sudo systemctl restart gunicorn

# Restart Nginx (if using)
# sudo systemctl restart nginx

echo "Hotel management system deployment completed successfully!"
