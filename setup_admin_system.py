#!/usr/bin/env python3
"""
Setup script for the enhanced admin system
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import SubscriptionPlan
from hotels.models import Hotel

User = get_user_model()

def create_subscription_plans():
    """Create default subscription plans"""
    plans = [
        {
            'name': 'Basic',
            'description': 'Perfect for small hotels',
            'price': 29.99,
            'billing_cycle': 'monthly',
            'max_properties': 1,
            'max_rooms': 50,
            'features': {
                'online_reservations': True,
                'basic_reports': True,
                'email_support': True,
            }
        },
        {
            'name': 'Professional',
            'description': 'Ideal for growing hotel businesses',
            'price': 79.99,
            'billing_cycle': 'monthly',
            'max_properties': 3,
            'max_rooms': 200,
            'features': {
                'online_reservations': True,
                'advanced_reports': True,
                'api_access': True,
                'priority_support': True,
                'integrations': True,
            }
        },
        {
            'name': 'Enterprise',
            'description': 'For large hotel chains',
            'price': 199.99,
            'billing_cycle': 'monthly',
            'max_properties': 10,
            'max_rooms': 1000,
            'features': {
                'online_reservations': True,
                'advanced_reports': True,
                'api_access': True,
                'priority_support': True,
                'integrations': True,
                'custom_branding': True,
                'dedicated_support': True,
            }
        }
    ]
    
    for plan_data in plans:
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            print(f"Created subscription plan: {plan.name}")
        else:
            print(f"Subscription plan already exists: {plan.name}")

def create_super_admin():
    """Create super admin user"""
    email = 'admin@hotel-management.com'
    password = 'admin123'
    
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Super',
            last_name='Admin'
        )
        user.role = 'super_admin'
        user.save()
        print(f"Created super admin: {email} / {password}")
    else:
        print("Super admin already exists")

def create_demo_hotel():
    """Create a demo hotel"""
    # Create hotel owner
    owner_email = 'owner@demo-hotel.com'
    if not User.objects.filter(email=owner_email).exists():
        owner = User.objects.create_user(
            email=owner_email,
            password='owner123'
        )
        owner.first_name = 'John'
        owner.last_name = 'Doe'
        owner.phone = '+1234567890'
        owner.role = 'hotel_owner'
        owner.save()
        print(f"Created hotel owner: {owner_email} / owner123")
    else:
        owner = User.objects.get(email=owner_email)
        print("Hotel owner already exists")
    
    # Create demo hotel
    if not Hotel.objects.filter(name='Demo Luxury Hotel').exists():
        basic_plan = SubscriptionPlan.objects.get(name='Basic')
        hotel = Hotel.objects.create(
            name='Demo Luxury Hotel',
            address='123 Luxury Street, Hotel City, HC 12345',
            phone='+1234567890',
            email='info@demo-hotel.com',
            owner=owner,
            subscription_plan=basic_plan,
            subscription_status='trial'
        )
        print(f"Created demo hotel: {hotel.name}")
    else:
        print("Demo hotel already exists")

def main():
    """Main setup function"""
    print("Setting up enhanced admin system...")
    
    try:
        create_subscription_plans()
        create_super_admin()
        create_demo_hotel()
        
        print("\n" + "="*50)
        print("Setup completed successfully!")
        print("="*50)
        print("Super Admin Login:")
        print("Email: admin@hotel-management.com")
        print("Password: admin123")
        print("\nHotel Owner Login:")
        print("Email: owner@demo-hotel.com") 
        print("Password: owner123")
        print("="*50)
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()