# AuraStay - Hotel Management System

🏨 **A comprehensive multi-tenant hotel management SaaS platform built with Django**

*Design by MA Qureshi | Developed by Momin Ali*

---

## 🌟 Overview

AuraStay is a modern, cloud-based hotel management platform designed to streamline operations for hotels of all sizes. Built with Django and featuring a multi-tenant architecture, it provides separate environments for each hotel while maintaining centralized administration.

## ✨ Key Features

### 🔧 Super Admin Dashboard
- **Multi-tenant Management**: Complete tenant lifecycle management
- **Subscription Plans**: Flexible pricing tiers (Basic, Premium, Enterprise)
- **Analytics & Reporting**: Platform-wide insights and metrics
- **Billing System**: Automated billing and payment tracking
- **User Management**: Hotel owner and staff administration
- **System Configuration**: Global settings and customization

### 🏢 Hotel Owner/Manager Dashboard
- **Property Management**: Multi-property support with centralized control
- **Staff Management**: Role-based access control (RBAC) system
- **Room Management**: Room types, categories, pricing, and availability
- **Reservation System**: Advanced booking management with calendar view
- **Guest CRM**: Complete guest profile and history management
- **Financial Reports**: Revenue tracking, occupancy rates, and analytics
- **Inventory Control**: Stock management for hotel supplies
- **Configuration Management**: Room types, categories, bed types, floors, and amenities
- **Bulk Import**: CSV-based bulk import for configurations

### 👥 Employee Dashboards

#### 🏨 **Front Desk (Receptionist)**
- Guest check-in/check-out processing
- Reservation management and modifications
- Room assignment and status updates
- Guest services and requests handling
- Folio management and billing

#### 🧹 **Housekeeping**
- Room cleaning task assignments
- Room status updates (Clean, Dirty, Maintenance, Out of Order)
- Inventory usage tracking
- Maintenance issue reporting
- Task scheduling and completion tracking
- Kanban and list view for room management

#### 🔧 **Maintenance**
- Work order management
- Issue tracking and resolution
- Preventive maintenance scheduling
- Equipment and asset management
- Vendor coordination

#### 👨🍳 **Kitchen/Restaurant (Chef)**
- Menu management and pricing
- Order processing and tracking
- Inventory management for food items
- POS system integration
- Revenue tracking for F&B operations

## 🛠️ Technology Stack

### Backend
- **Django 4.2.16** - Web framework
- **PostgreSQL** - Primary database with multi-tenant support
- **Redis** - Caching and session storage
- **Celery** - Background task processing
- **Django Tenants** - Multi-tenancy implementation

### Frontend
- **TailwindCSS** - Modern utility-first CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **Font Awesome** - Icon library
- **Inter Font** - Modern typography

### Data Processing & Export
- **Pandas 2.0.3** - Data analysis and manipulation
- **OpenPyXL 3.1.2** - Excel file processing
- **XlsxWriter 3.1.9** - Excel file generation
- **ReportLab 4.1.0** - PDF generation

### Integrations
- **Stripe 8.7.0** - Payment processing
- **Twilio 8.10.0** - SMS notifications
- **Django Countries 7.5.1** - Country and phone field support
- **Django CKEditor 5** - Rich text editing

### Development Tools
- **Django REST Framework 3.14.0** - API development
- **Django Extensions 3.2.3** - Development utilities
- **Faker 20.1.0** - Test data generation
- **Gunicorn 21.2.0** - WSGI server for production
- **WhiteNoise 6.6.0** - Static file serving

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis Server
- Git

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd hotel_software_deliverable
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Database**
   ```bash
   createdb hotel_software
   ```

5. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database and service credentials
   ```

6. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Generate CSV Template (Optional)**
   ```bash
   python create_excel_template.py
   ```

9. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

## 🌐 Access Points

- **Public Landing Page**: http://localhost:8000
- **Super Admin Panel**: http://localhost:8000/admin
- **Hotel Dashboard**: http://localhost:8000/dashboard
- **API Documentation**: http://localhost:8000/api/docs
- **Bulk Import**: http://localhost:8000/configurations/bulk-import/

## 🏗️ Architecture

### Multi-Tenant Design
- **Schema-based Tenancy**: Each hotel gets its own database schema
- **Shared Public Schema**: Common data like subscription plans
- **Tenant Isolation**: Complete data separation between hotels
- **Scalable Infrastructure**: Supports unlimited tenants

### Security Features
- **Role-Based Access Control (RBAC)**: Granular permissions system
- **JWT Authentication**: Secure API access
- **Data Encryption**: Sensitive data protection
- **Audit Logging**: Complete activity tracking
- **CSRF Protection**: Cross-site request forgery prevention

### Performance Optimizations
- **Database Indexing**: Optimized query performance
- **Redis Caching**: Fast data retrieval
- **Static File Optimization**: CDN-ready asset management
- **Background Tasks**: Asynchronous processing with Celery

## 📱 Core Modules

| Module | Description | Key Features |
|--------|-------------|-------------|
| **Accounts** | User management and authentication | Multi-role support, profile management, permissions |
| **Hotels** | Property and room management | Multi-property, room types, pricing, activity logs |
| **Configurations** | System configuration management | Room types, categories, bed types, floors, amenities, bulk import |
| **Reservations** | Booking and reservation system | Calendar view, availability checking, expense tracking |
| **Front Desk** | Check-in/out operations | Guest services, folio management, room assignments |
| **Housekeeping** | Room maintenance and cleaning | Task assignment, status tracking, scheduling, kanban view |
| **CRM** | Guest relationship management | Guest profiles, history, preferences, company contracts |
| **Billing** | Financial management | Invoicing, payments, reporting, tax configuration |
| **Inventory** | Stock and supply management | Item tracking, usage monitoring, categories |
| **POS** | Point of sale system | Menu management, order processing, minibar items |
| **Reporting** | Analytics and insights | Revenue reports, occupancy analytics, custom dashboards |
| **Maintenance** | Facility management | Work orders, asset tracking, issue resolution |
| **Staff** | Employee management | Scheduling, performance tracking, role management |
| **Notifications** | Communication system | Real-time alerts, messaging, system notifications |

## 🔧 Configuration Management

### Bulk Import System
- **CSV Format**: Unified CSV format for all configuration types
- **Template Download**: Built-in template generator with sample data
- **Duplicate Handling**: Automatically skips existing configurations
- **Error Handling**: Comprehensive validation and error reporting
- **Supported Types**: Room Types, Room Categories, Bed Types, Floors, Amenities

### Configuration Types
- **Room Types**: Standard Room, Deluxe, Suite, Presidential Suite, etc.
- **Room Categories**: Economy, Business, Premium, Luxury with occupancy limits
- **Bed Types**: Single, Double, Queen, King, Twin, Bunk, Sofa Bed, etc.
- **Floors**: Ground Floor, numbered floors, Mezzanine, Penthouse, Basement
- **Amenities**: Wi-Fi, AC, TV, Mini Bar, Balcony, Safe, etc. with FontAwesome icons

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   export DEBUG=False
   export ALLOWED_HOSTS=yourdomain.com
   export DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

2. **Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Database Migration**
   ```bash
   python manage.py migrate
   ```

4. **Web Server (Gunicorn + Nginx)**
   ```bash
   gunicorn hotelmanagement.wsgi:application --bind 0.0.0.0:8000
   ```

### Docker Deployment
```bash
docker-compose up -d
```

## 📊 Subscription Plans

| Plan | Price | Rooms | Features |
|------|-------|-------|----------|
| **Basic** | $29/month | Up to 25 | Core features, basic reporting |
| **Premium** | $79/month | Up to 100 | Advanced analytics, priority support |
| **Enterprise** | $199/month | Unlimited | All features, custom integrations |

## 🆕 Recent Updates

### Version 2.1.0 - Configuration Management Enhancement
- ✅ **CSV Bulk Import System**: Replace Excel with CSV format for better compatibility
- ✅ **Room Category Model**: New model with max occupancy field
- ✅ **Bed Type Usage Field**: Added usage descriptions for bed types
- ✅ **Dynamic Amenity Selection**: Interactive amenity selection in room forms
- ✅ **Room Activity Logging**: Comprehensive room activity tracking
- ✅ **Luxury UI Components**: Beautiful modals and enhanced user interface
- ✅ **Alphabetical Ordering**: Consistent alphabetical sorting across all lists
- ✅ **Navigation Integration**: Bulk import accessible from configurations dropdown

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨💻 Credits

**Design**: MA Qureshi  
**Development**: Momin Ali

---

## 📞 Support

For support and inquiries:
- 📧 Email: mominalikhoker589@gmail.com
- 📱 Phone: +923144506620
- 🌐 Website:   

---

*Built with ❤️ for the hospitality industry*