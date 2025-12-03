from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.role_permissions import RolePermissions

User = get_user_model()

class Command(BaseCommand):
    help = 'Apply role-based permissions to all existing users'

    def handle(self, *args, **options):
        users = User.objects.filter(role__isnull=False)
        updated_count = 0
        
        for user in users:
            if user.role in RolePermissions.ROLE_PERMISSIONS:
                RolePermissions.apply_role_permissions(user)
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Applied {user.role} permissions to {user.email}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} users')
        )