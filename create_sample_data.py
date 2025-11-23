#!/usr/bin/env python3
import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import SubscriptionPlan
from hotels.models import Hotel, HotelSubscription, Payment, SubscriptionHistory

User = get_user_model()

def create_sample_data():
    try:
        # Create subscription plans
        plans_data = [
            {'name': 'Basic', 'price_monthly': 29, 'max_rooms': 50, 'max_managers': 2, 'max_reports': 10},
            {'name': 'Premium', 'price_monthly': 79, 'max_rooms': 200, 'max_managers': 10, 'max_reports': 50},
            {'name': 'Enterprise', 'price_monthly': 199, 'max_rooms': 1000, 'max_managers': 50, 'max_reports': 999},
        ]
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults={
                    'description': f'{plan_data["name"]} plan with {plan_data["max_rooms"]} rooms',
                    'price_monthly': plan_data['price_monthly'],
                    'price_yearly': plan_data['price_monthly'] * 10,  # 2 months free
                    'max_rooms': plan_data['max_rooms'],
                    'max_managers': plan_data['max_managers'],
                    'max_reports': plan_data['max_reports'],
                    'is_active': True
                }
            )
            if created:
                print(f"Created subscription plan: {plan.name}")
        
        # Create hotel owners
        owners_data = [
            {'username': 'owner1', 'email': 'owner1@hotel.com', 'first_name': 'Muhammad', 'last_name': 'Ali Khan'},
            {'username': 'owner2', 'email': 'owner2@hotel.com', 'first_name': 'Sarah', 'last_name': 'Ahmed'},
        ]
        
        for owner_data in owners_data:
            owner, created = User.objects.get_or_create(
                username=owner_data['username'],
                defaults={
                    'email': owner_data['email'],
                    'first_name': owner_data['first_name'],
                    'last_name': owner_data['last_name'],
                    'role': 'Owner',
                    'is_active': True
                }
            )
            if created:
                owner.set_password('password123')
                owner.save()
                print(f"Created hotel owner: {owner.first_name} {owner.last_name}")
        
        # Create hotels
        hotels_data = [
            {'name': 'Royal Palace Hotel', 'owner_username': 'owner1', 'city': 'Karachi', 'country': 'Pakistan'},
            {'name': 'Grand Seaside Resort', 'owner_username': 'owner2', 'city': 'Dubai', 'country': 'UAE'},
        ]
        
        for hotel_data in hotels_data:
            owner = User.objects.get(username=hotel_data['owner_username'])
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data['name'],
                defaults={
                    'owner': owner,
                    'address': f'123 Main Street, {hotel_data["city"]}',
                    'city': hotel_data['city'],
                    'country': hotel_data['country'],
                    'phone': '+1-555-0123',
                    'email': f'info@{hotel_data["name"].lower().replace(" ", "")}.com',
                    'is_active': True
                }
            )
            if created:
                print(f"Created hotel: {hotel.name}")
        
        # Create hotel subscriptions
        hotels = Hotel.objects.all()
        basic_plan = SubscriptionPlan.objects.get(name='Basic')
        
        for hotel in hotels:
            subscription, created = HotelSubscription.objects.get_or_create(
                hotel=hotel,
                defaults={
                    'plan': basic_plan,
                    'start_date': date.today(),
                    'end_date': date.today() + timedelta(days=365),
                    'status': 'active',
                    'auto_renew': True
                }
            )
            if created:
                print(f"Created subscription for: {hotel.name}")
                
                # Create payment record
                Payment.objects.create(
                    hotel_subscription=subscription,
                    amount=basic_plan.price_monthly * 12,  # Yearly payment
                    payment_date=date.today()
                )
                
                # Create subscription history
                SubscriptionHistory.objects.create(
                    hotel_subscription=subscription,
                    action='started',
                    action_date=date.today()
                )
        
        print("\nSample data created successfully!")
        print("\nLogin credentials:")
        print("Superuser - Username: admin, Password: admin123")
        print("Hotel Owner 1 - Username: owner1, Password: password123")
        print("Hotel Owner 2 - Username: owner2, Password: password123")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")

if __name__ == "__main__":
    create_sample_data()