#!/usr/bin/env python3
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from tenants.models import Client, Domain
from django.contrib.auth import get_user_model

User = get_user_model()

# Get or create public tenant
try:
    public_tenant = Client.objects.get(schema_name='public')
    print("Public tenant already exists")
except Client.DoesNotExist:
    public_tenant = Client(
        schema_name='public',
        name='Public',
        contact_email='admin@system.com',
        is_active=True
    )
    public_tenant.save()
    print("Public tenant created")

# Create domains for public tenant
if not Domain.objects.filter(domain='127.0.0.1').exists():
    domain1 = Domain(
        domain='127.0.0.1',
        tenant=public_tenant,
        is_primary=True
    )
    domain1.save()
    print("Added 127.0.0.1 domain")

if not Domain.objects.filter(domain='localhost').exists():
    domain2 = Domain(
        domain='localhost',
        tenant=public_tenant,
        is_primary=False
    )
    domain2.save()
    print("Added localhost domain")

print("Public tenant created successfully")
print("You can now access: http://127.0.0.1:8000/accounts/login/")