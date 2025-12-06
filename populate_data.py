#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.contrib.auth import get_user_model
from hotels.models import Hotel, Service
from configurations.models import RoomType, BedType, Floor, Amenity

User = get_user_model()

def create_sample_data():
    print("Creating sample data...")
    
    # Get or create a user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True,
            'role': 'Owner'
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"Created user: {user.username}")
    
    # Create Hotels
    hotels_data = [
        {'name': 'Grand Palace Hotel', 'city': 'New York', 'country': 'USA'},
        {'name': 'Royal Resort & Spa', 'city': 'Miami', 'country': 'USA'},
        {'name': 'Luxury Suites Downtown', 'city': 'Chicago', 'country': 'USA'},
    ]
    
    hotels = []
    for hotel_data in hotels_data:
        hotel, created = Hotel.objects.get_or_create(
            name=hotel_data['name'],
            defaults={
                'owner': user,
                'city': hotel_data['city'],
                'country': hotel_data['country'],
                'currency': 'USD',
                'is_active': True
            }
        )
        hotels.append(hotel)
        if created:
            print(f"Created hotel: {hotel.name}")
    
    # Create Room Types
    room_types_data = [
        {'name': 'Standard Room', 'description': 'Comfortable standard accommodation'},
        {'name': 'Deluxe Room', 'description': 'Spacious room with premium amenities'},
        {'name': 'Junior Suite', 'description': 'Suite with separate seating area'},
        {'name': 'Executive Suite', 'description': 'Luxury suite with executive privileges'},
        {'name': 'Presidential Suite', 'description': 'Ultimate luxury accommodation'},
    ]
    
    for rt_data in room_types_data:
        room_type, created = RoomType.objects.get_or_create(
            name=rt_data['name'],
            defaults={
                'description': rt_data['description'],
                'is_active': True
            }
        )
        if created:
            # Add to all hotels
            room_type.hotels.set(hotels)
            print(f"Created room type: {room_type.name}")
    
    # Create Bed Types
    bed_types_data = [
        {'name': 'Single Bed', 'description': '90cm x 190cm single bed'},
        {'name': 'Double Bed', 'description': '135cm x 190cm double bed'},
        {'name': 'Queen Bed', 'description': '150cm x 200cm queen size bed'},
        {'name': 'King Bed', 'description': '180cm x 200cm king size bed'},
        {'name': 'Twin Beds', 'description': 'Two single beds'},
        {'name': 'Sofa Bed', 'description': 'Convertible sofa bed'},
    ]
    
    for bt_data in bed_types_data:
        bed_type, created = BedType.objects.get_or_create(
            name=bt_data['name'],
            defaults={
                'description': bt_data['description'],
                'is_active': True
            }
        )
        if created:
            bed_type.hotels.set(hotels)
            print(f"Created bed type: {bed_type.name}")
    
    # Create Floors
    floors_data = [
        {'name': 'Ground Floor', 'number': 0, 'description': 'Lobby and reception area'},
        {'name': 'First Floor', 'number': 1, 'description': 'Standard rooms'},
        {'name': 'Second Floor', 'number': 2, 'description': 'Standard and deluxe rooms'},
        {'name': 'Third Floor', 'number': 3, 'description': 'Deluxe rooms and junior suites'},
        {'name': 'Fourth Floor', 'number': 4, 'description': 'Executive suites'},
        {'name': 'Penthouse', 'number': 5, 'description': 'Presidential suites'},
    ]
    
    for floor_data in floors_data:
        floor, created = Floor.objects.get_or_create(
            name=floor_data['name'],
            number=floor_data['number'],
            defaults={
                'description': floor_data['description'],
                'is_active': True
            }
        )
        if created:
            floor.hotels.set(hotels)
            print(f"Created floor: {floor.name}")
    
    # Create Amenities
    amenities_data = [
        {'name': 'Free Wi-Fi', 'description': 'Complimentary high-speed internet', 'icon': 'fas fa-wifi'},
        {'name': 'Air Conditioning', 'description': 'Climate control system', 'icon': 'fas fa-snowflake'},
        {'name': 'Flat Screen TV', 'description': 'HD television with cable channels', 'icon': 'fas fa-tv'},
        {'name': 'Mini Bar', 'description': 'In-room refreshment center', 'icon': 'fas fa-glass-martini'},
        {'name': 'Room Service', 'description': '24/7 in-room dining service', 'icon': 'fas fa-concierge-bell'},
        {'name': 'Safe Deposit Box', 'description': 'Secure storage for valuables', 'icon': 'fas fa-lock'},
        {'name': 'Balcony', 'description': 'Private outdoor space', 'icon': 'fas fa-door-open'},
        {'name': 'Work Desk', 'description': 'Dedicated workspace', 'icon': 'fas fa-desk'},
        {'name': 'Coffee Machine', 'description': 'In-room coffee maker', 'icon': 'fas fa-coffee'},
        {'name': 'Bathtub', 'description': 'Luxury bathing facility', 'icon': 'fas fa-bath'},
    ]
    
    for amenity_data in amenities_data:
        amenity, created = Amenity.objects.get_or_create(
            name=amenity_data['name'],
            defaults={
                'description': amenity_data['description'],
                'icon': amenity_data['icon'],
                'is_active': True
            }
        )
        if created:
            amenity.hotels.set(hotels)
            print(f"Created amenity: {amenity.name}")
    
    # Create Services
    services_data = [
        {'name': 'Airport Shuttle', 'description': 'Complimentary airport transportation', 'price': 0.00},
        {'name': 'Laundry Service', 'description': 'Professional cleaning and pressing', 'price': 25.00},
        {'name': 'Spa Treatment', 'description': 'Relaxing massage and wellness services', 'price': 150.00},
        {'name': 'Valet Parking', 'description': 'Premium parking service', 'price': 35.00},
        {'name': 'Business Center', 'description': 'Printing, copying, and meeting facilities', 'price': 20.00},
        {'name': 'Fitness Center', 'description': '24/7 gym access', 'price': 0.00},
        {'name': 'Swimming Pool', 'description': 'Indoor heated pool', 'price': 0.00},
        {'name': 'Restaurant Dining', 'description': 'Fine dining experience', 'price': 75.00},
        {'name': 'Concierge Service', 'description': 'Personal assistance and recommendations', 'price': 0.00},
        {'name': 'Pet Care', 'description': 'Pet sitting and walking services', 'price': 50.00},
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults={
                'description': service_data['description'],
                'price': service_data['price']
            }
        )
        if created:
            service.hotels.set(hotels)
            print(f"Created service: {service.name}")
    
    print("\n✅ Sample data created successfully!")
    print(f"Hotels: {Hotel.objects.count()}")
    print(f"Room Types: {RoomType.objects.count()}")
    print(f"Bed Types: {BedType.objects.count()}")
    print(f"Floors: {Floor.objects.count()}")
    print(f"Amenities: {Amenity.objects.count()}")
    print(f"Services: {Service.objects.count()}")

if __name__ == '__main__':
    create_sample_data()