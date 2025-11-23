#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    try:
        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            print("Superuser already exists!")
            return
        
        # Create superuser
        superuser = User.objects.create_user(
            username='admin',
            email='admin@hotel.com',
            password='admin123',
            first_name='Super',
            last_name='Admin',
            role='Owner',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        print("Superuser created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Email: admin@hotel.com")
        
    except Exception as e:
        print(f"Error creating superuser: {e}")

if __name__ == "__main__":
    create_superuser()