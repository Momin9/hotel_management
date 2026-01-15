from django.core.management.base import BaseCommand
from hotels.models import Hotel, Service
from configurations.models import Amenity

class Command(BaseCommand):
    help = 'Create sample amenities and services for hotels'

    def add_arguments(self, parser):
        parser.add_argument('--hotel-id', type=str, help='Hotel ID to add amenities and services to')

    def handle(self, *args, **options):
        hotel_id = options.get('hotel_id')
        
        if hotel_id:
            try:
                hotel = Hotel.objects.get(hotel_id=hotel_id)
                hotels = [hotel]
            except Hotel.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Hotel with ID {hotel_id} not found'))
                return
        else:
            hotels = Hotel.objects.all()

        # Sample amenities
        amenity_data = [
            {'name': 'Free Wi-Fi', 'icon': 'fas fa-wifi', 'description': 'High-speed internet access'},
            {'name': 'Air Conditioning', 'icon': 'fas fa-snowflake', 'description': 'Climate control'},
            {'name': 'Mini Bar', 'icon': 'fas fa-glass-martini', 'description': 'In-room refreshments'},
            {'name': 'Safe', 'icon': 'fas fa-lock', 'description': 'Personal safe for valuables'},
            {'name': 'TV', 'icon': 'fas fa-tv', 'description': 'Flat screen television'},
            {'name': 'Balcony', 'icon': 'fas fa-door-open', 'description': 'Private balcony with view'},
        ]

        # Sample services
        service_data = [
            {'name': 'Laundry', 'description': 'Professional laundry service', 'price': 100.00},
            {'name': 'Room Service', 'description': '24/7 room service', 'price': 50.00},
            {'name': 'Spa Treatment', 'description': 'Relaxing spa services', 'price': 200.00},
            {'name': 'Airport Transfer', 'description': 'Transportation to/from airport', 'price': 150.00},
        ]

        for hotel in hotels:
            self.stdout.write(f'Adding amenities and services for hotel: {hotel.name}')
            
            # Create amenities
            for amenity_info in amenity_data:
                amenity, created = Amenity.objects.get_or_create(
                    name=amenity_info['name'],
                    defaults={
                        'icon': amenity_info['icon'],
                        'description': amenity_info['description'],
                        'is_active': True
                    }
                )
                amenity.hotels.add(hotel)
                if created:
                    self.stdout.write(f'  Created amenity: {amenity.name}')
                else:
                    self.stdout.write(f'  Added existing amenity: {amenity.name}')

            # Create services
            for service_info in service_data:
                service, created = Service.objects.get_or_create(
                    name=service_info['name'],
                    defaults={
                        'description': service_info['description'],
                        'price': service_info['price'],
                        'is_active': True
                    }
                )
                service.hotels.add(hotel)
                if created:
                    self.stdout.write(f'  Created service: {service.name}')
                else:
                    self.stdout.write(f'  Added existing service: {service.name}')

        self.stdout.write(self.style.SUCCESS('Successfully created sample amenities and services'))