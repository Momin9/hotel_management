#!/usr/bin/env python
import os
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelmanagement.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    try:
        print("Testing email configuration...")
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        # Send test email
        subject = 'AuraStay Email Test'
        message = 'This is a test email from AuraStay hotel management system.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.EMAIL_HOST_USER]  # Send to self
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_email()
    if success:
        print("\n🎉 Email server is working correctly!")
    else:
        print("\n⚠️  Email server configuration needs attention.")