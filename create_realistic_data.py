#!/usr/bin/env python3
"""
Create realistic occupancy and revenue data
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from hotels.models import Hotel, Room
from accounts.models import User

def create_realistic_occupancy():
    """Create realistic room occupancy"""
    print("Creating realistic room occupancy...")
    
    hotels = Hotel.objects.all()
    
    for hotel in hotels:
        rooms = Room.objects.filter(hotel=hotel)
        total_rooms = rooms.count()
        
        # Set 60-80% occupancy randomly
        occupancy_rate = random.uniform(0.6, 0.8)
        occupied_count = int(total_rooms * occupancy_rate)
        
        # Reset all rooms to Available first
        rooms.update(status='Available')
        
        # Set some rooms as occupied
        rooms_to_occupy = random.sample(list(rooms), occupied_count)
        for room in rooms_to_occupy:
            room.status = 'Occupied'
            room.save()
        
        # Set a few rooms to other statuses
        remaining_rooms = rooms.exclude(status='Occupied')
        if remaining_rooms.exists():
            # Set some as cleaning
            cleaning_count = min(2, remaining_rooms.count())
            cleaning_rooms = random.sample(list(remaining_rooms), cleaning_count)
            for room in cleaning_rooms:
                room.status = 'Cleaning'
                room.save()
            
            # Set some as maintenance
            remaining_rooms = remaining_rooms.exclude(status='Cleaning')
            if remaining_rooms.exists():
                maintenance_count = min(1, remaining_rooms.count())
                maintenance_rooms = random.sample(list(remaining_rooms), maintenance_count)
                for room in maintenance_rooms:
                    room.status = 'Maintenance'
                    room.save()
        
        occupied_rooms = rooms.filter(status='Occupied').count()
        print(f"✓ {hotel.name}: {occupied_rooms}/{total_rooms} rooms occupied ({occupied_rooms/total_rooms*100:.1f}%)")

def assign_staff_to_hotels():
    """Assign staff members to hotels"""
    print("Assigning staff to hotels...")
    
    hotels = Hotel.objects.all()
    staff_users = User.objects.filter(role__in=['Manager', 'Receptionist', 'Housekeeping'], assigned_hotel__isnull=True)
    
    for i, staff in enumerate(staff_users):
        hotel = hotels[i % hotels.count()]
        staff.assigned_hotel = hotel
        staff.save()
        print(f"✓ Assigned {staff.get_full_name()} ({staff.role}) to {hotel.name}")

def main():
    """Main function"""
    print("🏨 Creating Realistic Hotel Data")
    print("=" * 40)
    
    try:
        create_realistic_occupancy()
        assign_staff_to_hotels()
        
        print("\n" + "=" * 40)
        print("🎉 Realistic data created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()