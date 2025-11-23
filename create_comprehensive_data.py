#!/usr/bin/env python3
import os
import django
from datetime import date, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import SubscriptionPlan
from hotels.models import Hotel, HotelSubscription, Payment, SubscriptionHistory
from crm.models import GuestProfile
from reservations.models import Reservation

User = get_user_model()

def create_comprehensive_data():
    try:
        print("Creating comprehensive hotel management data...")
        
        # Create subscription plans
        plans_data = [
            {'name': 'Basic', 'price_monthly': 29, 'price_yearly': 290, 'max_rooms': 50, 'max_managers': 2, 'max_reports': 10},
            {'name': 'Premium', 'price_monthly': 79, 'price_yearly': 790, 'max_rooms': 200, 'max_managers': 10, 'max_reports': 50},
            {'name': 'Enterprise', 'price_monthly': 199, 'price_yearly': 1990, 'max_rooms': 1000, 'max_managers': 50, 'max_reports': 999},
            {'name': 'Luxury', 'price_monthly': 399, 'price_yearly': 3990, 'max_rooms': 2000, 'max_managers': 100, 'max_reports': 9999},
        ]
        
        created_plans = []
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'description': f'{plan_data["name"]} plan with {plan_data["max_rooms"]} rooms',
                    'price_monthly': plan_data['price_monthly'],
                    'price_yearly': plan_data['price_yearly'],
                    'max_rooms': plan_data['max_rooms'],
                    'max_managers': plan_data['max_managers'],
                    'max_reports': plan_data['max_reports'],
                    'is_active': True
                }
            )
            created_plans.append(plan)
            if created:
                print(f"✓ Created subscription plan: {plan.name}")
        
        # Create multiple hotel owners
        owners_data = [
            {'username': 'owner1', 'email': 'owner1@aurastay.com', 'first_name': 'Muhammad', 'last_name': 'Ali Khan', 'phone': '+92-300-1234567'},
            {'username': 'owner2', 'email': 'owner2@aurastay.com', 'first_name': 'Sarah', 'last_name': 'Ahmed', 'phone': '+971-50-9876543'},
            {'username': 'owner3', 'email': 'owner3@aurastay.com', 'first_name': 'Ahmed', 'last_name': 'Hassan', 'phone': '+1-555-0123'},
            {'username': 'owner4', 'email': 'owner4@aurastay.com', 'first_name': 'Fatima', 'last_name': 'Sheikh', 'phone': '+44-20-7946-0958'},
            {'username': 'owner5', 'email': 'owner5@aurastay.com', 'first_name': 'Omar', 'last_name': 'Malik', 'phone': '+33-1-42-86-83-26'},
        ]
        
        created_owners = []
        for owner_data in owners_data:
            owner, created = User.objects.get_or_create(
                username=owner_data['username'],
                defaults={
                    'email': owner_data['email'],
                    'first_name': owner_data['first_name'],
                    'last_name': owner_data['last_name'],
                    'phone': owner_data['phone'],
                    'role': 'Owner',
                    'is_active': True
                }
            )
            if created:
                owner.set_password('password123')
                owner.save()
                print(f"✓ Created hotel owner: {owner.first_name} {owner.last_name}")
            created_owners.append(owner)
        
        # Create multiple hotels
        hotels_data = [
            {'name': 'Royal Palace Hotel Karachi', 'owner': created_owners[0], 'city': 'Karachi', 'country': 'Pakistan', 'rooms': 45},
            {'name': 'Grand Seaside Resort Dubai', 'owner': created_owners[1], 'city': 'Dubai', 'country': 'UAE', 'rooms': 120},
            {'name': 'Metropolitan Luxury Suites', 'owner': created_owners[2], 'city': 'New York', 'country': 'USA', 'rooms': 80},
            {'name': 'Thames View Hotel London', 'owner': created_owners[3], 'city': 'London', 'country': 'UK', 'rooms': 65},
            {'name': 'Champs-Élysées Boutique Hotel', 'owner': created_owners[4], 'city': 'Paris', 'country': 'France', 'rooms': 35},
            {'name': 'Marina Bay Luxury Resort', 'owner': created_owners[0], 'city': 'Karachi', 'country': 'Pakistan', 'rooms': 90},
            {'name': 'Desert Oasis Hotel', 'owner': created_owners[1], 'city': 'Dubai', 'country': 'UAE', 'rooms': 150},
            {'name': 'Central Park Plaza', 'owner': created_owners[2], 'city': 'New York', 'country': 'USA', 'rooms': 200},
        ]
        
        created_hotels = []
        for hotel_data in hotels_data:
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data['name'],
                defaults={
                    'owner': hotel_data['owner'],
                    'address': f'123 Premium Street, {hotel_data["city"]}',
                    'city': hotel_data['city'],
                    'country': hotel_data['country'],
                    'phone': f'+{random.randint(1,99)}-{random.randint(100,999)}-{random.randint(1000,9999)}',
                    'email': f'info@{hotel_data["name"].lower().replace(" ", "").replace("-", "")}.com',
                    'is_active': True
                }
            )
            if created:
                print(f"✓ Created hotel: {hotel.name} ({hotel_data['rooms']} rooms)")
            created_hotels.append((hotel, hotel_data['rooms']))
        
        # Create hotel subscriptions with different plans
        for i, (hotel, room_count) in enumerate(created_hotels):
            # Assign plans based on hotel size
            if room_count <= 50:
                plan = created_plans[0]  # Basic
            elif room_count <= 100:
                plan = created_plans[1]  # Premium
            elif room_count <= 150:
                plan = created_plans[2]  # Enterprise
            else:
                plan = created_plans[3]  # Luxury
            
            subscription, created = HotelSubscription.objects.get_or_create(
                hotel=hotel,
                defaults={
                    'plan': plan,
                    'start_date': date.today() - timedelta(days=random.randint(30, 365)),
                    'end_date': date.today() + timedelta(days=random.randint(30, 365)),
                    'billing_cycle': random.choice(['monthly', 'yearly']),
                    'status': 'active',
                    'auto_renew': True
                }
            )
            if created:
                print(f"✓ Created {plan.name} subscription for: {hotel.name}")
                
                # Create payment record
                amount = plan.price_yearly if subscription.billing_cycle == 'yearly' else plan.price_monthly
                Payment.objects.create(
                    hotel_subscription=subscription,
                    amount=amount,
                    payment_date=subscription.start_date,
                    payment_method='credit_card',
                    status='completed'
                )
                
                # Create subscription history
                SubscriptionHistory.objects.create(
                    hotel_subscription=subscription,
                    action='started',
                    action_date=subscription.start_date
                )
        
        # Create rooms for each hotel
        room_types = ['Single', 'Double', 'Twin', 'Triple']
        room_statuses = ['Available', 'Occupied', 'Cleaning', 'Maintenance']
        
        try:
            from hotels.models import Room
            for hotel, room_count in created_hotels:
                for room_num in range(1, room_count + 1):
                    floor = (room_num - 1) // 10 + 1
                    room_number = f"{floor}{room_num:02d}"
                    
                    room, created = Room.objects.get_or_create(
                        hotel=hotel,
                        room_number=room_number,
                        defaults={
                            'type': random.choice(room_types),
                            'category': random.choice(['Standard', 'Deluxe', 'Suite']),
                            'bed': random.choice(['King', 'Queen', 'DoubleBed']),
                            'price': random.randint(100, 500),
                            'status': random.choice(room_statuses)
                        }
                    )
                    if created and room_num <= 5:  # Only print first 5 rooms per hotel
                        print(f"✓ Created room {room_number} for {hotel.name}")
                
                print(f"✓ Created {room_count} rooms for {hotel.name}")
        except ImportError:
            print("⚠ Room model not available, skipping room creation")
        
        # Create staff for each hotel with different roles
        staff_roles = ['Manager', 'Staff', 'Receptionist', 'Housekeeper', 'Maintenance']
        staff_names = [
            ('John', 'Smith'), ('Emma', 'Johnson'), ('Michael', 'Brown'), ('Sarah', 'Davis'),
            ('David', 'Wilson'), ('Lisa', 'Garcia'), ('James', 'Martinez'), ('Maria', 'Lopez'),
            ('Robert', 'Anderson'), ('Jennifer', 'Taylor'), ('William', 'Thomas'), ('Linda', 'Jackson'),
            ('Richard', 'White'), ('Patricia', 'Harris'), ('Charles', 'Martin'), ('Barbara', 'Thompson')
        ]
        
        staff_counter = 1
        for hotel, _ in created_hotels:
            # Create 5-8 staff members per hotel
            staff_count = random.randint(5, 8)
            for i in range(staff_count):
                first_name, last_name = random.choice(staff_names)
                role = staff_roles[i % len(staff_roles)]
                
                username = f"staff{staff_counter}"
                email = f"staff{staff_counter}@{hotel.name.lower().replace(' ', '').replace('-', '')}.com"
                
                staff_user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'role': role,
                        'assigned_hotel': hotel,
                        'phone': f'+1-555-{random.randint(1000,9999)}',
                        'is_active': True
                    }
                )
                if created:
                    staff_user.set_password('password123')
                    staff_user.save()
                    if i < 2:  # Only print first 2 staff per hotel
                        print(f"✓ Created {role}: {first_name} {last_name} for {hotel.name}")
                
                staff_counter += 1
            
            print(f"✓ Created {staff_count} staff members for {hotel.name}")
        
        # Create guests
        guest_names = [
            ('Alex', 'Johnson', 'alex.johnson@email.com'),
            ('Maria', 'Garcia', 'maria.garcia@email.com'),
            ('James', 'Wilson', 'james.wilson@email.com'),
            ('Sophie', 'Brown', 'sophie.brown@email.com'),
            ('Ahmed', 'Ali', 'ahmed.ali@email.com'),
            ('Elena', 'Rodriguez', 'elena.rodriguez@email.com'),
            ('David', 'Chen', 'david.chen@email.com'),
            ('Fatima', 'Hassan', 'fatima.hassan@email.com'),
        ]
        
        created_guests = []
        for first_name, last_name, email in guest_names:
            guest, created = GuestProfile.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': f'+1-555-{random.randint(1000,9999)}',
                    'nationality': random.choice(['USA', 'UK', 'Canada', 'Australia', 'Germany']),
                    'loyalty_status': random.choice(['bronze', 'silver', 'gold']),
                    'loyalty_points': random.randint(0, 5000)
                }
            )
            if created:
                print(f"✓ Created guest: {first_name} {last_name}")
            created_guests.append(guest)
        
        print(f"\n{'='*60}")
        print("COMPREHENSIVE DATA CREATION COMPLETE!")
        print(f"{'='*60}")
        print(f"✓ Created {len(created_plans)} subscription plans")
        print(f"✓ Created {len(created_owners)} hotel owners")
        print(f"✓ Created {len(created_hotels)} hotels")
        print(f"✓ Created {User.objects.filter(role__in=['Manager', 'Staff', 'Receptionist', 'Housekeeper', 'Maintenance']).count()} staff members")
        print(f"✓ Created {len(created_guests)} guests")
        
        print(f"\n{'='*60}")
        print("LOGIN CREDENTIALS:")
        print(f"{'='*60}")
        print("Super Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nHotel Owners:")
        for i, owner in enumerate(created_owners, 1):
            print(f"  Owner {i}: {owner.username} / password123")
        print("\nStaff Members:")
        print("  Username: staff1, staff2, staff3, etc.")
        print("  Password: password123")
        
        print(f"\n{'='*60}")
        print("HOTEL SUMMARY:")
        print(f"{'='*60}")
        for hotel, room_count in created_hotels:
            subscription = HotelSubscription.objects.filter(hotel=hotel).first()
            staff_count = User.objects.filter(assigned_hotel=hotel).count()
            print(f"🏨 {hotel.name}")
            print(f"   📍 {hotel.city}, {hotel.country}")
            print(f"   👤 Owner: {hotel.owner.get_full_name()}")
            print(f"   📋 Plan: {subscription.plan.name if subscription else 'No Plan'}")
            print(f"   🏠 Rooms: {room_count}")
            print(f"   👥 Staff: {staff_count}")
            print()
        
    except Exception as e:
        print(f"❌ Error creating comprehensive data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_comprehensive_data()