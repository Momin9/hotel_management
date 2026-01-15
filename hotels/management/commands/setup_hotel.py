from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from hotels.models import Hotel, Room
from configurations.models import RoomType, BedType, Floor

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup basic hotel data for testing'

    def handle(self, *args, **options):
        # Create a test user if none exists
        if not User.objects.filter(is_superuser=True).exists():
            admin_user = User.objects.create_superuser(
                email='admin@hotel.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(f'Created admin user: admin@hotel.com / admin123')
        else:
            admin_user = User.objects.filter(is_superuser=True).first()
        
        # Create a test hotel if none exists
        if not Hotel.objects.exists():
            hotel = Hotel.objects.create(
                owner=admin_user,
                name='Test Hotel',
                address='123 Test Street',
                city='Test City',
                country='Pakistan',
                phone='+92-300-1234567',
                email='info@testhotel.com'
            )
            self.stdout.write(f'Created hotel: {hotel.name}')
        else:
            hotel = Hotel.objects.first()
        
        # Create room configurations
        room_type, created = RoomType.objects.get_or_create(
            name='Standard',
            defaults={'description': 'Standard room'}
        )
        if created:
            room_type.hotels.add(hotel)
        
        bed_type, created = BedType.objects.get_or_create(
            name='Double',
            defaults={'description': 'Double bed'}
        )
        if created:
            bed_type.hotels.add(hotel)
        
        floor, created = Floor.objects.get_or_create(
            name='Ground Floor',
            number=1,
            defaults={'description': 'Ground floor'}
        )
        if created:
            floor.hotels.add(hotel)
        
        # Create sample rooms if none exist
        if not Room.objects.filter(hotel=hotel).exists():
            for i in range(1, 6):
                room = Room.objects.create(
                    hotel=hotel,
                    room_number=f'10{i}',
                    room_type=room_type,
                    bed_type=bed_type,
                    floor=floor,
                    price=100,
                    status='Available'
                )
                self.stdout.write(f'Created room: {room.room_number}')
        
        self.stdout.write(self.style.SUCCESS('Hotel setup completed successfully!'))
        self.stdout.write(f'Hotel: {hotel.name}')
        self.stdout.write(f'Rooms: {Room.objects.filter(hotel=hotel).count()}')
        self.stdout.write(f'Admin login: admin@hotel.com / admin123')