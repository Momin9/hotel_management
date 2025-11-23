#!/usr/bin/env python3
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Fix superuser
email = 'admin@hotel-management.com'
password = 'admin123'

try:
    user = User.objects.get(email=email)
    print(f"Found user: {user.email}")
    
    # Reset password
    user.set_password(password)
    
    # Ensure all required fields are set
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    
    # Set role if field exists
    if hasattr(user, 'role'):
        user.role = 'super_admin'
        print("Set role to super_admin")
    
    user.save()
    print("✓ User updated successfully!")
    print(f"Email: {user.email}")
    print(f"Password: {password}")
    print(f"Is Active: {user.is_active}")
    print(f"Is Staff: {user.is_staff}")
    print(f"Is Superuser: {user.is_superuser}")
    
    # Test authentication
    from django.contrib.auth import authenticate
    auth_user = authenticate(username=email, password=password)
    if auth_user:
        print("✓ Authentication test successful!")
    else:
        print("✗ Authentication test failed!")
        
except User.DoesNotExist:
    print("User not found, creating new one...")
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name='Super',
        last_name='Admin',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    if hasattr(user, 'role'):
        user.role = 'super_admin'
        user.save()
    print("✓ New superuser created!")