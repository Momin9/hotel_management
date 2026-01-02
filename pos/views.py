from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from .models import POSOrder, POSItem, POSCategory, POSShift

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from .models import POSOrder, POSItem, POSCategory, POSShift, POSPayment

@login_required
def pos_dashboard(request):
    """POS main dashboard with financial data for accountants"""
    today = timezone.now().date()
    
    # Today's statistics
    today_orders = POSOrder.objects.filter(order_time__date=today)
    today_sales = today_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    today_orders_count = today_orders.count()
    
    # This week's statistics
    week_start = today - timedelta(days=today.weekday())
    week_orders = POSOrder.objects.filter(order_time__date__gte=week_start)
    week_sales = week_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # This month's statistics
    month_start = today.replace(day=1)
    month_orders = POSOrder.objects.filter(order_time__date__gte=month_start)
    month_sales = month_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Payment method breakdown (today)
    payment_breakdown = POSPayment.objects.filter(
        order__order_time__date=today
    ).values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Recent orders
    recent_orders = POSOrder.objects.all().order_by('-order_time')[:10]
    
    # Top selling items (this month)
    top_items = POSOrder.objects.filter(
        order_time__date__gte=month_start
    ).values(
        'items__item__name'
    ).annotate(
        total_quantity=Sum('items__quantity'),
        total_revenue=Sum('items__total_price')
    ).order_by('-total_revenue')[:5]
    
    # Order status breakdown (today)
    status_breakdown = today_orders.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Average order value
    avg_order_value = today_sales / today_orders_count if today_orders_count > 0 else 0
    
    context = {
        'today_sales': today_sales,
        'today_orders_count': today_orders_count,
        'week_sales': week_sales,
        'month_sales': month_sales,
        'avg_order_value': avg_order_value,
        'payment_breakdown': payment_breakdown,
        'recent_orders': recent_orders,
        'top_items': top_items,
        'status_breakdown': status_breakdown,
    }
    
    return render(request, 'pos/dashboard.html', context)

@login_required
def order_list(request):
    """List all orders"""
    orders = POSOrder.objects.all().order_by('-order_time')
    return render(request, 'pos/order_list.html', {'orders': orders})

@login_required
def create_order(request):
    """Create new POS order"""
    if request.method == 'POST':
        # Handle order creation logic
        pass
    
    categories = POSCategory.objects.filter(is_active=True)
    items = POSItem.objects.filter(is_active=True, is_available=True)
    
    context = {
        'categories': categories,
        'items': items,
    }
    
    return render(request, 'pos/create_order.html', context)

@login_required
def order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(POSOrder, id=order_id)
    return render(request, 'pos/order_detail.html', {'order': order})

@login_required
def menu_management(request):
    """Manage POS menu items"""
    try:
        items = POSItem.objects.all()
        categories = POSCategory.objects.all()
    except Exception as e:
        # Handle case where tables don't exist yet
        items = []
        categories = []
        messages.warning(request, 'POS system is being set up. Please contact administrator.')
    
    context = {
        'items': items,
        'categories': categories,
    }
    
    return render(request, 'pos/menu.html', context)

@login_required
def add_menu_item(request):
    """Add new menu item"""
    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = get_object_or_404(POSCategory, id=category_id)
        
        item = POSItem.objects.create(
            category=category,
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            price=request.POST.get('price'),
            cost=request.POST.get('cost', 0),
            track_inventory=request.POST.get('track_inventory') == 'on',
            stock_quantity=request.POST.get('stock_quantity', 0),
            low_stock_threshold=request.POST.get('low_stock_threshold', 5)
        )
        
        messages.success(request, f'Menu item "{item.name}" added successfully!')
        return redirect('pos:menu')
    
    categories = POSCategory.objects.filter(is_active=True)
    return render(request, 'pos/add_item.html', {'categories': categories})

@login_required
def add_category(request):
    """Add new category"""
    if request.method == 'POST':
        category = POSCategory.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description', '')
        )
        
        messages.success(request, f'Category "{category.name}" added successfully!')
        return redirect('pos:menu')
    
    return render(request, 'pos/add_category.html')

@login_required
def shift_management(request):
    """Manage POS shifts"""
    shifts = POSShift.objects.filter(staff_member=request.user).order_by('-shift_date')
    return render(request, 'pos/shift.html', {'shifts': shifts})