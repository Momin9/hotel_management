#!/usr/bin/env python3
import os
import re

# List of files to fix
files_to_fix = [
    'front_desk/models.py',
    'inventory/models.py', 
    'notifications/models.py',
    'pos/models.py',
    'reporting/models.py',
]

base_dir = '/home/momin-ali/Projects/Django/hotel_software_deliverable'

for file_path in files_to_fix:
    full_path = os.path.join(base_dir, file_path)
    if os.path.exists(full_path):
        print(f"Fixing {file_path}...")
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Replace imports
        content = re.sub(
            r'from django\.contrib\.auth\.models import User',
            'from django.conf import settings',
            content
        )
        
        # Replace ForeignKey references
        content = re.sub(
            r'models\.ForeignKey\(User,',
            'models.ForeignKey(settings.AUTH_USER_MODEL,',
            content
        )
        
        # Replace OneToOneField references
        content = re.sub(
            r'models\.OneToOneField\(User,',
            'models.OneToOneField(settings.AUTH_USER_MODEL,',
            content
        )
        
        # Replace ManyToManyField references
        content = re.sub(
            r'models\.ManyToManyField\(User,',
            'models.ManyToManyField(settings.AUTH_USER_MODEL,',
            content
        )
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Fixed {file_path}")
    else:
        print(f"✗ File not found: {file_path}")

print("Done!")