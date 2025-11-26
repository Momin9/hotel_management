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

### 👥 Employee Dashboards

#### 🏨 **Front Desk (Receptionist)**
- Guest check-in/check-out processing
- Reservation management and modifications
- Room assignment and status updates
- Guest services and requests handling
- Folio management and billing

#### 🧹 **Housekeeping**
- Room cleaning task assignments
- Room status updates (Clean, Dirty, Maintenance)
- Inventory usage tracking
- Maintenance issue reporting
- Task scheduling and completion tracking

#### 🔧 **Maintenance**
- Work order management
- Issue tracking and resolution
- Preventive maintenance scheduling
- Equipment and asset management
- Vendor coordination

#### 👨‍🍳 **Kitchen/Restaurant (Chef)**
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

### Integrations
- **Stripe** - Payment processing
- **Twilio** - SMS notifications
- **SendGrid** - Email services
- **AWS S3** - File storage (via django-storages)
- **ReportLab** - PDF generation

### Development Tools
- **Django REST Framework** - API development
- **Django Debug Toolbar** - Development debugging
- **Faker** - Test data generation
- **Gunicorn** - WSGI server for production
- **WhiteNoise** - Static file serving

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

6. **Run Development Setup**
   ```bash
   chmod +x setup_dev.sh
   ./setup_dev.sh
   ```

7. **Run Migrations**
   ```bash
   python manage.py migrate_schemas
   ```

8. **Create Superuser**
   ```bash
   python manage.py createsuperuser
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
| **Accounts** | User management and authentication | Multi-role support, profile management |
| **Hotels** | Property and room management | Multi-property, room types, pricing |
| **Reservations** | Booking and reservation system | Calendar view, availability checking |
| **Front Desk** | Check-in/out operations | Guest services, folio management |
| **Housekeeping** | Room maintenance and cleaning | Task assignment, status tracking |
| **CRM** | Guest relationship management | Guest profiles, history, preferences |
| **Billing** | Financial management | Invoicing, payments, reporting |
| **Inventory** | Stock and supply management | Item tracking, usage monitoring |
| **POS** | Point of sale system | Menu management, order processing |
| **Reporting** | Analytics and insights | Revenue reports, occupancy analytics |
| **Maintenance** | Facility management | Work orders, asset tracking |
| **Staff** | Employee management | Scheduling, performance tracking |
| **Notifications** | Communication system | Real-time alerts, messaging |

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
   python manage.py migrate_schemas --shared
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Credits

**Design**: MA Qureshi  
**Development**: Momin Ali

---

## 📞 Support

For support and inquiries:
- 📧 Email: support@aurastay.com
- 📱 Phone: +1 (555) 123-4567
- 🌐 Website: https://aurastay.com

---

*Built with ❤️ for the hospitality industry*