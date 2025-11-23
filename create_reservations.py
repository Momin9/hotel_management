#!/usr/bin/env python3
import os
import django
from datetime import date, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.contrib.auth import get_user_model
from hotels.models import Hotel, Room
from crm.models import GuestProfile
from reservations.models import Reservation

User = get_user_model()

def create_reservations():
    print("Removing existing reservations...")
    Reservation.objects.all().delete()
    
    print("Creating realistic reservations for each hotel...")
    
    # Create guest profiles
    guests_data = [
        {'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@email.com', 'phone': '+1-555-0101'},
        {'first_name': 'Emma', 'last_name': 'Johnson', 'email': 'emma.johnson@email.com', 'phone': '+1-555-0102'},
        {'first_name': 'Michael', 'last_name': 'Brown', 'email': 'michael.brown@email.com', 'phone': '+1-555-0103'},
        {'first_name': 'Sarah', 'last_name': 'Davis', 'email': 'sarah.davis@email.com', 'phone': '+1-555-0104'},
        {'first_name': 'David', 'last_name': 'Wilson', 'email': 'david.wilson@email.com', 'phone': '+1-555-0105'},
        {'first_name': 'Lisa', 'last_name': 'Garcia', 'email': 'lisa.garcia@email.com', 'phone': '+1-555-0106'},
        {'first_name': 'James', 'last_name': 'Martinez', 'email': 'james.martinez@email.com', 'phone': '+1-555-0107'},
        {'first_name': 'Maria', 'last_name': 'Lopez', 'email': 'maria.lopez@email.com', 'phone': '+1-555-0108'},
        {'first_name': 'Robert', 'last_name': 'Anderson', 'email': 'robert.anderson@email.com', 'phone': '+1-555-0109'},
        {'first_name': 'Jennifer', 'last_name': 'Taylor', 'email': 'jennifer.taylor@email.com', 'phone': '+1-555-0110'},
    ]
    
    created_guests = []
    for guest_data in guests_data:
        guest, created = GuestProfile.objects.get_or_create(
            email=guest_data['email'],
            defaults=guest_data
        )
        created_guests.append(guest)
        if created:
            print(f"✓ Created guest: {guest.full_name}")
    
    # Get all hotels
    hotels = Hotel.objects.filter(deleted_at__isnull=True, is_active=True)
    
    reservation_statuses = ['confirmed', 'checked_in', 'checked_out']
    
    for hotel in hotels:
        print(f"\nCreating reservations for {hotel.name}...")
        
        # Get available rooms for this hotel
        rooms = list(Room.objects.filter(hotel=hotel)[:10])  # Limit to first 10 rooms
        
        if not rooms:
            print(f"  ⚠ No rooms found for {hotel.name}, skipping...")
            continue
        
        # Create 3-5 reservations per hotel
        num_reservations = random.randint(3, 5)
        
        for i in range(num_reservations):
            guest = random.choice(created_guests)
            room = random.choice(rooms)
            
            # Generate random dates
            days_ago = random.randint(1, 30)
            check_in_date = date.today() - timedelta(days=days_ago)
            stay_duration = random.randint(1, 7)
            check_out_date = check_in_date + timedelta(days=stay_duration)
            
            # Determine status based on dates
            if check_out_date < date.today():
                status = 'checked_out'
            elif check_in_date <= date.today() <= check_out_date:
                status = 'checked_in'
            else:
                status = 'confirmed'
            
            reservation = Reservation.objects.create(
                guest=guest,
                hotel=hotel,
                room=room,
                check_in=check_in_date,
                check_out=check_out_date,
                adults=random.randint(1, 4),
                children=random.randint(0, 2),
                rate=room.price,
                status=status,
                booking_source='direct',
                special_requests=random.choice([
                    'Late check-in requested',
                    'Extra towels needed',
                    'Quiet room preferred',
                    'High floor requested',
                    ''
                ])
            )
            
            print(f"  ✓ Created reservation: {guest.full_name} - Room {room.room_number} ({status})")
    
    total_reservations = Reservation.objects.count()
    print(f"\n✓ Created {total_reservations} reservations across all hotels")

if __name__ == '__main__':
    create_reservations()