from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from .email_utils import send_subscription_welcome_email
from hotels.models import Hotel, HotelSubscription
from tenants.models import SubscriptionPlan

User = get_user_model()

@csrf_exempt
def test_subscription_email(request):
    """
    Test function to send subscription welcome email to hadiraza1109@gmail.com
    """
    try:
        # Create or get test user
        test_email = "hadiraza1109@gmail.com"
        
        # Try to get existing user or create new one
        try:
            test_user = User.objects.get(email=test_email)
        except User.DoesNotExist:
            test_user = User.objects.create_user(
                username="testhotelowner",
                email=test_email,
                password="testpassword123",
                first_name="Hadi",
                last_name="Raza",
                role="Owner",
                is_active=True
            )
        
        # Create or get test hotel
        try:
            test_hotel = Hotel.objects.filter(owner=test_user).first()
            if not test_hotel:
                raise Hotel.DoesNotExist
        except Hotel.DoesNotExist:
            test_hotel = Hotel.objects.create(
                owner=test_user,
                name="Grand Palace Hotel",
                address="123 Luxury Street",
                city="Karachi",
                country="Pakistan",
                phone="+92-300-1234567",
                email=test_email,
                currency="PKR",
                is_active=True
            )
        
        # Create or get test subscription plan
        try:
            test_plan = SubscriptionPlan.objects.get(name="Premium")
        except SubscriptionPlan.DoesNotExist:
            test_plan = SubscriptionPlan.objects.create(
                name="Premium",
                description="Premium hotel management plan with advanced features",
                price_monthly=99.99,
                price_yearly=999.99,
                max_rooms=100,
                max_managers=10,
                has_advanced_analytics=True,
                has_priority_support=True,
                is_active=True
            )
        
        # Create test subscription
        start_date = date.today()
        end_date = start_date + timedelta(days=30)
        
        try:
            test_subscription = HotelSubscription.objects.get(hotel=test_hotel)
            # Update existing subscription
            test_subscription.plan = test_plan
            test_subscription.start_date = start_date
            test_subscription.end_date = end_date
            test_subscription.status = 'active'
            test_subscription.save()
        except HotelSubscription.DoesNotExist:
            test_subscription = HotelSubscription.objects.create(
                hotel=test_hotel,
                plan=test_plan,
                start_date=start_date,
                end_date=end_date,
                billing_cycle='monthly',
                status='active',
                auto_renew=True
            )
        
        # Set temporary password for email
        test_user.temp_password = "testpassword123"
        test_user.save()
        
        # Send the welcome email
        email_sent = send_subscription_welcome_email(test_subscription, "testpassword123")
        
        if email_sent:
            return JsonResponse({
                'success': True,
                'message': f'Subscription welcome email sent successfully to {test_email}',
                'details': {
                    'hotel_name': test_hotel.name,
                    'plan_name': test_plan.name,
                    'owner_name': test_user.get_full_name(),
                    'start_date': start_date.strftime('%B %d, %Y'),
                    'end_date': end_date.strftime('%B %d, %Y')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to send email. Check email configuration.'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })