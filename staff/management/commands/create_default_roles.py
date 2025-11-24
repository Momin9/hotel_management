from django.core.management.base import BaseCommand
from staff.models import Role

class Command(BaseCommand):
    help = 'Create default staff roles'

    def handle(self, *args, **options):
        roles = [
            {'name': 'Manager', 'description': 'Hotel Manager with full access'},
            {'name': 'Front Desk Agent', 'description': 'Front desk operations'},
            {'name': 'Housekeeper', 'description': 'Room cleaning and maintenance'},
            {'name': 'Maintenance Staff', 'description': 'Property maintenance'},
            {'name': 'Security', 'description': 'Security and safety'},
            {'name': 'Concierge', 'description': 'Guest services'},
        ]
        
        for role_data in roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.name}')
                )
            else:
                self.stdout.write(f'Role already exists: {role.name}')