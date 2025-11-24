from django.contrib import admin
from django.utils.html import format_html
from .models import Reservation, Stay

class StayInline(admin.StackedInline):
    model = Stay
    extra = 0
    readonly_fields = ['actual_check_in', 'actual_check_out']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'property_name', 'check_in', 'check_out', 'status', 'rate']
    list_filter = ['status', 'check_in', 'check_out', 'created_at']
    search_fields = ['confirmation_number', 'guest__first_name', 'guest__last_name', 'guest__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [StayInline]
    
    def guest_name(self, obj):
        return obj.guest.full_name if obj.guest else "No Guest"
    guest_name.short_description = 'Guest'
    
    def property_name(self, obj):
        return obj.hotel_property.name if obj.hotel_property else "No Property"
    property_name.short_description = 'Property'
    
