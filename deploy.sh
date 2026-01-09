#!/bin/bash

# EC2 Deployment Script for Hotel Management System

echo "🚀 Starting deployment..."

# Update system
sudo apt-get update -y

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create project directory
PROJECT_DIR="/home/ubuntu/hotel-management"
sudo mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clone or update repository
if [ -d ".git" ]; then
    echo "📥 Updating repository..."
    git pull origin master
else
    echo "📥 Cloning repository..."
    git clone https://github.com/Momin9/hotel_management.git .
fi

# Copy production environment
cp .env.production .env

# Update environment variables
echo "⚙️ Please update the following in .env file:"
echo "- SECRET_KEY (generate a new one)"
echo "- ALLOWED_HOSTS (add your domain/IP)"
echo "- CSRF_TRUSTED_ORIGINS (add your domain/IP)"
echo ""
read -p "Press Enter after updating .env file..."

# Build and start containers
echo "🏗️ Building containers..."
sudo docker-compose down
sudo docker-compose build --no-cache

echo "🚀 Starting services..."
sudo docker-compose up -d

# Run migrations
echo "📊 Running database migrations..."
sudo docker-compose exec web python manage.py migrate

# Create superuser (optional)
echo "👤 Create superuser? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    sudo docker-compose exec web python manage.py createsuperuser
fi

# Show status
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your application is running at:"
echo "   HTTP: http://51.20.5.40"
echo ""
echo "📊 Check status: sudo docker-compose ps"
echo "📋 View logs:    sudo docker-compose logs -f"
echo "🔄 Restart:      sudo docker-compose restart"