#!/bin/bash

set -e  # Exit on any error

echo "🚀 Starting hotel management deployment..."

# Navigate to project directory
cd /home/ec2-user/hotel_software_deliverable

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Backup current environment file if it exists
if [ -f ".env" ]; then
    cp .env .env.backup
fi

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git fetch origin
git reset --hard origin/main

# Restore environment file
if [ -f ".env.backup" ]; then
    mv .env.backup .env
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create media directories
mkdir -p media/hotel_images media/hotel_icons media/profile_images
chmod 755 media/ media/hotel_images/ media/hotel_icons/ media/profile_images/

# Run database migrations
echo "🗃️ Running database migrations..."
python3 manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python3 manage.py collectstatic --noinput

# Check if services are running, start if not
if ! systemctl is-active --quiet gunicorn; then
    echo "🔧 Starting Gunicorn service..."
    sudo systemctl start gunicorn
else
    echo "🔄 Restarting Gunicorn service..."
    sudo systemctl restart gunicorn
fi

if ! systemctl is-active --quiet nginx; then
    echo "🔧 Starting Nginx service..."
    sudo systemctl start nginx
else
    echo "🔄 Restarting Nginx service..."
    sudo systemctl restart nginx
fi


# Restart Gunicorn (if using)
 sudo systemctl restart gunicorn

# Restart Nginx (if using)
# sudo systemctl restart nginx

echo "Hotel management system deployment completed successfully!"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Set proper permissions for static files
sudo chown -R ec2-user:nginx /home/ec2-user/hotel_management/staticfiles/
sudo chmod -R 755 /home/ec2-user/hotel_management/staticfiles/
# Run health check
echo "🏥 Running health check..."
sleep 5
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Hotel management deployment completed successfully!"
else
    echo "❌ Deployment may have issues. Please check the services."
    exit 1
fi
