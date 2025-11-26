from django.core.management.base import BaseCommand
from hotels.models import Hotel

class Command(BaseCommand):
    help = 'List all hotels in the system'

    def handle(self, *args, **options):
        hotels = Hotel.objects.all()
        self.stdout.write(f"Total hotels in system: {hotels.count()}")
        
        for hotel in hotels:
            self.stdout.write(f"Hotel: {hotel.name}")
            self.stdout.write(f"  - ID: {hotel.hotel_id}")
            self.stdout.write(f"  - Owner: {hotel.owner.username} ({hotel.owner.email})")
            self.stdout.write(f"  - Active: {hotel.is_active}")
            self.stdout.write(f"  - Created: {hotel.created_at}")
            self.stdout.write("---")