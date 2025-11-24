from django.core.management.base import BaseCommand
from tenants.models import Client, Domain, TenantSettings

class Command(BaseCommand):
    help = 'Create a new tenant with domain'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Tenant name')
        parser.add_argument('domain', type=str, help='Domain name (without .localhost)')
        parser.add_argument('email', type=str, help='Contact email')
        parser.add_argument('--plan', type=str, default='basic', help='Subscription plan')

    def handle(self, *args, **options):
        # Create tenant
        tenant = Client.objects.create(
            name=options['name'],
            contact_email=options['email'],
            subscription_plan=options['plan']
        )
        
        # Create domain
        domain = Domain.objects.create(
            domain=f"{options['domain']}.localhost",
            tenant=tenant,
            is_primary=True
        )
        
        # Create default settings
        TenantSettings.objects.create(tenant=tenant)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created tenant "{tenant.name}" with domain "{domain.domain}"'
            )
        )