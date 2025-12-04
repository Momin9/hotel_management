#!/usr/bin/env python3
"""
Sample Data Population Script for Hotel Management System
Creates realistic hotel data for testing and demonstration
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from accounts.models import User
from hotels.models import Hotel, Service, Room, Company
from configurations.models import RoomType, BedType, Floor, Amenity
from tenants.models import SubscriptionPlan
from crm.models import GuestProfile

def create_users():
    """Create sample users with different roles"""
    print("Creating users...")
    
    # Create superuser if not exists
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@aurastay.com',
            password='admin123',
            first_name='System',
            last_name='Administrator',
            role='Owner'
        )
        print(f"✓ Created superuser: {admin.username}")
    
    # Hotel owners
    owners_data = [
        {
            'username': 'john_owner',
            'email': 'john@grandhotel.com',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Smith',
            'role': 'Owner',
            'phone': '+1-555-0101'
        },
        {
            'username': 'sarah_owner',
            'email': 'sarah@luxuryresort.com',
            'password': 'password123',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'role': 'Owner',
            'phone': '+1-555-0102'
        }
    ]
    
    created_owners = []
    for owner_data in owners_data:
        if not User.objects.filter(username=owner_data['username']).exists():
            owner = User.objects.create_user(**owner_data)
            # Set full permissions for owners
            for field in owner._meta.fields:
                if field.name.startswith('can_'):
                    setattr(owner, field.name, True)
            owner.save()
            created_owners.append(owner)
            print(f"✓ Created owner: {owner.username}")
    
    return created_owners

def create_subscription_plans():
    """Create subscription plans"""
    print("Creating subscription plans...")
    
    plans_data = [
        {
            'name': 'Free Trial',
            'description': 'Perfect for small properties to get started',
            'price_monthly': Decimal('0.00'),
            'price_yearly': Decimal('0.00'),
            'is_free_trial': True,
            'max_rooms': 10,
            'max_managers': 2,
            'max_reports': 5,
            'has_advanced_analytics': False,
            'has_priority_support': False
        },
        {
            'name': 'Starter',
            'description': 'Ideal for boutique hotels and small properties',
            'price_monthly': Decimal('49.99'),
            'price_yearly': Decimal('499.99'),
            'max_rooms': 50,
            'max_managers': 5,
            'max_reports': 20,
            'has_advanced_analytics': False,
            'has_priority_support': False
        },
        {
            'name': 'Professional',
            'description': 'Perfect for mid-size hotels and growing businesses',
            'price_monthly': Decimal('99.99'),
            'price_yearly': Decimal('999.99'),
            'max_rooms': 150,
            'max_managers': 15,
            'max_reports': 50,
            'has_advanced_analytics': True,
            'has_priority_support': False
        },
        {
            'name': 'Enterprise',
            'description': 'Complete solution for large hotels and chains',
            'price_monthly': Decimal('199.99'),
            'price_yearly': Decimal('1999.99'),
            'max_rooms': 500,
            'max_managers': 50,
            'max_reports': 100,
            'has_advanced_analytics': True,
            'has_priority_support': True
        }
    ]
    
    created_plans = []
    for plan_data in plans_data:
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        if created:
            created_plans.append(plan)
            print(f"✓ Created plan: {plan.name}")
    
    return created_plans

def create_hotels(owners):
    """Create sample hotels"""
    print("Creating hotels...")
    
    hotels_data = [
        {
            'name': 'Grand Palace Hotel',
            'address': '123 Luxury Avenue, Downtown District',
            'city': 'New York',
            'country': 'United States',
            'phone': '+1-555-0201',
            'email': 'info@grandpalace.com',
            'currency': 'USD'
        },
        {
            'name': 'Oceanview Resort & Spa',
            'address': '456 Beachfront Boulevard',
            'city': 'Miami',
            'country': 'United States',
            'phone': '+1-555-0202',
            'email': 'reservations@oceanviewresort.com',
            'currency': 'USD'
        },
        {
            'name': 'Mountain Lodge Retreat',
            'address': '789 Alpine Way, Mountain View',
            'city': 'Denver',
            'country': 'United States',
            'phone': '+1-555-0203',
            'email': 'contact@mountainlodge.com',
            'currency': 'USD'
        }
    ]
    
    created_hotels = []
    for i, hotel_data in enumerate(hotels_data):
        if not Hotel.objects.filter(name=hotel_data['name']).exists():
            # Assign owner (cycle through available owners)
            owner = owners[i % len(owners)] if owners else User.objects.filter(role='Owner').first()
            hotel_data['owner'] = owner
            
            hotel = Hotel.objects.create(**hotel_data)
            created_hotels.append(hotel)
            print(f"✓ Created hotel: {hotel.name}")
    
    return created_hotels

def create_configurations(hotels):
    """Create room types, bed types, floors, and amenities"""
    print("Creating configurations...")
    
    # Room Types
    room_types_data = [
        {'name': 'Standard Room', 'description': 'Comfortable standard accommodation'},
        {'name': 'Deluxe Room', 'description': 'Enhanced comfort with premium amenities'},
        {'name': 'Junior Suite', 'description': 'Spacious room with separate seating area'},
        {'name': 'Executive Suite', 'description': 'Luxury suite with living room'},
        {'name': 'Presidential Suite', 'description': 'Ultimate luxury accommodation'},
    ]
    
    # Bed Types
    bed_types_data = [
        {'name': 'Single Bed', 'description': 'Single bed for one person'},
        {'name': 'Double Bed', 'description': 'Double bed for two people'},
        {'name': 'Queen Bed', 'description': 'Queen size bed'},
        {'name': 'King Bed', 'description': 'King size bed'},
        {'name': 'Twin Beds', 'description': 'Two separate single beds'},
    ]
    
    # Amenities
    amenities_data = [
        {'name': 'Room Service', 'description': '24/7 room service', 'icon': 'fas fa-concierge-bell'},
        {'name': 'Spa Access', 'description': 'Access to hotel spa', 'icon': 'fas fa-spa'},
        {'name': 'Gym Access', 'description': 'Fitness center access', 'icon': 'fas fa-dumbbell'},
        {'name': 'Pool Access', 'description': 'Swimming pool access', 'icon': 'fas fa-swimming-pool'},
        {'name': 'Business Center', 'description': 'Business facilities', 'icon': 'fas fa-briefcase'},
        {'name': 'Concierge Service', 'description': 'Personal concierge', 'icon': 'fas fa-user-tie'},
        {'name': 'Valet Parking', 'description': 'Valet parking service', 'icon': 'fas fa-car'},
        {'name': 'Airport Shuttle', 'description': 'Airport transfer service', 'icon': 'fas fa-shuttle-van'},
    ]
    
    for hotel in hotels:
        # Create room types
        for rt_data in room_types_data:
            RoomType.objects.get_or_create(
                hotel=hotel,
                name=rt_data['name'],
                defaults=rt_data
            )
        
        # Create bed types
        for bt_data in bed_types_data:
            BedType.objects.get_or_create(
                hotel=hotel,
                name=bt_data['name'],
                defaults=bt_data
            )
        
        # Create floors
        floor_data = [
            {'name': 'Ground Floor', 'number': 0, 'description': 'Lobby and reception area'},
            {'name': 'First Floor', 'number': 1, 'description': 'Standard rooms'},
            {'name': 'Second Floor', 'number': 2, 'description': 'Deluxe rooms'},
            {'name': 'Third Floor', 'number': 3, 'description': 'Premium rooms'},
            {'name': 'Fourth Floor', 'number': 4, 'description': 'Suites and executive rooms'},
        ]
        
        for floor_data_item in floor_data:
            Floor.objects.get_or_create(
                hotel=hotel,
                number=floor_data_item['number'],
                defaults=floor_data_item
            )
        
        # Create amenities
        for amenity_data in amenities_data:
            Amenity.objects.get_or_create(
                hotel=hotel,
                name=amenity_data['name'],
                defaults=amenity_data
            )
    
    print("✓ Created configurations for all hotels")

def create_rooms(hotels):
    """Create sample rooms for each hotel"""
    print("Creating rooms...")
    
    room_configs = [
        # Standard rooms
        {'type': 'Standard Room', 'bed': 'Double Bed', 'floor': 1, 'price': 150, 'count': 10},
        {'type': 'Standard Room', 'bed': 'Twin Beds', 'floor': 1, 'price': 160, 'count': 5},
        
        # Deluxe rooms
        {'type': 'Deluxe Room', 'bed': 'Queen Bed', 'floor': 2, 'price': 220, 'count': 8},
        {'type': 'Deluxe Room', 'bed': 'King Bed', 'floor': 2, 'price': 250, 'count': 6},
        
        # Suites
        {'type': 'Junior Suite', 'bed': 'King Bed', 'floor': 3, 'price': 350, 'count': 4},
        {'type': 'Executive Suite', 'bed': 'King Bed', 'floor': 4, 'price': 500, 'count': 2},
        {'type': 'Presidential Suite', 'bed': 'King Bed', 'floor': 4, 'price': 800, 'count': 1},
    ]
    
    for hotel in hotels:
        room_number = 101
        
        for config in room_configs:
            room_type = RoomType.objects.filter(hotel=hotel, name=config['type']).first()
            bed_type = BedType.objects.filter(hotel=hotel, name=config['bed']).first()
            floor = Floor.objects.filter(hotel=hotel, number=config['floor']).first()
            
            for i in range(config['count']):
                if not Room.objects.filter(hotel=hotel, room_number=str(room_number)).exists():
                    room = Room.objects.create(
                        hotel=hotel,
                        room_number=str(room_number),
                        room_type=room_type,
                        bed_type=bed_type,
                        floor=floor,
                        price=Decimal(str(config['price'])),
                        max_guests=2 if 'Suite' in config['type'] else 2,
                        room_size=300 if 'Suite' in config['type'] else 250,
                        view_type='City' if room_number % 2 == 0 else 'Garden',
                        has_wifi=True,
                        has_ac=True,
                        has_tv=True,
                        has_minibar='Suite' in config['type'],
                        has_balcony=room_number % 3 == 0,
                        has_work_desk=True,
                        has_seating_area='Suite' in config['type'],
                        has_kitchenette='Executive' in config['type'] or 'Presidential' in config['type'],
                        has_living_room='Executive' in config['type'] or 'Presidential' in config['type'],
                        description=f"Beautiful {config['type'].lower()} with {config['bed'].lower()}"
                    )
                    
                    # Add amenities to suites
                    if 'Suite' in config['type']:
                        amenities = Amenity.objects.filter(hotel=hotel)[:4]
                        room.amenities.set(amenities)
                
                room_number += 1
        
        print(f"✓ Created rooms for {hotel.name}")

def create_services(hotels):
    """Create hotel services"""
    print("Creating services...")
    
    services_data = [
        {'name': 'Airport Transfer', 'description': 'One-way airport shuttle service', 'price': 25.00},
        {'name': 'Laundry Service', 'description': 'Same-day laundry and dry cleaning', 'price': 15.00},
        {'name': 'Spa Treatment', 'description': '60-minute relaxation massage', 'price': 120.00},
        {'name': 'Room Service Breakfast', 'description': 'Continental breakfast delivered to room', 'price': 35.00},
        {'name': 'Late Checkout', 'description': 'Checkout extension until 3 PM', 'price': 50.00},
        {'name': 'Pet Care Service', 'description': 'Pet sitting and walking service', 'price': 40.00},
        {'name': 'Business Center Access', 'description': '24-hour business center usage', 'price': 20.00},
        {'name': 'Valet Parking', 'description': 'Premium valet parking service', 'price': 30.00},
    ]
    
    for hotel in hotels:
        for service_data in services_data:
            Service.objects.get_or_create(
                hotel=hotel,
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'price': Decimal(str(service_data['price']))
                }
            )
        
        print(f"✓ Created services for {hotel.name}")

def create_companies(hotels):
    """Create corporate clients"""
    print("Creating corporate clients...")
    
    companies_data = [
        {
            'name': 'TechCorp Solutions',
            'contact_person': 'Michael Chen',
            'email': 'michael.chen@techcorp.com',
            'phone': '+1-555-0301',
            'address': '100 Tech Plaza, Silicon Valley, CA',
            'tax_id': 'TC-2024-001',
            'discount_percentage': 15.00,
            'credit_limit': 50000.00,
            'payment_terms': 'Net 30 days'
        },
        {
            'name': 'Global Consulting Group',
            'contact_person': 'Emma Rodriguez',
            'email': 'emma.r@globalconsulting.com',
            'phone': '+1-555-0302',
            'address': '200 Business Center, New York, NY',
            'tax_id': 'GCG-2024-002',
            'discount_percentage': 20.00,
            'credit_limit': 75000.00,
            'payment_terms': 'Net 15 days'
        },
        {
            'name': 'International Finance Corp',
            'contact_person': 'David Kim',
            'email': 'david.kim@intlfinance.com',
            'phone': '+1-555-0303',
            'address': '300 Financial District, Chicago, IL',
            'tax_id': 'IFC-2024-003',
            'discount_percentage': 25.00,
            'credit_limit': 100000.00,
            'payment_terms': 'Net 45 days'
        }
    ]
    
    for hotel in hotels:
        for company_data in companies_data:
            Company.objects.get_or_create(
                hotel=hotel,
                name=company_data['name'],
                defaults={
                    'contact_person': company_data['contact_person'],
                    'email': company_data['email'],
                    'phone': company_data['phone'],
                    'address': company_data['address'],
                    'tax_id': company_data['tax_id'],
                    'discount_percentage': Decimal(str(company_data['discount_percentage'])),
                    'credit_limit': Decimal(str(company_data['credit_limit'])),
                    'payment_terms': company_data['payment_terms'],
                    'notes': f'Corporate client established {date.today().year}'
                }
            )
        
        print(f"✓ Created corporate clients for {hotel.name}")

def create_guests():
    """Create sample guest profiles"""
    print("Creating guest profiles...")
    
    guests_data = [
        {
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'email': 'alice.johnson@email.com',
            'phone': '+1-555-0401',
            'nationality': 'US',
            'loyalty_status': 'gold',
            'loyalty_points': 2500
        },
        {
            'first_name': 'Robert',
            'last_name': 'Williams',
            'email': 'robert.williams@email.com',
            'phone': '+1-555-0402',
            'nationality': 'CA',
            'loyalty_status': 'silver',
            'loyalty_points': 1200
        },
        {
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'email': 'maria.garcia@email.com',
            'phone': '+1-555-0403',
            'nationality': 'MX',
            'loyalty_status': 'platinum',
            'loyalty_points': 5000
        },
        {
            'first_name': 'James',
            'last_name': 'Brown',
            'email': 'james.brown@email.com',
            'phone': '+1-555-0404',
            'nationality': 'GB',
            'loyalty_status': 'bronze',
            'loyalty_points': 500
        },
        {
            'first_name': 'Lisa',
            'last_name': 'Davis',
            'email': 'lisa.davis@email.com',
            'phone': '+1-555-0405',
            'nationality': 'AU',
            'loyalty_status': 'gold',
            'loyalty_points': 3200
        }
    ]
    
    for guest_data in guests_data:
        if not GuestProfile.objects.filter(email=guest_data['email']).exists():
            guest_data['national_id_card'] = f"ID{guest_data['phone'][-6:]}"
            GuestProfile.objects.create(**guest_data)
            print(f"✓ Created guest: {guest_data['first_name']} {guest_data['last_name']}")

def create_staff_users(hotels):
    """Create staff users for hotels"""
    print("Creating staff users...")
    
    staff_data = [
        {
            'username': 'manager1',
            'email': 'manager@grandpalace.com',
            'first_name': 'Jennifer',
            'last_name': 'Wilson',
            'role': 'Manager',
            'phone': '+1-555-0501'
        },
        {
            'username': 'receptionist1',
            'email': 'reception@grandpalace.com',
            'first_name': 'Mark',
            'last_name': 'Thompson',
            'role': 'Receptionist',
            'phone': '+1-555-0502'
        },
        {
            'username': 'housekeeping1',
            'email': 'housekeeping@grandpalace.com',
            'first_name': 'Anna',
            'last_name': 'Martinez',
            'role': 'Housekeeping',
            'phone': '+1-555-0503'
        }
    ]
    
    for i, staff in enumerate(staff_data):
        if not User.objects.filter(username=staff['username']).exists():
            hotel = hotels[i % len(hotels)] if hotels else None
            user = User.objects.create_user(
                username=staff['username'],
                email=staff['email'],
                password='password123',
                first_name=staff['first_name'],
                last_name=staff['last_name'],
                role=staff['role'],
                phone=staff['phone'],
                assigned_hotel=hotel
            )
            
            # Set role-based permissions
            if staff['role'] == 'Manager':
                # Managers get most permissions
                permissions = [
                    'can_view_hotels', 'can_view_rooms', 'can_add_rooms', 'can_change_rooms',
                    'can_view_reservations', 'can_add_reservations', 'can_change_reservations',
                    'can_view_guests', 'can_add_guests', 'can_change_guests',
                    'can_view_staff', 'can_add_staff', 'can_change_staff',
                    'can_view_housekeeping', 'can_add_housekeeping', 'can_change_housekeeping',
                    'can_view_billing', 'can_add_billing', 'can_view_reports'
                ]
            elif staff['role'] == 'Receptionist':
                # Receptionists get front desk permissions
                permissions = [
                    'can_view_rooms', 'can_view_reservations', 'can_add_reservations', 'can_change_reservations',
                    'can_view_guests', 'can_add_guests', 'can_change_guests',
                    'can_view_checkins', 'can_add_checkins', 'can_change_checkins',
                    'can_view_billing', 'can_add_billing'
                ]
            elif staff['role'] == 'Housekeeping':
                # Housekeeping gets limited permissions
                permissions = [
                    'can_view_rooms', 'can_view_housekeeping', 'can_add_housekeeping', 'can_change_housekeeping'
                ]
            else:
                permissions = []
            
            for perm in permissions:
                if hasattr(user, perm):
                    setattr(user, perm, True)
            
            user.save()
            print(f"✓ Created staff: {user.username} ({user.role})")

def main():
    """Main function to populate all sample data"""
    print("🏨 Starting Hotel Management System Data Population")
    print("=" * 60)
    
    try:
        # Create subscription plans first
        create_subscription_plans()
        
        # Create users
        owners = create_users()
        
        # Create hotels
        hotels = create_hotels(owners)
        
        # Create configurations
        create_configurations(hotels)
        
        # Create rooms
        create_rooms(hotels)
        
        # Create services
        create_services(hotels)
        
        # Create companies
        create_companies(hotels)
        
        # Create guests
        create_guests()
        
        # Create staff users
        create_staff_users(hotels)
        
        print("\n" + "=" * 60)
        print("🎉 Sample data population completed successfully!")
        print("\nLogin credentials:")
        print("- Admin: admin / admin123")
        print("- Owner: john_owner / password123")
        print("- Manager: manager1 / password123")
        print("- Receptionist: receptionist1 / password123")
        print("- Housekeeping: housekeeping1 / password123")
        
    except Exception as e:
        print(f"❌ Error during data population: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()