from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django_tenants.utils import schema_context

class Command(BaseCommand):
    help = 'Create demo users for testing'

    def handle(self, *args, **options):
        with schema_context('demo'):
            # Create owner user
            owner, created = User.objects.get_or_create(
                username='owner@demo.com',
                email='owner@demo.com',
                defaults={
                    'first_name': 'Demo',
                    'last_name': 'Owner',
                    'is_staff': False,
                    'is_active': True,
                }
            )
            if created:
                owner.set_password('demo123')
                owner.save()
                self.stdout.write(self.style.SUCCESS('Demo owner created: owner@demo.com / demo123'))
            else:
                self.stdout.write('Demo owner already exists')
            
            # Create staff user
            staff, created = User.objects.get_or_create(
                username='staff@demo.com',
                email='staff@demo.com',
                defaults={
                    'first_name': 'Demo',
                    'last_name': 'Staff',
                    'is_staff': True,
                    'is_active': True,
                }
            )
            if created:
                staff.set_password('demo123')
                staff.save()
                self.stdout.write(self.style.SUCCESS('Demo staff created: staff@demo.com / demo123'))
            else:
                self.stdout.write('Demo staff already exists')