from django.contrib import admin
from django.utils.html import format_html
from .models import GuestFolio, FolioCharge, CheckInOut

@admin.register(GuestFolio)
class GuestFolioAdmin(admin.ModelAdmin):
    list_display = ['folio_number', 'guest_name', 'balance_formatted', 'is_settled', 'created_at']
    list_filter = ['is_settled', 'created_at']
    search_fields = ['folio_number', 'guest__first_name', 'guest__last_name']
    readonly_fields = ['folio_number', 'created_at', 'updated_at']
    
    def guest_name(self, obj):
        return obj.guest.full_name if obj.guest else "No Guest"
    guest_name.short_description = 'Guest'
    
    def room_number(self, obj):
        return obj.room.room_number if obj.room else "No Room"
    room_number.short_description = 'Room'
    
    def balance_formatted(self, obj):
        return f"${obj.balance}"
    balance_formatted.short_description = 'Balance'
    
    def status_badge(self, obj):
        colors = {'open': '#10B981', 'closed': '#6B7280', 'transferred': '#3B82F6'}
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

@admin.register(FolioCharge)
class FolioChargeAdmin(admin.ModelAdmin):
    list_display = ['folio', 'charge_type', 'amount_formatted', 'description', 'charge_date']
    list_filter = ['charge_type', 'charge_date']
    search_fields = ['folio__folio_number', 'description']
    
    def amount_formatted(self, obj):
        return f"${obj.amount}"
    amount_formatted.short_description = 'Amount'

@admin.register(CheckInOut)
class CheckInOutAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'room_number', 'checked_in_at', 'checked_out_at', 'status']
    list_filter = ['status', 'checked_in_at', 'checked_out_at']
    search_fields = ['guest__first_name', 'guest__last_name', 'room__room_number']
    
    def guest_name(self, obj):
        return obj.guest.full_name if obj.guest else "No Guest"
    guest_name.short_description = 'Guest'
    
    def room_number(self, obj):
        return obj.room.room_number if obj.room else "No Room"
    room_number.short_description = 'Room'