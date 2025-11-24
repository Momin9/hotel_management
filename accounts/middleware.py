from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse
from datetime import date
from hotels.models import HotelSubscription

class SubscriptionMiddleware:
    """Middleware to check subscription status for non-superuser requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that don't require subscription check
        self.exempt_paths = [
            '/login/',
            '/logout/',
            '/admin/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Skip check for exempt paths
        if any(request.path.startswith(path) for path in self.exempt_paths):
            response = self.get_response(request)
            return response
        
        # Skip check for unauthenticated users and superusers
        if not request.user.is_authenticated or request.user.is_superuser:
            response = self.get_response(request)
            return response
        
        # Check subscription status
        if not self.check_subscription_status(request.user):
            messages.error(request, 'Your subscription has expired or is inactive. Please contact administrator.')
            logout(request)
            return redirect('accounts:login')
        
        response = self.get_response(request)
        return response
    
    def check_subscription_status(self, user):
        """Check if user has active subscription"""
        try:
            if user.role == 'Owner':
                # Check if owner's hotels have active subscriptions
                from hotels.models import Hotel
                hotels = Hotel.objects.filter(owner=user)
                for hotel in hotels:
                    active_subscription = HotelSubscription.objects.filter(
                        hotel=hotel,
                        status='active',
                        start_date__lte=date.today(),
                        end_date__gte=date.today()
                    ).exists()
                    if active_subscription:
                        return True
                return False
            elif hasattr(user, 'staff_profile'):
                # Check if staff's hotel has active subscription
                hotel = user.staff_profile.hotel
                return HotelSubscription.objects.filter(
                    hotel=hotel,
                    status='active',
                    start_date__lte=date.today(),
                    end_date__gte=date.today()
                ).exists()
            return True  # Default allow for other roles
        except:
            return False