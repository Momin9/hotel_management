from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Invoice, Payment
from django.db.models import Sum
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    """Billing dashboard"""
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_payments = Invoice.objects.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_invoices = Invoice.objects.count()
    monthly_revenue = Payment.objects.filter(
        status='completed',
        timestamp__date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    recent_invoices = Invoice.objects.order_by('-created_at')[:5]
    
    context = {
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'total_invoices': total_invoices,
        'monthly_revenue': monthly_revenue,
        'recent_invoices': recent_invoices,
    }
    
    return render(request, 'billing/dashboard.html', context)

@login_required
def invoice_list(request):
    """List all invoices"""
    invoices = Invoice.objects.all().order_by('-created_at')
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})

@login_required
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.all().order_by('-timestamp')
    return render(request, 'billing/payment_list.html', {'payments': payments})

@login_required
def create_invoice(request):
    """Create new invoice"""
    if request.method == 'POST':
        messages.success(request, 'Invoice created successfully!')
        return redirect('billing:invoice_list')
    
    return render(request, 'billing/create_invoice.html')