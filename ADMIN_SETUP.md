# Enhanced Super Admin Dashboard Setup

This document provides instructions for setting up and using the enhanced Super Admin Dashboard for the Hotel Management System.

## Features Implemented

### Super Admin Dashboard
- **Hotel List View**: Display all hotels with search and filter options
- **Hotel Detail View**: Comprehensive hotel information including owner, subscription, and staff
- **User Management**: Manage all users across the platform with role-based permissions
- **Subscription Management**: Create and manage subscription plans with features and pricing
- **Real-time Metrics**: Dashboard showing system-wide statistics
- **Activity Logging**: Track important system activities (framework ready)

### Key Functionalities

#### 1. Hotel Management
- View all hotels with filtering by status, subscription plan, and search
- Detailed hotel information including owner, subscription status, and statistics
- Ability to activate/suspend hotels
- Manage hotel subscriptions and plans

#### 2. User Role Management
- Comprehensive user list with role-based filtering
- Create, edit, and manage users across all hotels
- Role-based permission system
- User activation/deactivation

#### 3. Subscription Management
- Create and manage subscription plans
- Set pricing, limits, and features for each plan
- Track subscription analytics and revenue
- Plan activation/deactivation

#### 4. Enhanced Login System
- Role-based login interface
- Super Admin portal emphasis
- Secure authentication with role redirection

## Setup Instructions

### 1. Database Setup
Since there were migration conflicts, you may need to reset the database:

```bash
# Remove existing migration files (if needed)
find . -name "0002_*.py" -path "*/migrations/*" -delete
find . -name "0003_*.py" -path "*/migrations/*" -delete

# Create fresh migrations
python manage.py makemigrations
python manage.py migrate
```

### 2. Run Setup Script
```bash
python3 setup_admin_system.py
```

This will create:
- Default subscription plans (Basic, Professional, Enterprise)
- Super admin user
- Demo hotel with owner

### 3. Access the System

#### Super Admin Login
- URL: `/accounts/login/`
- Email: `admin@hotel-management.com`
- Password: `admin123`

#### Hotel Owner Login (Demo)
- Email: `owner@demo-hotel.com`
- Password: `owner123`

## URL Structure

### Super Admin URLs
- `/accounts/super-admin/` - Main dashboard
- `/accounts/manage-hotels/` - Hotel management
- `/accounts/hotel/<hotel_id>/` - Hotel detail view
- `/accounts/manage-users/` - User management
- `/accounts/manage-subscriptions/` - Subscription management

### Authentication
- `/accounts/login/` - Enhanced login page
- `/accounts/logout/` - Logout
- `/accounts/dashboard/` - Role-based dashboard redirect

## Model Updates

### User Model Enhancements
- Added `role` field with predefined choices
- Added `hotel` relationship for staff assignment
- Added `phone` and `permissions` fields
- Enhanced role-based properties

### Hotel Model Enhancements
- Added `owner` relationship
- Added subscription management fields
- Added status tracking
- Added computed properties for statistics

### New Features Ready for Implementation
- Payment history tracking
- Activity logging system
- Advanced analytics
- Bulk operations
- Export functionality

## Security Features

### Role-Based Access Control
- Super Admin: Full system access
- Hotel Owner: Hotel-specific management
- Hotel Manager: Limited hotel operations
- Staff: Role-specific permissions

### Permission System
- Granular permissions stored in JSON format
- Role-based default permissions
- Custom permission assignment capability

## Next Steps

1. **Test the System**: Use the provided login credentials to test all features
2. **Customize Styling**: Modify templates to match your brand
3. **Add Real Data**: Replace demo data with actual hotels and users
4. **Implement APIs**: Add REST API endpoints for mobile apps
5. **Add Analytics**: Implement detailed reporting and analytics
6. **Payment Integration**: Add payment processing for subscriptions

## Troubleshooting

### Migration Issues
If you encounter migration conflicts:
1. Delete migration files: `find . -name "*.py" -path "*/migrations/*" ! -name "__init__.py" -delete`
2. Recreate migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`

### Template Issues
Ensure all template files are in the correct locations:
- `templates/accounts/dashboards/super_admin.html`
- `templates/accounts/admin_dashboard/hotels.html`
- `templates/accounts/admin_dashboard/hotel_detail.html`
- `templates/accounts/admin_dashboard/users.html`
- `templates/accounts/admin_dashboard/subscriptions.html`

### Static Files
Run `python manage.py collectstatic` if styling appears broken.

## Support

For issues or questions about the enhanced admin system, refer to the code comments and model documentation. The system is designed to be extensible and customizable for your specific needs.