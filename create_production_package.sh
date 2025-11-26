#!/bin/bash

# Create Production Package for AuraStay
echo "📦 Creating production deployment package..."

# Create deployment directory
mkdir -p production_deployment
cd production_deployment

# Copy essential files
echo "📋 Copying essential files..."
cp ../website_data_export.json .
cp ../setup_production_data.sh .
cp ../requirements.txt .
cp -r ../accounts/management .

# Create README for production deployment
cat > README_PRODUCTION.md << 'EOF'
# AuraStay Production Deployment

## Quick Setup Instructions

1. **Upload files to production server:**
   - `website_data_export.json` (contains all website data)
   - `setup_production_data.sh` (setup script)
   - `requirements.txt` (dependencies)
   - `management/` folder (Django commands)

2. **Run setup script:**
   ```bash
   chmod +x setup_production_data.sh
   ./setup_production_data.sh
   ```

3. **What gets created:**
   - Superuser account (admin/admin123)
   - Complete footer and company information
   - About Us page with full content
   - All landing page features (12 features)
   - Page titles and descriptions (30+ pages)
   - Site configuration
   - Subscription plans (8 plans: Free, Basic, Premium, etc.)
   - Terms of Service and Privacy Policy with rich content
   - All website branding and content

4. **Default Admin Credentials:**
   - Username: `admin`
   - Password: `admin123`
   - Email: `admin@aurastay.com`

5. **⚠️ IMPORTANT SECURITY:**
   - Change admin password immediately after first login
   - Update email settings in Django settings
   - Configure proper SECRET_KEY for production
   - Set DEBUG=False in production

## Manual Setup (Alternative)

If the script doesn't work, run these commands manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Populate website data
python manage.py populate_website_data
```

## Data Included

### Website Content:
- ✅ Company branding (AuraStay)
- ✅ Footer with contact information
- ✅ About Us page with mission, vision, features
- ✅ Landing page features and descriptions
- ✅ All page titles and subtitles
- ✅ Terms of Service and Privacy Policy

### Subscription Plans:
- ✅ Free Plan (20 rooms, $0/month)
- ✅ Basic Plan (25 rooms, $30/month)
- ✅ Premium Plan (100 rooms, $70/month)
- ✅ Enterprise Plan (500 rooms, $199/month)
- ✅ Luxury Plan (2000 rooms, $399/month)
- ✅ And more...

### Features Included:
- ✅ Reservation Management
- ✅ Guest Management & CRM
- ✅ Staff Management
- ✅ Analytics & Reports
- ✅ Housekeeping Management
- ✅ Billing & Payments
- ✅ Mobile Access
- ✅ Security & Compliance

## Support

For issues or questions:
- Email: info@aurastay.com
- Check Django admin at `/admin/` after setup
EOF

echo "✅ Production package created in 'production_deployment' folder"
echo ""
echo "📁 Package contents:"
echo "   • website_data_export.json (all website data)"
echo "   • setup_production_data.sh (automated setup)"
echo "   • requirements.txt (Python dependencies)"
echo "   • management/ (Django commands)"
echo "   • README_PRODUCTION.md (setup instructions)"
echo ""
echo "🚀 Ready for production deployment!"
echo "📤 Upload the 'production_deployment' folder to your server"