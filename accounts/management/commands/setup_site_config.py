from django.core.management.base import BaseCommand
from accounts.models import SiteConfiguration


class Command(BaseCommand):
    help = 'Create initial site configuration'

    def handle(self, *args, **options):
        config, created = SiteConfiguration.objects.get_or_create(
            pk=1,
            defaults={
                'company_name': 'AuraStay',
                'site_title': 'AuraStay - Hotel Management System',
                'site_description': "The world's most advanced hotel management platform"
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created site configuration')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Site configuration already exists')
            )