# Hotel Management System

A comprehensive multi-tenant hotel management SaaS platform built with Django.

## Features

### Super Admin Dashboard
- Tenant management and onboarding
- Subscription plan management
- Platform-wide analytics
- Billing and revenue tracking
- Audit logging

### Hotel Owner/Manager Dashboard
- Multi-property management
- Staff management with RBAC
- Room and rate management
- Reservation and booking management
- Financial reporting and analytics
- Guest CRM

### Employee Dashboards
- **Receptionist**: Check-in/out, reservations, guest management
- **Housekeeper**: Room cleaning tasks, status updates
- **Maintenance**: Issue tracking, work orders
- **Chef**: Food orders, kitchen management

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**
   ```bash
   createdb hotel_software
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate_schemas
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start Server**
   ```bash
   python manage.py runserver
   ```

## Access Points

- **Super Admin**: http://localhost:8000/admin
- **Public Landing**: http://localhost:8000
- **Tenant Access**: http://[tenant].localhost:8000

## Architecture

- **Multi-tenant**: Separate schemas per tenant
- **Role-based Access Control**: Granular permissions
- **Modular Design**: Separate apps for each feature
- **Production Ready**: Environment-based configuration

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment
2. Configure proper database credentials
3. Set up Redis for Celery
4. Configure email/SMS providers
5. Set up payment gateway (Stripe)
6. Use gunicorn + nginx

## License

MIT License