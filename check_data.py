#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from accounts.models import *
from tenants.models import *

print('=== DETAILED DATA ANALYSIS ===')

print('\n--- FEATURES ---')
for f in Feature.objects.all():
    print(f'{f.title} - {f.color} - Order: {f.order}')

print('\n--- SUBSCRIPTION PLANS ---')
for p in SubscriptionPlan.objects.all():
    print(f'{p.name} - Monthly: ${p.price_monthly} - Yearly: ${p.price_yearly} - Rooms: {p.max_rooms}')

print('\n--- PAGE CONTENTS ---')
for pc in PageContent.objects.all()[:15]:
    print(f'{pc.page_name}: {pc.page_title}')

print('\n--- FOOTER INFO ---')
footer = Footer.objects.first()
if footer:
    print(f'Company: {footer.company_name}')
    print(f'Email: {footer.email}')
    print(f'Phone: {footer.phone}')

print('\n--- ABOUT US ---')
about = AboutUs.objects.first()
if about:
    print(f'Active: {about.is_active}')
    print(f'Mission: {about.mission_statement[:100]}...')

print('\n--- TERMS & PRIVACY ---')
terms = TermsOfService.objects.first()
privacy = PrivacyPolicy.objects.first()
print(f'Terms: {terms.title if terms else "None"}')
print(f'Privacy: {privacy.title if privacy else "None"}')