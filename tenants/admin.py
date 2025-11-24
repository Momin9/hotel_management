from django.contrib import admin
from .models import SubscriptionPlan

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_monthly_formatted', 'max_rooms', 'max_managers', 'has_advanced_analytics', 'has_priority_support', 'is_active']
    list_filter = ['is_active', 'has_advanced_analytics', 'has_priority_support']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price_monthly', 'price_yearly')
        }),
        ('Limits', {
            'fields': ('max_rooms', 'max_managers')
        }),
        ('Features', {
            'fields': ('has_advanced_analytics', 'has_priority_support')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )
    
    def price_monthly_formatted(self, obj):
        return f"${obj.price_monthly}"
    price_monthly_formatted.short_description = 'Monthly Price'