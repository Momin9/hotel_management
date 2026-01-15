from django.core.management.base import BaseCommand
from hotels.models import Hotel, Room
from configurations.models import RoomType, BedType, Floor

class Command(BaseCommand):
    help = 'Create sample rooms for hotels'

    def handle(self, *args, **options):
        # Get all hotels
        hotels = Hotel.objects.filter(deleted_at__isnull=True)
        
        if not hotels.exists():
            self.stdout.write(self.style.ERROR('No hotels found. Please create hotels first.'))
            return
        
        # Create default room types if they don't exist
        room_types_data = [
            {'name': 'Standard', 'description': 'Standard room with basic amenities'},
            {'name': 'Deluxe', 'description': 'Deluxe room with premium amenities'},
            {'name': 'Suite', 'description': 'Luxury suite with separate living area'},
        ]
        
        for rt_data in room_types_data:
            room_type, created = RoomType.objects.get_or_create(
                name=rt_data['name'],
                defaults={'description': rt_data['description']}
            )
            if created:
                self.stdout.write(f'Created room type: {room_type.name}')
            # Associate with all hotels
            room_type.hotels.set(hotels)
        
        # Create default bed types if they don't exist
        bed_types_data = [
            {'name': 'Single', 'description': 'Single bed'},
            {'name': 'Double', 'description': 'Double bed'},
            {'name': 'Queen', 'description': 'Queen size bed'},
            {'name': 'King', 'description': 'King size bed'},
        ]
        
        for bt_data in bed_types_data:
            bed_type, created = BedType.objects.get_or_create(
                name=bt_data['name'],
                defaults={'description': bt_data['description']}
            )
            if created:
                self.stdout.write(f'Created bed type: {bed_type.name}')
            # Associate with all hotels
            bed_type.hotels.set(hotels)
        
        # Create sample rooms for each hotel
        for hotel in hotels:
            # Create floor if it doesn't exist
            floor, created = Floor.objects.get_or_create(
                name='Ground Floor',
                number=1,
                defaults={'description': 'Ground floor rooms'}
            )
            if created:
                floor.hotels.add(hotel)
            
            # Check if hotel already has rooms
            if hotel.rooms.exists():
                self.stdout.write(f'Hotel {hotel.name} already has rooms. Skipping...')
                continue
            
            # Get room types and bed types
            room_types = {rt.name: rt for rt in RoomType.objects.filter(hotels=hotel)}
            bed_types = {bt.name: bt for bt in BedType.objects.filter(hotels=hotel)}
            
            # Create sample rooms
            room_data = [
                {'number': '101', 'type': 'Standard', 'bed': 'Double', 'price': 100},
                {'number': '102', 'type': 'Standard', 'bed': 'Double', 'price': 100},
                {'number': '103', 'type': 'Deluxe', 'bed': 'Queen', 'price': 150},
                {'number': '104', 'type': 'Deluxe', 'bed': 'Queen', 'price': 150},
                {'number': '105', 'type': 'Suite', 'bed': 'King', 'price': 250},
            ]
            
            for room_info in room_data:
                room_type = room_types.get(room_info['type'])
                bed_type = bed_types.get(room_info['bed'])
                
                if room_type and bed_type:
                    room = Room.objects.create(
                        hotel=hotel,
                        floor=floor,
                        room_number=room_info['number'],
                        room_type=room_type,
                        bed_type=bed_type,
                        price=room_info['price'],
                        status='Available'
                    )
                    
                    self.stdout.write(f'Created room {room.room_number} for {hotel.name}')
                else:
                    self.stdout.write(self.style.WARNING(f'Skipping room {room_info["number"]} - missing room type or bed type'))
        
        self.stdout.write(self.style.SUCCESS('Sample rooms created successfully!'))