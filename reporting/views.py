from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from hotels.models import Room
from reservations.models import Reservation
from billing.models import Invoice
from django.db.models import Count, Sum
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    """Reports dashboard"""
    return render(request, 'reporting/dashboard.html')

@login_required
def occupancy_report(request):
    """Occupancy report"""
    rooms = Room.objects.all()
    total_rooms = rooms.count()
    occupied_rooms = rooms.filter(status='occupied').count()
    available_rooms = rooms.filter(status='available').count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    context = {
        'rooms': rooms,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'occupancy_rate': round(occupancy_rate, 1),
    }
    
    return render(request, 'reporting/occupancy.html', context)

@login_required
def revenue_report(request):
    """Revenue report"""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    total_revenue = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_revenue = Invoice.objects.filter(
        status='paid',
        created_at__date__gte=month_start
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'reporting/revenue.html', context)

@login_required
def guest_report(request):
    """Guest report"""
    total_guests = Reservation.objects.values('guest').distinct().count()
    repeat_guests = Reservation.objects.values('guest').annotate(
        reservation_count=Count('id')
    ).filter(reservation_count__gt=1).count()
    
    context = {
        'total_guests': total_guests,
        'repeat_guests': repeat_guests,
    }
    
    return render(request, 'reporting/guests.html', context)