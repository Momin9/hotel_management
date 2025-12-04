#!/usr/bin/env python3
"""
Create realistic reservations for occupied rooms
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
from crm.models import GuestProfile
from reservations.models import Reservation, Stay
from django.utils import timezone

def create_reservations_for_occupied_rooms():
    """Create reservations for all occupied rooms"""
    print("Creating reservations for occupied rooms...")
    
    # Get all occupied rooms
    occupied_rooms = Room.objects.filter(status='Occupied')
    guests = list(GuestProfile.objects.all())
    
    if not guests:
        print("❌ No guests found! Please run populate_sample_data.py first")
        return
    
    today = date.today()
    
    for room in occupied_rooms:
        # Random guest
        guest = random.choice(guests)
        
        # Random check-in date (1-5 days ago)
        check_in_date = today - timedelta(days=random.randint(1, 5))
        
        # Random stay duration (1-7 days from check-in)
        stay_duration = random.randint(1, 7)
        check_out_date = check_in_date + timedelta(days=stay_duration)
        
        # If check-out is in the past, extend it to future
        if check_out_date <= today:
            check_out_date = today + timedelta(days=random.randint(1, 3))
        
        # Create reservation
        reservation = Reservation.objects.create(
            guest=guest,
            hotel=room.hotel,
            room=room,
            check_in=check_in_date,
            check_out=check_out_date,
            adults=random.randint(1, 2),
            children=random.randint(0, 1),
            status='checked_in',
            booking_source=random.choice(['direct', 'online', 'phone', 'walk_in']),
            rate=room.price
        )
        
        # Create stay record
        check_in_time = timezone.make_aware(
            datetime.combine(check_in_date, datetime.min.time().replace(hour=15))
        )
        
        Stay.objects.create(
            reservation=reservation,
            room=room,
            actual_check_in=check_in_time,
            notes=f"Guest checked in on {check_in_date}"
        )
        
        print(f"✓ Created reservation for Room {room.room_number} at {room.hotel.name}")
        print(f"  Guest: {guest.full_name}")
        print(f"  Check-in: {check_in_date}, Check-out: {check_out_date}")
        print(f"  Rate: ${room.price}/night")

def create_future_reservations():
    """Create some future reservations for available rooms"""
    print("\nCreating future reservations...")
    
    available_rooms = Room.objects.filter(status='Available')
    guests = list(GuestProfile.objects.all())
    
    # Create 10-15 future reservations
    future_reservations_count = min(15, available_rooms.count())
    selected_rooms = random.sample(list(available_rooms), future_reservations_count)
    
    today = date.today()
    
    for room in selected_rooms:
        guest = random.choice(guests)
        
        # Future check-in (1-30 days from now)
        check_in_date = today + timedelta(days=random.randint(1, 30))
        
        # Stay duration (1-5 days)
        stay_duration = random.randint(1, 5)
        check_out_date = check_in_date + timedelta(days=stay_duration)
        
        reservation = Reservation.objects.create(
            guest=guest,
            hotel=room.hotel,
            room=room,
            check_in=check_in_date,
            check_out=check_out_date,
            adults=random.randint(1, 2),
            children=random.randint(0, 2),
            status='confirmed',
            booking_source=random.choice(['direct', 'online', 'phone', 'ota']),
            rate=room.price
        )
        
        print(f"✓ Future reservation: Room {room.room_number} at {room.hotel.name}")
        print(f"  Guest: {guest.full_name}")
        print(f"  Check-in: {check_in_date}, Check-out: {check_out_date}")

def main():
    """Main function"""
    print("🏨 Creating Realistic Reservations")
    print("=" * 40)
    
    try:
        # First, clear existing reservations to avoid conflicts
        print("Clearing existing reservations...")
        Reservation.objects.all().delete()
        Stay.objects.all().delete()
        
        create_reservations_for_occupied_rooms()
        create_future_reservations()
        
        # Summary
        total_reservations = Reservation.objects.count()
        checked_in = Reservation.objects.filter(status='checked_in').count()
        confirmed = Reservation.objects.filter(status='confirmed').count()
        
        print("\n" + "=" * 40)
        print("🎉 Reservations created successfully!")
        print(f"Total reservations: {total_reservations}")
        print(f"Currently checked in: {checked_in}")
        print(f"Future confirmed: {confirmed}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()