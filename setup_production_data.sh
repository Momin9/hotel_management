#!/bin/bash

# Production Data Setup Script for AuraStay
# This script populates all website-related data excluding hotels, owners, staff, rooms, reservations

echo "🚀 Starting AuraStay Production Data Setup..."
echo "================================================"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
elif [ -d "env" ]; then
    echo "📦 Activating virtual environment..."
    source env/bin/activate
else
    echo "⚠️  No virtual environment found. Make sure to install dependencies."
fi

# Install/Update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Copy website data export if exists
if [ -f "website_data_export.json" ]; then
    echo "📄 Found website data export file"
else
    echo "⚠️  No export file found, will use default data"
fi

# Populate website data
echo "🌐 Populating website data..."
python manage.py populate_website_data

echo ""
echo "✅ Production setup completed successfully!"
echo "================================================"
echo "📋 What was created:"
echo "   • Superuser account (admin/admin123)"
echo "   • Footer content and company information"
echo "   • About Us page content"
echo "   • Page titles and descriptions"
echo "   • Feature listings for landing page"
echo "   • Site configuration"
echo "   • Subscription plans (Starter, Professional, Enterprise, Premium)"
echo "   • Terms of Service and Privacy Policy"
echo ""
echo "🔐 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   Email: admin@aurastay.com"
echo ""
echo "⚠️  IMPORTANT: Change the admin password after first login!"
echo "🌍 Your AuraStay installation is ready for production use."