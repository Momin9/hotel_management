#!/usr/bin/env python3
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from accounts.roles import RoleManager

User = get_user_model()

# Test credentials
email = 'admin@hotel-management.com'
password = 'admin123'

print("Testing login credentials...")
print(f"Email: {email}")
print(f"Password: {password}")
print()

# Check if user exists
try:
    user = User.objects.get(email=email)
    print(f"✓ User found: {user.first_name} {user.last_name}")
    print(f"  - Email: {user.email}")
    role_value = getattr(user, 'role', 'Not set')
    print(f"  - Role: {role_value}")
    print(f"  - Is Active: {user.is_active}")
    print(f"  - Is Staff: {user.is_staff}")
    print(f"  - Is Superuser: {user.is_superuser}")
    print()
    
    # Test authentication
    auth_user = authenticate(username=email, password=password)
    if auth_user:
        print("✓ Authentication successful!")
        try:
            role = RoleManager.get_user_role(auth_user)
            print(f"  - Detected Role: {role}")
        except Exception as e:
            print(f"  - Role detection error: {e}")
    else:
        print("✗ Authentication failed!")
        print("  - Check password or user status")
        
except User.DoesNotExist:
    print("✗ User not found!")
    print("  - Run create_superuser_simple.py to create the user")

print()
print("Login URL: http://127.0.0.1:8000/accounts/login/")
print("Use the email address as username in the login form")