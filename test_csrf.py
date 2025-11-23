#!/usr/bin/env python3
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.test import RequestFactory
from django.middleware.csrf import get_token
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.csrf import CsrfViewMiddleware

# Create a test request
factory = RequestFactory()
request = factory.get('/accounts/login/')

# Add session middleware
session_middleware = SessionMiddleware(lambda req: None)
session_middleware.process_request(request)
request.session.save()

# Add CSRF middleware
csrf_middleware = CsrfViewMiddleware(lambda req: None)
csrf_middleware.process_request(request)

# Get CSRF token
token = get_token(request)
print(f"CSRF Token generated: {token}")
print(f"Token length: {len(token)}")
print("CSRF middleware is working correctly!")