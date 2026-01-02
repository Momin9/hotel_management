from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    ExpenseCategory, HotelExpense, EmployeeExpense, 
    PayrollRecord, InternationalTransaction, FinancialAlert
)
from billing.models import Invoice, Payment
from pos.models import POSOrder
from reservations.models import Reservation

@login_required
def finance_dashboard(request):
    """Comprehensive financial dashboard for accountants"""
    if request.user.role != 'Accountant':
        return redirect('accounts:dashboard')
    
    today = date.today()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=today.weekday())
    
    # Revenue Statistics
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount'))['total'] or Decimal('0')
    
    today_revenue = Payment.objects.filter(
        status='completed', timestamp__date=today
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    week_revenue = Payment.objects.filter(
        status='completed', timestamp__date__gte=week_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    month_revenue = Payment.objects.filter(
        status='completed', timestamp__date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Expense Statistics
    total_expenses = HotelExpense.objects.filter(status='PAID').aggregate(
        total=Sum('amount'))['total'] or Decimal('0')
    
    month_expenses = HotelExpense.objects.filter(
        status='PAID', expense_date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    pending_expenses = HotelExpense.objects.filter(status='PENDING').aggregate(
        total=Sum('amount'))['total'] or Decimal('0')
    
    # Employee Expenses
    pending_employee_expenses = EmployeeExpense.objects.filter(
        status='PENDING'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Payroll Statistics
    month_payroll = PayrollRecord.objects.filter(
        pay_period_start__gte=month_start, status='PAID'
    ).aggregate(total=Sum('net_salary'))['total'] or Decimal('0')
    
    pending_payroll = PayrollRecord.objects.filter(
        status='PROCESSED'
    ).count()
    
    # Invoice Statistics
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(status='paid').count()
    pending_invoices = Invoice.objects.filter(status__in=['draft', 'sent', 'pending']).count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
    
    # POS Statistics
    pos_today = POSOrder.objects.filter(
        order_time__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    pos_month = POSOrder.objects.filter(
        order_time__date__gte=month_start
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    # Financial Alerts
    critical_alerts = FinancialAlert.objects.filter(
        assigned_to=request.user, is_resolved=False, priority='CRITICAL'
    ).count()
    
    high_alerts = FinancialAlert.objects.filter(
        assigned_to=request.user, is_resolved=False, priority='HIGH'
    ).count()
    
    # Expense Categories Breakdown
    expense_categories = HotelExpense.objects.filter(
        expense_date__gte=month_start, status='PAID'
    ).values('category__name', 'category__category_type').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    # Recent Transactions
    recent_payments = Payment.objects.filter(
        status='completed'
    ).order_by('-timestamp')[:10]
    
    recent_expenses = HotelExpense.objects.filter(
        status='PAID'
    ).order_by('-expense_date')[:10]
    
    # Upcoming Payments
    upcoming_expenses = HotelExpense.objects.filter(
        status='APPROVED'
    ).order_by('expense_date')[:10]
    
    # Net Profit Calculation
    net_profit = month_revenue - month_expenses - month_payroll
    
    # Cash Position (simplified)
    cash_balance = total_revenue - total_expenses
    
    context = {
        # Revenue
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        
        # Expenses
        'total_expenses': total_expenses,
        'month_expenses': month_expenses,
        'pending_expenses': pending_expenses,
        'pending_employee_expenses': pending_employee_expenses,
        
        # Payroll
        'month_payroll': month_payroll,
        'pending_payroll': pending_payroll,
        
        # Invoices
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'pending_invoices': pending_invoices,
        'overdue_invoices': overdue_invoices,
        
        # POS
        'pos_today': pos_today,
        'pos_month': pos_month,
        
        # Financial Health
        'net_profit': net_profit,
        'cash_balance': cash_balance,
        
        # Alerts
        'critical_alerts': critical_alerts,
        'high_alerts': high_alerts,
        
        # Breakdowns
        'expense_categories': expense_categories,
        'recent_payments': recent_payments,
        'recent_expenses': recent_expenses,
        'upcoming_expenses': upcoming_expenses,
    }
    
    return render(request, 'finance/dashboard.html', context)

@login_required
def expense_management(request):
    """Hotel expense management"""
    if request.user.role != 'Accountant':
        return redirect('accounts:dashboard')
    
    expenses = HotelExpense.objects.all().order_by('-expense_date')
    categories = ExpenseCategory.objects.filter(is_active=True)
    
    context = {
        'expenses': expenses,
        'categories': categories,
    }
    
    return render(request, 'finance/expenses.html', context)

@login_required
def employee_expenses(request):
    """Employee expense management"""
    if request.user.role != 'Accountant':
        return redirect('accounts:dashboard')
    
    expenses = EmployeeExpense.objects.all().order_by('-expense_date')
    
    context = {
        'expenses': expenses,
    }
    
    return render(request, 'finance/employee_expenses.html', context)

@login_required
def payroll_management(request):
    """Payroll management"""
    if request.user.role != 'Accountant':
        return redirect('accounts:dashboard')
    
    payroll_records = PayrollRecord.objects.all().order_by('-pay_period_start')
    
    context = {
        'payroll_records': payroll_records,
    }
    
    return render(request, 'finance/payroll.html', context)

@login_required
def international_transactions(request):
    """International transaction management"""
    if request.user.role != 'Accountant':
        return redirect('accounts:dashboard')
    
    transactions = InternationalTransaction.objects.all().order_by('-transaction_date')
    
    context = {
        'transactions': transactions,
    }
    
    return render(request, 'finance/international.html', context)

@login_required
def financial_reports(request):
    """Financial reports dashboard"""
    if request.user.role != 'Accountant':
        return redirect('accounts:dashboard')
    
    today = date.today()
    month_start = today.replace(day=1)
    
    # P&L Data
    revenue = Payment.objects.filter(
        status='completed', timestamp__date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    expenses = HotelExpense.objects.filter(
        status='PAID', expense_date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    payroll = PayrollRecord.objects.filter(
        pay_period_start__gte=month_start, status='PAID'
    ).aggregate(total=Sum('net_salary'))['total'] or Decimal('0')
    
    net_income = revenue - expenses - payroll
    
    context = {
        'revenue': revenue,
        'expenses': expenses,
        'payroll': payroll,
        'net_income': net_income,
    }
    
    return render(request, 'finance/reports.html', context)