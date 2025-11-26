from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import User
from accounts.permissions import assign_default_permissions, PERMISSION_CATEGORIES

class Command(BaseCommand):
    help = 'Setup permissions and assign them to existing users'

    def handle(self, *args, **options):
        self.stdout.write('Setting up permissions...')
        
        # Get content type for User model
        content_type = ContentType.objects.get_for_model(User)
        
        # Create all permissions from categories
        created_count = 0
        for category, permissions in PERMISSION_CATEGORIES.items():
            for perm_code, perm_name in permissions:
                # Check if permission already exists
                existing_perms = Permission.objects.filter(codename=perm_code)
                if existing_perms.count() > 1:
                    # Remove duplicates, keep the first one
                    for perm in existing_perms[1:]:
                        perm.delete()
                    self.stdout.write(f'Removed duplicate permissions for: {perm_code}')
                
                permission, created = Permission.objects.get_or_create(
                    codename=perm_code,
                    defaults={
                        'name': perm_name,
                        'content_type': content_type
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'Created permission: {perm_code}')
        
        self.stdout.write(f'Created {created_count} new permissions')
        
        # Assign permissions to existing staff users
        staff_users = User.objects.filter(
            role__in=['Manager', 'Staff', 'Receptionist', 'Housekeeper', 'Maintenance', 'Kitchen', 'Accountant'],
            is_active=True
        )
        
        updated_count = 0
        for user in staff_users:
            try:
                assign_default_permissions(user)
                updated_count += 1
                self.stdout.write(f'Updated permissions for: {user.username} ({user.role})')
            except Exception as e:
                self.stdout.write(f'Error updating permissions for {user.username}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} permissions and updated {updated_count} users')
        )