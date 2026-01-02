from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, F, Count
from django.db import models
from .models import InventoryItem, StockMovement, PurchaseOrder, Supplier, StockTake, InventoryCategory

@login_required
def inventory_dashboard(request):
    """Inventory main dashboard"""
    # Total items count
    total_items = InventoryItem.objects.filter(is_active=True).count()
    
    # Low stock items count
    low_stock_count = InventoryItem.objects.filter(
        current_stock__lte=models.F('minimum_stock'),
        is_active=True
    ).count()
    
    # Total categories count
    total_categories = InventoryCategory.objects.filter(is_active=True).count()
    
    # Recent stock movements
    recent_movements = StockMovement.objects.all().order_by('-created_at')[:10]
    
    # Pending purchase orders
    pending_pos = PurchaseOrder.objects.filter(status__in=['draft', 'sent', 'confirmed'])
    
    # Total inventory value
    total_value = InventoryItem.objects.aggregate(
        total=Sum(models.F('current_stock') * models.F('cost_price'))
    )['total'] or 0
    
    # Low stock items for display
    low_stock_items = InventoryItem.objects.filter(
        current_stock__lte=models.F('minimum_stock'),
        is_active=True
    )[:5]
    
    context = {
        'total_items': total_items,
        'low_stock_items': low_stock_count,
        'total_categories': total_categories,
        'total_value': total_value,
        'low_stock_items_list': low_stock_items,
        'recent_movements': recent_movements,
        'pending_pos': pending_pos,
        'recent_activities': recent_movements[:5],  # Use recent movements as activities
    }
    
    return render(request, 'inventory/dashboard.html', context)

@login_required
def item_list(request):
    """List all inventory items"""
    items = InventoryItem.objects.filter(is_active=True)
    return render(request, 'inventory/item_list.html', {'items': items})

@login_required
def create_item(request):
    """Create new inventory item"""
    if request.method == 'POST':
        # Handle item creation logic
        pass
    
    return render(request, 'inventory/create_item.html')

@login_required
def item_detail(request, item_id):
    """Item detail view"""
    item = get_object_or_404(InventoryItem, id=item_id)
    movements = item.movements.all().order_by('-created_at')
    
    context = {
        'item': item,
        'movements': movements,
    }
    
    return render(request, 'inventory/item_detail.html', context)

@login_required
def stock_movements(request):
    """Stock movements list"""
    movements = StockMovement.objects.all().order_by('-created_at')
    return render(request, 'inventory/stock_movements.html', {'movements': movements})

@login_required
def purchase_orders(request):
    """Purchase orders list"""
    orders = PurchaseOrder.objects.all().order_by('-created_at')
    return render(request, 'inventory/purchase_orders.html', {'orders': orders})

@login_required
def supplier_list(request):
    """Suppliers list"""
    suppliers = Supplier.objects.filter(is_active=True)
    return render(request, 'inventory/suppliers.html', {'suppliers': suppliers})

@login_required
def stock_take(request):
    """Stock take management"""
    stock_takes = StockTake.objects.all().order_by('-created_at')
    return render(request, 'inventory/stock_take.html', {'stock_takes': stock_takes})