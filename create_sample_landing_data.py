#!/usr/bin/env python3
"""
Create sample data for landing page trusted hotels section
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from accounts.models import TrustedHotel, LandingPageContent

def create_sample_data():
    """Create sample trusted hotels and landing page content"""
    
    # Create landing page content
    content, created = LandingPageContent.objects.get_or_create(
        is_active=True,
        defaults={
            'section_title': 'Trusted By Leading Hotels',
            'section_subtitle': 'Join thousands of hotels worldwide using AuraStay'
        }
    )
    
    if created:
        print("✅ Created landing page content")
    else:
        print("ℹ️  Landing page content already exists")
    
    # Sample trusted hotels data
    trusted_hotels_data = [
        {'name': 'Royal Palace Hotel', 'icon': 'fas fa-crown', 'order': 1},
        {'name': 'Grand Resort & Spa', 'icon': 'fas fa-building', 'order': 2},
        {'name': 'Luxury Suites', 'icon': 'fas fa-bed', 'order': 3},
        {'name': 'Elite Hotels Group', 'icon': 'fas fa-star', 'order': 4},
        {'name': 'Ocean View Resort', 'icon': 'fas fa-water', 'order': 5},
        {'name': 'Mountain Lodge', 'icon': 'fas fa-mountain', 'order': 6},
        {'name': 'City Center Hotel', 'icon': 'fas fa-city', 'order': 7},
        {'name': 'Boutique Collection', 'icon': 'fas fa-gem', 'order': 8},
    ]
    
    created_count = 0
    for hotel_data in trusted_hotels_data:
        hotel, created = TrustedHotel.objects.get_or_create(
            name=hotel_data['name'],
            defaults={
                'icon': hotel_data['icon'],
                'order': hotel_data['order'],
                'is_active': True
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Created trusted hotel: {hotel.name}")
        else:
            print(f"ℹ️  Trusted hotel already exists: {hotel.name}")
    
    print(f"\n🎉 Sample data creation completed!")
    print(f"📊 Created {created_count} new trusted hotels")
    print(f"📊 Total trusted hotels: {TrustedHotel.objects.count()}")
    print(f"📊 Active trusted hotels: {TrustedHotel.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    create_sample_data()