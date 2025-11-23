#!/usr/bin/env python3
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create super admin
email = 'admin@hotel-management.com'
password = 'admin123'

if not User.objects.filter(email=email).exists():
    user = User(
        email=email,
        first_name='Super',
        last_name='Admin',
        role='super_admin',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    user.set_password(password)
    user.save()
    print(f"Super admin created: {email} / {password}")
else:
    # Update existing user to ensure it has the correct role
    user = User.objects.get(email=email)
    user.role = 'super_admin'
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    print("Super admin already exists - updated role and permissions")

print("Access: http://127.0.0.1:8000/accounts/login/")