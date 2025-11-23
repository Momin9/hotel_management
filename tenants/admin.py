from django.contrib import admin
from .models import SubscriptionPlan

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_monthly_formatted', 'max_rooms', 'max_managers', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    
    def price_monthly_formatted(self, obj):
        return f"${obj.price_monthly}"
    price_monthly_formatted.short_description = 'Monthly Price'