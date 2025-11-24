from datetime import date, timedelta
from django.utils import timezone
from hotels.models import HotelSubscription

def check_free_trial_restrictions(user):
    """Check if user is on free trial and if trial has expired"""
    if not user.assigned_hotel and user.role != 'Owner':
        return {'is_free_trial': False, 'trial_expired': False}
    
    hotel = user.assigned_hotel if user.assigned_hotel else user.owned_hotels.first()
    if not hotel:
        return {'is_free_trial': False, 'trial_expired': False}
    
    # Get active subscription
    subscription = HotelSubscription.objects.filter(
        hotel=hotel,
        status='active',
        start_date__lte=date.today(),
        end_date__gte=date.today()
    ).first()
    
    if not subscription:
        return {'is_free_trial': False, 'trial_expired': True}
    
    is_free_trial = subscription.plan.is_free_trial
    trial_expired = False
    
    if is_free_trial:
        # Check if trial period (30 days) has expired
        trial_start = subscription.start_date
        trial_end = trial_start + timedelta(days=30)
        trial_expired = date.today() > trial_end
    
    return {
        'is_free_trial': is_free_trial,
        'trial_expired': trial_expired,
        'subscription': subscription,
        'hotel': hotel
    }

def get_currency_symbol(currency_code):
    """Get currency symbol from currency code"""
    currency_symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'AUD': 'A$',
        'CAD': 'C$', 'CHF': 'CHF', 'CNY': '¥', 'INR': '₹', 'PKR': '₨',
        'BRL': 'R$', 'RUB': '₽', 'KRW': '₩', 'TRY': '₺', 'AED': 'د.إ',
        'SAR': '﷼', 'EGP': '£', 'SEK': 'kr', 'NOK': 'kr', 'NZD': 'NZ$',
        'MXN': '$', 'SGD': 'S$', 'HKD': 'HK$', 'ZAR': 'R'
    }
    return currency_symbols.get(currency_code, currency_code)