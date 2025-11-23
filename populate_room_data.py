#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from hotels.models import RoomCategory, RoomType, RoomStatus, Room, Hotel

def populate_room_data():
    """Populate room categories, types, and statuses"""
    
    # Create Room Categories
    categories_data = [
        {
            'name': 'Standard',
            'description': 'Basic comfortable rooms with essential amenities',
            'base_price_multiplier': 1.00,
            'amenities': '["WiFi", "TV", "Air Conditioning", "Private Bathroom"]'
        },
        {
            'name': 'Deluxe',
            'description': 'Enhanced rooms with premium amenities and better views',
            'base_price_multiplier': 1.50,
            'amenities': '["WiFi", "Smart TV", "Air Conditioning", "Private Bathroom", "Mini Bar", "City View"]'
        },
        {
            'name': 'Suite',
            'description': 'Spacious suites with separate living areas',
            'base_price_multiplier': 2.50,
            'amenities': '["WiFi", "Smart TV", "Air Conditioning", "Private Bathroom", "Mini Bar", "Living Area", "Kitchenette", "Premium View"]'
        },
        {
            'name': 'Executive',
            'description': 'Business-class rooms with work facilities',
            'base_price_multiplier': 2.00,
            'amenities': '["WiFi", "Smart TV", "Air Conditioning", "Private Bathroom", "Work Desk", "Business Center Access", "Premium Bedding"]'
        },
        {
            'name': 'Presidential Suite',
            'description': 'Luxury presidential suites with premium services',
            'base_price_multiplier': 5.00,
            'amenities': '["WiFi", "Smart TV", "Air Conditioning", "Private Bathroom", "Butler Service", "Jacuzzi", "Panoramic View", "Dining Area"]'
        }
    ]
    
    for cat_data in categories_data:
        category, created = RoomCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"Created category: {category.name}")
    
    # Create Room Types
    types_data = [
        {
            'name': 'Single',
            'description': 'Single occupancy room with one bed',
            'max_occupancy': 1,
            'bed_configuration': 'Single Bed'
        },
        {
            'name': 'Double',
            'description': 'Double occupancy room with one double bed',
            'max_occupancy': 2,
            'bed_configuration': 'Double Bed'
        },
        {
            'name': 'Twin',
            'description': 'Twin beds for two guests',
            'max_occupancy': 2,
            'bed_configuration': 'Two Single Beds'
        },
        {
            'name': 'Triple',
            'description': 'Room for three guests',
            'max_occupancy': 3,
            'bed_configuration': 'One Double + One Single Bed'
        },
        {
            'name': 'Quad',
            'description': 'Room for four guests',
            'max_occupancy': 4,
            'bed_configuration': 'Two Double Beds'
        },
        {
            'name': 'King',
            'description': 'Spacious room with king-size bed',
            'max_occupancy': 2,
            'bed_configuration': 'King Size Bed'
        },
        {
            'name': 'Queen',
            'description': 'Comfortable room with queen-size bed',
            'max_occupancy': 2,
            'bed_configuration': 'Queen Size Bed'
        }
    ]
    
    for type_data in types_data:
        room_type, created = RoomType.objects.get_or_create(
            name=type_data['name'],
            defaults=type_data
        )
        if created:
            print(f"Created room type: {room_type.name}")
    
    # Create Room Statuses
    statuses_data = [
        {
            'name': 'Available',
            'description': 'Room is clean and ready for guests',
            'color_code': '#10B981',
            'is_available_for_booking': True
        },
        {
            'name': 'Occupied',
            'description': 'Room is currently occupied by guests',
            'color_code': '#EF4444',
            'is_available_for_booking': False
        },
        {
            'name': 'Reserved',
            'description': 'Room is reserved for future check-in',
            'color_code': '#F59E0B',
            'is_available_for_booking': False
        },
        {
            'name': 'Dirty',
            'description': 'Room needs cleaning after checkout',
            'color_code': '#8B5CF6',
            'is_available_for_booking': False
        },
        {
            'name': 'Cleaning',
            'description': 'Room is currently being cleaned',
            'color_code': '#3B82F6',
            'is_available_for_booking': False
        },
        {
            'name': 'Maintenance',
            'description': 'Room is under maintenance or repair',
            'color_code': '#F97316',
            'is_available_for_booking': False
        },
        {
            'name': 'Blocked',
            'description': 'Room is blocked and not available',
            'color_code': '#6B7280',
            'is_available_for_booking': False
        }
    ]
    
    for status_data in statuses_data:
        room_status, created = RoomStatus.objects.get_or_create(
            name=status_data['name'],
            defaults=status_data
        )
        if created:
            print(f"Created room status: {room_status.name}")
    
    # Update existing rooms to use new models
    print("\nUpdating existing rooms...")
    
    # Get default objects
    default_category = RoomCategory.objects.get(name='Standard')
    default_type = RoomType.objects.get(name='Double')
    default_status = RoomStatus.objects.get(name='Available')
    
    # Update rooms that don't have the new foreign keys
    rooms_updated = 0
    for room in Room.objects.all():
        updated = False
        
        if not hasattr(room, 'room_type') or room.room_type is None:
            # Map old type to new type
            type_mapping = {
                'Single': 'Single',
                'Double': 'Double',
                'Twin': 'Twin',
                'Triple': 'Triple',
                'Quad': 'Quad'
            }
            old_type = getattr(room, 'type', 'Double')
            new_type_name = type_mapping.get(old_type, 'Double')
            room.room_type = RoomType.objects.get(name=new_type_name)
            updated = True
        
        if not hasattr(room, 'category') or room.category is None:
            # Map old category to new category
            category_mapping = {
                'Standard': 'Standard',
                'Deluxe': 'Deluxe',
                'SuperDeluxe': 'Deluxe',
                'Executive': 'Executive',
                'Suite': 'Suite',
                'JuniorSuite': 'Suite',
                'PresidentialSuite': 'Presidential Suite'
            }
            old_category = getattr(room, 'category', 'Standard')
            new_category_name = category_mapping.get(old_category, 'Standard')
            room.category = RoomCategory.objects.get(name=new_category_name)
            updated = True
        
        if not hasattr(room, 'status') or room.status is None:
            # Map old status to new status
            status_mapping = {
                'Available': 'Available',
                'Occupied': 'Occupied',
                'Reserved': 'Reserved',
                'Dirty': 'Dirty',
                'Cleaning': 'Cleaning',
                'Maintenance': 'Maintenance',
                'Blocked': 'Blocked'
            }
            old_status = getattr(room, 'status', 'Available')
            new_status_name = status_mapping.get(old_status, 'Available')
            room.status = RoomStatus.objects.get(name=new_status_name)
            updated = True
        
        if updated:
            room.save()
            rooms_updated += 1
    
    print(f"Updated {rooms_updated} rooms with new model relationships")
    print("\nRoom data population completed successfully!")

if __name__ == "__main__":
    populate_room_data()