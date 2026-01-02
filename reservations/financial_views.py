from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from decimal import Decimal

from reservations.models import Reservation
from billing.models import Invoice, Payment
from pos.models import POSOrder, POSPayment
from hotels.models import Hotel

@login_required
def financial_data_view(request):
    """Financial data view for accountants - reservation and billing data only"""
    
    # Only allow accountants to access this view
    if request.user.role != 'Accountant':
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, "You don't have permission to view this page.")
        return redirect('accounts:dashboard')
    
    today = date.today()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    
    # Get reservations with financial data only (no guest personal info)
    reservations = Reservation.objects.all().select_related('hotel', 'room').order_by('-created_at')[:20]
    
    # Financial statistics
    today_revenue = Reservation.objects.filter(
        created_at__date=today,
        status__in=['confirmed', 'checked_in', 'checked_out']
    ).aggregate(total=Sum('rate'))['total'] or 0
    
    week_revenue = Reservation.objects.filter(
        created_at__date__gte=week_start,
        status__in=['confirmed', 'checked_in', 'checked_out']
    ).aggregate(total=Sum('rate'))['total'] or 0
    
    month_revenue = Reservation.objects.filter(
        created_at__date__gte=month_start,
        status__in=['confirmed', 'checked_in', 'checked_out']
    ).aggregate(total=Sum('rate'))['total'] or 0
    
    # Reservation counts
    today_reservations = Reservation.objects.filter(created_at__date=today).count()
    pending_reservations = Reservation.objects.filter(status='pending').count()
    confirmed_reservations = Reservation.objects.filter(status='confirmed').count()
    
    # Payment statistics - using timestamp field
    today_payments = Payment.objects.filter(timestamp__date=today).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    week_payments = Payment.objects.filter(timestamp__date__gte=week_start).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    month_payments = Payment.objects.filter(
        timestamp__year=today.year,
        timestamp__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Payment method breakdown
    payment_methods = Payment.objects.filter(
        timestamp__date__gte=month_start
    ).values('method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Recent invoices
    recent_invoices = Invoice.objects.all().order_by('-created_at')[:10]
    
    # Revenue by status
    revenue_by_status = Reservation.objects.filter(
        created_at__date__gte=month_start
    ).values('status').annotate(
        total_revenue=Sum('rate'),
        count=Count('id')
    ).order_by('-total_revenue')
    
    # Invoice statistics
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(status='paid').count()
    pending_invoices = Invoice.objects.filter(status__in=['draft', 'sent']).count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    
    context = {
        'reservations': reservations,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'today_reservations': today_reservations,
        'pending_reservations': pending_reservations,
        'confirmed_reservations': confirmed_reservations,
        'today_payments': today_payments,
        'week_payments': week_payments,
        'month_payments': month_payments,
        'payment_methods': payment_methods,
        'recent_invoices': recent_invoices,
        'revenue_by_status': revenue_by_status,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
    }
    
    return render(request, 'reservations/financial_data.html', context)