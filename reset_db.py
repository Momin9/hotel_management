#!/usr/bin/env python3
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

# Drop and recreate database
with connection.cursor() as cursor:
    cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
    cursor.execute("CREATE SCHEMA public;")
    cursor.execute("GRANT ALL ON SCHEMA public TO momin-ali;")
    cursor.execute("GRANT ALL ON SCHEMA public TO public;")

print("Database reset complete. Now run migrations manually:")
print("python3 manage.py migrate_schemas --shared")
print("python3 create_public_tenant_simple.py")
print("python3 create_superuser_simple.py")