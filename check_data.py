#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from hotels.models import Hotel, Room

print('🏨 Room Details by Hotel:')
for hotel in Hotel.objects.all():
    print(f'\n{hotel.name}:')
    rooms = Room.objects.filter(hotel=hotel).order_by('room_number')
    
    # Group by room type
    room_types = {}
    for room in rooms:
        rt = room.room_type.name if room.room_type else 'No Type'
        if rt not in room_types:
            room_types[rt] = []
        room_types[rt].append(room)
    
    for room_type, room_list in room_types.items():
        print(f'  {room_type}: {len(room_list)} rooms')
        for room in room_list[:3]:  # Show first 3 rooms
            bed = room.bed_type.name if room.bed_type else 'No Bed'
            floor = f'Floor {room.floor.number}' if room.floor else 'No Floor'
            print(f'    - Room {room.room_number}: {bed}, {floor}, ${room.price}/night')
        if len(room_list) > 3:
            print(f'    ... and {len(room_list) - 3} more rooms')