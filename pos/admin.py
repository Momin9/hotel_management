from django.contrib import admin
from django.utils.html import format_html
from .models import POSCategory, POSItem, POSOrder, POSOrderItem, POSPayment, POSShift

class POSItemInline(admin.TabularInline):
    model = POSItem
    extra = 1
    fields = ['name', 'price', 'is_available']

@admin.register(POSCategory)
class POSCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'item_count', 'is_active_badge', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    inlines = [POSItemInline]
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_badge.short_description = 'Status'

@admin.register(POSItem)
class POSItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_formatted', 'cost_formatted', 'profit_margin', 'stock_status', 'is_available']
    list_filter = ['category', 'is_available', 'track_inventory', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    list_editable = ['is_available']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'cost')
        }),
        ('Inventory', {
            'fields': ('track_inventory', 'stock_quantity', 'low_stock_threshold')
        }),
        ('Status', {
            'fields': ('is_available', 'is_active')
        })
    )
    
    def price_formatted(self, obj):
        return f"${obj.price}"
    price_formatted.short_description = 'Price'
    
    def cost_formatted(self, obj):
        return f"${obj.cost}"
    cost_formatted.short_description = 'Cost'
    
    def profit_margin(self, obj):
        if obj.cost > 0:
            margin = ((obj.price - obj.cost) / obj.price) * 100
            return f"{margin:.1f}%"
        return "N/A"
    profit_margin.short_description = 'Profit %'
    
    def stock_status(self, obj):
        if not obj.track_inventory:
            return "Not tracked"
        if obj.is_low_stock:
            return format_html('<span style="color: red;">Low Stock ({})</span>', obj.stock_quantity)
        return f"In Stock ({obj.stock_quantity})"
    stock_status.short_description = 'Stock'
    
    def is_available_badge(self, obj):
        if obj.is_available:
            return format_html('<span style="color: green;">✓ Available</span>')
        return format_html('<span style="color: red;">✗ Unavailable</span>')
    is_available_badge.short_description = 'Available'

class POSOrderItemInline(admin.TabularInline):
    model = POSOrderItem
    extra = 0
    readonly_fields = ['total_price']

class POSPaymentInline(admin.TabularInline):
    model = POSPayment
    extra = 0
    readonly_fields = ['processed_at']

@admin.register(POSOrder)
class POSOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'order_type', 'customer_info', 'total_amount_formatted', 'status_badge', 'payment_status_badge', 'order_time']
    list_filter = ['order_type', 'status', 'payment_status', 'order_time']
    search_fields = ['order_number', 'customer_name', 'guest__first_name', 'guest__last_name']
    readonly_fields = ['order_number', 'subtotal', 'tax_amount', 'service_charge', 'total_amount', 'order_time']
    inlines = [POSOrderItemInline, POSPaymentInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'order_type', 'status', 'payment_status')
        }),
        ('Customer Details', {
            'fields': ('guest', 'customer_name', 'room_number', 'table_number')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'service_charge', 'discount_amount', 'total_amount')
        }),
        ('Staff & Timing', {
            'fields': ('created_by', 'served_by', 'order_time', 'confirmed_at', 'served_at')
        }),
        ('Special Instructions', {
            'fields': ('special_instructions',)
        })
    )
    
    def customer_info(self, obj):
        if obj.guest:
            return f"{obj.guest.full_name} (Guest)"
        return obj.customer_name or "Walk-in"
    customer_info.short_description = 'Customer'
    
    def total_amount_formatted(self, obj):
        return f"${obj.total_amount}"
    total_amount_formatted.short_description = 'Total'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#F59E0B',
            'confirmed': '#3B82F6',
            'preparing': '#8B5CF6',
            'ready': '#10B981',
            'served': '#059669',
            'cancelled': '#EF4444'
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        colors = {
            'unpaid': '#EF4444',
            'paid': '#10B981',
            'charged_to_room': '#3B82F6'
        }
        color = colors.get(obj.payment_status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment'

@admin.register(POSPayment)
class POSPaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'amount_formatted', 'processed_by', 'processed_at']
    list_filter = ['payment_method', 'processed_at']
    search_fields = ['order__order_number', 'reference_number']
    
    def amount_formatted(self, obj):
        return f"${obj.amount}"
    amount_formatted.short_description = 'Amount'

@admin.register(POSShift)
class POSShiftAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'hotel', 'shift_date', 'total_sales_formatted', 'orders_count', 'is_closed_badge']
    list_filter = ['is_closed', 'shift_date', 'hotel']
    search_fields = ['staff_member__username', 'hotel__name']
    
    def total_sales_formatted(self, obj):
        return f"${obj.total_sales}"
    total_sales_formatted.short_description = 'Total Sales'
    
    def is_closed_badge(self, obj):
        if obj.is_closed:
            return format_html('<span style="color: green;">✓ Closed</span>')
        return format_html('<span style="color: orange;">⏳ Open</span>')
    is_closed_badge.short_description = 'Status'