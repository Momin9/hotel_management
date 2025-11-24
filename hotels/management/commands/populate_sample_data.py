from django.core.management.base import BaseCommand
from hotels.models import Hotel, Room
from accounts.models import User
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Populate database with sample data for demo'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample hotel owners
        owner1, created = User.objects.get_or_create(
            username='hotel_owner1',
            defaults={
                'email': 'owner1@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'Owner',
                'is_active': True
            }
        )
        if created:
            owner1.set_password('password123')
            owner1.save()
        
        # Create sample hotels
        hotel1, created = Hotel.objects.get_or_create(
            name='Grand Plaza Hotel',
            defaults={
                'owner': owner1,
                'address': '123 Main Street',
                'city': 'New York',
                'country': 'USA',
                'phone': '+1-555-0101',
                'email': 'info@grandplaza.com',
                'is_active': True
            }
        )
        
        # Create sample rooms
        room_types = ['Single', 'Double', 'Twin', 'Triple']
        categories = ['Standard', 'Deluxe', 'Suite']
        bed_types = ['King', 'Queen', 'DoubleBed', 'TwinBed']
        
        for i in range(1, 21):  # Create 20 rooms
            Room.objects.get_or_create(
                hotel=hotel1,
                room_number=f'{100 + i}',
                defaults={
                    'type': random.choice(room_types),
                    'category': random.choice(categories),
                    'bed': random.choice(bed_types),
                    'price': Decimal(str(random.randint(100, 500))),
                    'status': random.choice(['Available', 'Occupied', 'Dirty'])
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(f'Created: {Hotel.objects.count()} Hotels, {Room.objects.count()} Rooms')