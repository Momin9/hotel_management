from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from hotels.models import Hotel

User = get_user_model()

class Command(BaseCommand):
    help = 'Check user hotels for debugging'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to check')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"User found: {user.username} ({user.email})")
            self.stdout.write(f"User role: {user.role}")
            self.stdout.write(f"User ID: {user.user_id}")
            
            # Check owned hotels
            owned_hotels = Hotel.objects.filter(owner=user)
            self.stdout.write(f"Owned hotels count: {owned_hotels.count()}")
            
            for hotel in owned_hotels:
                self.stdout.write(f"Hotel: {hotel.name} (ID: {hotel.hotel_id}, Active: {hotel.is_active})")
                
            # Check using related name
            related_hotels = user.owned_hotels.all()
            self.stdout.write(f"Related hotels count: {related_hotels.count()}")
            
            for hotel in related_hotels:
                self.stdout.write(f"Related Hotel: {hotel.name} (ID: {hotel.hotel_id}, Active: {hotel.is_active})")
                
        except User.DoesNotExist:
            self.stdout.write(f"User {username} not found")