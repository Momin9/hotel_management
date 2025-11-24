from django.contrib import admin
from django.utils.html import format_html
from .models import InventoryCategory, InventoryItem, StockMovement

@admin.register(InventoryCategory)
class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'item_count', 'is_active']
    search_fields = ['name', 'description']
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'current_stock', 'stock_status', 'cost_price_formatted']
    list_filter = ['category', 'primary_supplier']
    search_fields = ['name', 'sku', 'supplier']
    list_editable = ['current_stock']
    
    def cost_price_formatted(self, obj):
        return f"${obj.cost_price}"
    cost_price_formatted.short_description = 'Cost Price'
    
    def stock_status(self, obj):
        if obj.current_stock <= obj.reorder_level:
            return format_html('<span style="color: red;">Low Stock</span>')
        elif obj.current_stock <= obj.reorder_level * 2:
            return format_html('<span style="color: orange;">Medium Stock</span>')
        return format_html('<span style="color: green;">Good Stock</span>')
    stock_status.short_description = 'Stock Status'

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'movement_type', 'quantity_change', 'created_by_name', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['item__name', 'created_by__username', 'notes']
    readonly_fields = ['created_at']
    
    def item_name(self, obj):
        return obj.item.name
    item_name.short_description = 'Item'
    
    def created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.username
    created_by_name.short_description = 'Created By'
    
    def quantity_change(self, obj):
        color = 'green' if obj.quantity > 0 else 'red'
        sign = '+' if obj.quantity > 0 else ''
        return format_html(
            '<span style="color: {};">{}{}</span>',
            color, sign, obj.quantity
        )
    quantity_change.short_description = 'Change'