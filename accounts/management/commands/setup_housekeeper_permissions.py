from django.core.management.base import BaseCommand
from accounts.models import User
from accounts.role_permissions import apply_housekeeper_permissions

class Command(BaseCommand):
    help = 'Setup permissions for housekeeping staff'

    def handle(self, *args, **options):
        housekeepers = User.objects.filter(role='Housekeeping')
        
        for housekeeper in housekeepers:
            apply_housekeeper_permissions(housekeeper)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated permissions for {housekeeper.get_full_name()}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Updated permissions for {housekeepers.count()} housekeeping staff members'
            )
        )